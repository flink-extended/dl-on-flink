# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import threading
import time
from datetime import timedelta
from typing import List, Optional, Set

import airflow.utils.dag_processing as dag_processing
from airflow.configuration import conf
from airflow.contrib.jobs.background_service import BackgroundService
from airflow.events.scheduler_events import DagExecutableEvent
from airflow.jobs import scheduler_job
from airflow.models import DagModel
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.mailbox import Mailbox
from airflow.utils.mixins import MultiprocessingStartMethodMixin
from airflow.utils.session import create_session


class DagTriggerDagFileProcessorAgent(dag_processing.DagFileProcessorAgent):
    def wait_on_manager_message(self, timeout=None):
        self._parent_signal_conn.poll(timeout)


class StoppableThread(threading.Thread, LoggingMixin):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._ended = threading.Event()

    def stop(self):
        self.log.debug("stopping thread")
        self._ended.set()

    def stopped(self):
        return self._ended.is_set()


class DagRunnableReportingThread(StoppableThread, LoggingMixin):

    def __init__(self, async_mode: bool, dag_file_processor_agent, mailbox: Mailbox, *args, **kwargs):
        super(DagRunnableReportingThread, self).__init__(*args, **kwargs)
        self.setName("DagTrigger-DagRunnableReporter")
        self._async_mode = async_mode
        self._dag_file_processor_agent: DagTriggerDagFileProcessorAgent = dag_file_processor_agent
        self._mailbox = mailbox

    def run(self) -> None:
        while not self.stopped():
            # send AGENT_RUN_ONCE to DagFileProcessorManager to trigger dag parsing if not async mode
            if not self._async_mode:
                self._dag_file_processor_agent.run_single_parsing_loop()
            with create_session() as session:
                dag_models = DagModel.dags_needing_dagruns(session).all()
                self.log.debug("dags needs dagruns: {}".format(dag_models))
                self._send_dag_executable(dag_models)
            time.sleep(5)
        self.log.info("DagRunnableReporter exiting")

    def _send_dag_executable(self, dag_models: Set[DagModel]):
        for dag_model in dag_models:
            self._mailbox.send_message(DagExecutableEvent(dag_model.dag_id, dag_model.next_dagrun).to_event())


class ParsingStatRetrieveThread(StoppableThread):
    def __init__(self, dag_file_processor_agent, *args, **kwargs):
        super(ParsingStatRetrieveThread, self).__init__(*args, **kwargs)
        self.setName("DagTrigger-ParsingStatRetriever")
        self._dag_file_processor_agent: DagTriggerDagFileProcessorAgent = dag_file_processor_agent

    def run(self) -> None:
        while not self.stopped():
            self._dag_file_processor_agent.wait_on_manager_message()
            self._dag_file_processor_agent.heartbeat()
            time.sleep(10)
        self.log.info("ParsingStatRetriever exiting")


class DagTrigger(BackgroundService, MultiprocessingStartMethodMixin):

    def __init__(self,
                 dag_directory: str,
                 max_runs: int,
                 dag_ids: Optional[List[str]],
                 pickle_dags: bool,
                 mailbox: Mailbox,
                 refresh_dag_dir_interval=1,
                 notification_service_uri=None):
        """
        :param dag_directory: Directory where DAG definitions are kept. All
        files in file_paths should be under this directory
        :type dag_directory: unicode
        :param max_runs: The number of times to parse and schedule each file. -1
            for unlimited.
        :type max_runs: int
        :param dag_ids: if specified, only schedule tasks with these DAG IDs
        :type dag_ids: list[str]
        :param pickle_dags: whether to pickle DAGs.
        :type pickle_dags: bool
        :param mailbox: the mailbox to send the DagExecutableEvent
        :type mailbox: Mailbox
        """

        super().__init__()

        self._dag_directory = dag_directory
        self._max_runs = max_runs
        self._dag_ids = dag_ids
        self._pickle_dags = pickle_dags
        self._mailbox = mailbox
        # use synchronize mode when using sqlite
        self._async_mode = not conf.get('core', 'sql_alchemy_conn').lower().startswith('sqlite')

        self._dag_runnable_reporting_thread: Optional[StoppableThread] = None
        self._parsing_stat_process_thread: Optional[StoppableThread] = None
        self._dag_file_processor_agent: Optional[DagTriggerDagFileProcessorAgent] = None
        self._refresh_dag_dir_interval = refresh_dag_dir_interval
        self._notification_service_uri = notification_service_uri

    def start(self):
        self._start_dag_file_processor_manager()
        self._dag_runnable_reporting_thread = DagRunnableReportingThread(self._async_mode,
                                                                         self._dag_file_processor_agent,
                                                                         self._mailbox)
        self._dag_runnable_reporting_thread.start()

        self._parsing_stat_process_thread = ParsingStatRetrieveThread(self._dag_file_processor_agent)
        self._parsing_stat_process_thread.start()

    def end(self) -> None:
        if self._dag_file_processor_agent is not None:
            self._dag_file_processor_agent.terminate()
        if self._dag_runnable_reporting_thread is not None:
            self._dag_runnable_reporting_thread.stop()
        if self._parsing_stat_process_thread is not None:
            self._parsing_stat_process_thread.stop()
        self._dag_runnable_reporting_thread.join()
        self._parsing_stat_process_thread.join()
        self._dag_file_processor_agent.end()

    def terminate(self):
        if self._dag_file_processor_agent is not None:
            self._dag_file_processor_agent.end()
        if self._dag_runnable_reporting_thread is not None:
            self._dag_runnable_reporting_thread.stop()
        if self._parsing_stat_process_thread is not None:
            self._parsing_stat_process_thread.stop()

    def _start_dag_file_processor_manager(self):
        processor_factory = scheduler_job.SchedulerJob._create_dag_file_processor

        self._dag_file_processor_agent = DagTriggerDagFileProcessorAgent(self._dag_directory,
                                                                         self._max_runs,
                                                                         processor_factory,
                                                                         self._get_processor_timeout(),
                                                                         [],
                                                                         self._pickle_dags,
                                                                         self._async_mode,
                                                                         self._refresh_dag_dir_interval,
                                                                         self._notification_service_uri)
        self._dag_file_processor_agent.start()

    @staticmethod
    def _get_processor_timeout():
        processor_timeout_seconds: int = conf.getint('core', 'dag_file_processor_timeout')
        return timedelta(seconds=processor_timeout_seconds)

    def is_alive(self) -> bool:
        return self._dag_file_processor_agent is not None \
               and self._dag_runnable_reporting_thread is not None and self._dag_runnable_reporting_thread.is_alive() \
               and self._parsing_stat_process_thread is not None and self._parsing_stat_process_thread.is_alive()
