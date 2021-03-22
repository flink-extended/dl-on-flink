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

import multiprocessing
import threading
import time
from datetime import timedelta
from multiprocessing.process import BaseProcess
from typing import List, Optional, Set

from airflow.utils.log.logging_mixin import LoggingMixin

import airflow.utils.dag_processing as dag_processing
from airflow.configuration import conf
from airflow.contrib.jobs.background_service import BackgroundService
from airflow.events.scheduler_events import DagExecutableEvent
from airflow.jobs import scheduler_job
from airflow.models import DagModel
from airflow.utils.mailbox import Mailbox
from airflow.utils.mixins import MultiprocessingStartMethodMixin
from airflow.utils.session import create_session


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

    def __init__(self, async_mode: bool, parent_conn, mailbox: Mailbox, *args, **kwargs):
        super(DagRunnableReportingThread, self).__init__(*args, **kwargs)
        self.setName("DagTrigger-DagRunnableReporter")
        self._async_mode = async_mode
        self._parent_conn = parent_conn
        self._mailbox = mailbox

    def run(self) -> None:
        while not self.stopped():
            # send AGENT_RUN_ONCE to DagFileProcessorManager to trigger dag parsing if not async mode
            if not self._async_mode:
                self._parent_conn.send(dag_processing.DagParsingSignal.AGENT_RUN_ONCE)
            with create_session() as session:
                dag_models = DagModel.dags_needing_dagruns(session).all()
                self.log.debug("dags needs dagruns: {}".format(dag_models))
                self._send_dag_executable(dag_models)
            time.sleep(1)
        self.log.info("DagRunnableReporter exiting")

    def _send_dag_executable(self, dag_models: Set[DagModel]):
        for dag_model in dag_models:
            self._mailbox.send_message(DagExecutableEvent(dag_model.dag_id).to_event())


class ParsingStatRetrieveThread(StoppableThread):
    def __init__(self, parent_conn, *args, **kwargs):
        super(ParsingStatRetrieveThread, self).__init__(*args, **kwargs)
        self.setName("DagTrigger-ParsingStatRetriever")
        self._parent_conn = parent_conn

    def run(self) -> None:
        while not self.stopped() and self._parent_conn.poll(None):
            try:
                message = self._parent_conn.recv()
                self.log.debug("receiving parsing stat from dag file processor manager: {}".format(message))
            except EOFError as _:
                # log and ignore
                self.log.warning("nothing left to receive from DagFileProcessorManager")
                time.sleep(10)
        self.log.info("ParsingStatRetriever exiting")


class DagTrigger(BackgroundService, MultiprocessingStartMethodMixin):

    def __init__(self,
                 dag_directory: str,
                 max_runs: int,
                 dag_ids: Optional[List[str]],
                 pickle_dags: bool,
                 mailbox: Mailbox,
                 refresh_dag_dir_interval=1):
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
        self._manager_process: Optional[BaseProcess] = None
        self._parent_conn = None
        self._refresh_dag_dir_interval = refresh_dag_dir_interval

    def start(self):
        self._start_dag_file_processor_manager()
        self._dag_runnable_reporting_thread = DagRunnableReportingThread(self._async_mode, self._parent_conn,
                                                                         self._mailbox)
        self._dag_runnable_reporting_thread.start()

        self._parsing_stat_process_thread = ParsingStatRetrieveThread(self._parent_conn)
        self._parsing_stat_process_thread.start()

    def end(self) -> None:
        if self._manager_process is not None:
            self._manager_process.terminate()
        if self._dag_runnable_reporting_thread is not None:
            self._dag_runnable_reporting_thread.stop()
        if self._parsing_stat_process_thread is not None:
            self._parsing_stat_process_thread.stop()
        self._manager_process.join()
        self._dag_runnable_reporting_thread.join()
        self._parsing_stat_process_thread.join()

    def terminate(self):
        if self._manager_process is not None:
            self._manager_process.kill()
        if self._dag_runnable_reporting_thread is not None:
            self._dag_runnable_reporting_thread.stop()
        if self._parsing_stat_process_thread is not None:
            self._parsing_stat_process_thread.stop()

    def _start_dag_file_processor_manager(self):
        context = multiprocessing.get_context(super()._get_multiprocessing_start_method())
        self._parent_conn, child_conn = context.Pipe(duplex=True)
        self._manager_process = context.Process(target=dag_processing.DagFileProcessorAgent._run_processor_manager,
                                                args=(
                                                    self._dag_directory,
                                                    self._max_runs,
                                                    scheduler_job.SchedulerJob._create_dag_file_processor,
                                                    self._get_processor_timeout(),
                                                    child_conn,
                                                    self._dag_ids,
                                                    self._pickle_dags,
                                                    self._async_mode,
                                                    self._refresh_dag_dir_interval
                                                ))
        self._manager_process.start()

    @staticmethod
    def _get_processor_timeout():
        processor_timeout_seconds: int = conf.getint('core', 'dag_file_processor_timeout')
        return timedelta(seconds=processor_timeout_seconds)

    def is_alive(self) -> bool:
        return self._manager_process is not None and self._manager_process.is_alive() \
               and self._dag_runnable_reporting_thread is not None and self._dag_runnable_reporting_thread.is_alive() \
               and self._parsing_stat_process_thread is not None and self._parsing_stat_process_thread.is_alive()
