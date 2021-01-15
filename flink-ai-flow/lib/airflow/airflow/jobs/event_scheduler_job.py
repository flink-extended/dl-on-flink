# -*- coding: utf-8 -*-
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

import json
from typing import List
import multiprocessing as mp
from notification_service.service import NotificationService
from airflow.models.taskstate import TaskState, TaskAction, START_ACTION, action_is_stop_or_restart
from airflow.notification.event_model_storage import EventModelStorage
from airflow.ti_deps.dep_context import SCHEDULEABLE_STATES, DepContext, FINISHED_STATES, \
    RUNNING_STATES
from sqlalchemy.orm import make_transient
from airflow.utils.state import State
from airflow.utils.db import provide_session, create_session
from airflow.models.dagrun import DagRun
from airflow.models.dag import DAG, DagModel
from notification_service.master import NotificationMaster
from airflow.settings import Stats
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.dag_processing import (DagFileProcessorAgent,
                                          SimpleDag,
                                          list_py_file_paths, SimpleDagBag)
from airflow.configuration import conf
from airflow.jobs.scheduler_job import SchedulerJob, DagFileProcessor
from airflow import models, settings
from datetime import timedelta
from time import sleep
import time
import signal
import sys
import os
import threading
from airflow.utils import timezone
from notification_service.client import NotificationClient, EventWatcher
from airflow.models.event import DagRunEvent, Event, EventType, TaskInstanceHelper, DagRunFinishedEvent
from airflow.utils.mailbox import Mailbox
from notification_service.util.db import EventModel


class EventDagFileProcessor(DagFileProcessor):
    """
    use EventSchedulerJob process_file function to parse dag.
    """

    @classmethod
    def _create_scheduler_job(cls, dag_id_white_list, log):
        return EventSchedulerJob(dag_ids=dag_id_white_list, log=log)


class Trigger(LoggingMixin):

    def start(self):
        pass

    def stop(self):
        pass


class DagTrigger(Trigger):
    """
    process dag files and send DAG_RUN event to notification service.
    """

    def __init__(self,
                 subdir,
                 mailbox,
                 run_duration=None,
                 using_sqlite=True,
                 num_runs=conf.getint('scheduler', 'num_runs', fallback=-1),
                 processor_poll_interval=conf.getfloat(
                     'scheduler', 'processor_poll_interval', fallback=1)) -> None:
        self.mailbox = mailbox
        self.pickle_dags = True
        self.using_sqlite = using_sqlite
        self.subdir = subdir
        self.num_runs = num_runs
        self.processor_agent = None
        self.execute_start_time = None
        if run_duration is None:
            self.run_duration = conf.getint('scheduler',
                                            'run_duration')
        else:
            self.run_duration = run_duration
        self._processor_poll_interval = processor_poll_interval
        self.running = True
        self.dag_process_thread = None
        signal.signal(signal.SIGINT, self._exit_gracefully)
        signal.signal(signal.SIGTERM, self._exit_gracefully)

    def _exit_gracefully(self, signum, frame):
        """
        Helper method to clean up processor_agent to avoid leaving orphan processes.
        """
        self.log.info("Exiting gracefully upon receiving signal %s", signum)
        if self.processor_agent:
            self.processor_agent.end()
        sys.exit(os.EX_OK)

    def start(self):

        self.log.info("Running dag trigger loop for %s seconds", self.run_duration)
        self.log.info("Processing each file at most %s times", self.num_runs)

        # Build up a list of Python files that could contain DAGs
        self.log.info("Searching for files in %s", self.subdir)
        known_file_paths = list_py_file_paths(self.subdir)
        self.log.info("There are %s files in %s", len(known_file_paths), self.subdir)
        self.log.info("known files are %s.", str(known_file_paths))

        def processor_factory(file_path, zombies):
            return EventDagFileProcessor(file_path,
                                         self.pickle_dags,
                                         [],
                                         zombies)

        # When using sqlite, we do not use async_mode
        # so the scheduler job and DAG parser don't access the DB at the same time.
        async_mode = not self.using_sqlite

        processor_timeout_seconds = conf.getint('core', 'dag_file_processor_timeout')
        processor_timeout = timedelta(seconds=processor_timeout_seconds)
        self.processor_agent = DagFileProcessorAgent(self.subdir,
                                                     known_file_paths,
                                                     self.num_runs,
                                                     processor_factory,
                                                     processor_timeout,
                                                     async_mode)

        self.processor_agent.start()

        self.execute_start_time = timezone.utcnow()
        self.dag_process_thread = threading.Thread(target=self.run_parse_dags, args=())
        self.dag_process_thread.setDaemon(True)
        self.dag_process_thread.start()

    def _get_simple_dags(self):
        return self.processor_agent.harvest_simple_dags()

    def run_parse_dags(self):
        # For the execute duration, parse and schedule DAGs
        num_runs = 0
        if self.num_runs < 0:
            self.num_runs = sys.maxsize
        while self.running and num_runs < self.num_runs:
            self.log.debug("Starting Loop... num_runs: {0} max_runs {1}".format(num_runs, self.num_runs))
            loop_start_time = time.time()
            if self.using_sqlite:
                self.processor_agent.heartbeat()
                # For the sqlite case w/ 1 thread, wait until the processor
                # is finished to avoid concurrent access to the DB.
                self.log.debug(
                    "Waiting for processors to finish since we're using sqlite")
                self.processor_agent.wait_until_finished()

            self.log.debug("Harvesting DAG parsing results")
            simple_dag_runs = self._get_simple_dags()
            self.log.debug("Harvested {} SimpleDAGRuns".format(len(simple_dag_runs)))

            if 0 == len(simple_dag_runs):
                sleep(self._processor_poll_interval)
                continue
            else:
                for simple_dag_run in simple_dag_runs:
                    event = DagRunEvent(dag_run_id=simple_dag_run.dag_run_id, simple_dag=simple_dag_run.simple_dag)
                    self.mailbox.send_message(event)
                    num_runs += 1

            is_unit_test = conf.getboolean('core', 'unit_test_mode')
            loop_end_time = time.time()
            loop_duration = loop_end_time - loop_start_time
            self.log.debug(
                "Ran scheduling loop in %.2f seconds",
                loop_duration)

            if not is_unit_test:
                self.log.debug("Sleeping for %.2f seconds", self._processor_poll_interval)
                time.sleep(self._processor_poll_interval)

            if self.processor_agent.done:
                self.log.info("Exiting scheduler loop as all files"
                              " have been processed {} times".format(self.num_runs))
                break

            if loop_duration < 1 and not is_unit_test:
                sleep_length = 1 - loop_duration
                self.log.debug(
                    "Sleeping for {0:.2f} seconds to prevent excessive logging"
                        .format(sleep_length))
                sleep(sleep_length)
            if is_unit_test:
                sleep(1)

        while self.running:
            time.sleep(1)

    def stop(self):
        self.running = False
        self.dag_process_thread.join()

        # Stop any processors
        self.processor_agent.terminate()
        # Verify that all files were processed, and if so, deactivate DAGs that
        # haven't been touched by the scheduler as they likely have been
        # deleted.
        if self.processor_agent.all_files_processed:
            self.log.info(
                "Deactivating DAGs that haven't been touched since %s",
                self.execute_start_time.isoformat()
            )
            models.DAG.deactivate_stale_dags(self.execute_start_time)
        self.processor_agent.end()


class DagRunRoute(object):
    """
    DagRunRoute is a helper to find DagRuns by event message.
    """

    def __init__(self):
        self.route = {}
        self.event_route = {}
        self.dag_route = {}
        self.simple_dags = {}

    def add_dagrun(self, dagrun: DagRun, simple_dag: SimpleDag, session):
        """
        add a DagRun object to route.
        :param simple_dag:
        :param dagrun: DagRun object to scheduling
        :return:
        """
        self.route[dagrun.id] = dagrun
        self.simple_dags[dagrun.id] = simple_dag
        self.dag_route[(dagrun.dag_id, dagrun.execution_date)] = dagrun

        task_deps = load_task_dependencies(dagrun.dag_id, session=session)
        for task_key, deps in task_deps.items():
            for key, e_type in deps:
                if (key, e_type) not in self.event_route:
                    self.event_route[(key, e_type)] = []
                if dagrun not in self.event_route[(key, e_type)]:
                    self.event_route[(key, e_type)].append(dagrun)

    def remove_dagrun(self, dagrun: DagRun, session):
        """
        remove DagRun object from route.
        :param dagrun: DagRun object
        :return:
        """
        if dagrun.id in self.route:
            del self.route[dagrun.id]
        if dagrun.id in self.simple_dags:
            del self.simple_dags[dagrun.id]

        if (dagrun.dag_id, dagrun.execution_date) in self.dag_route:
            del self.dag_route[(dagrun.dag_id, dagrun.execution_date)]

        task_deps = load_task_dependencies(dagrun.dag_id, session=session)
        for task_key, deps in task_deps.items():
            for key, e_type in deps:
                if self.event_route[(key, e_type)] is not None:
                    self.event_route[(key, e_type)].remove(dagrun)
                    break

    def find_dagruns_by_event(self, event_key, event_type) -> List:
        """
        Find DagRun objects are affected by the event.
        :param event_key: EVENT message key field.
        :param event_type: EVENT message event_type field
        :return: List of DagRun object
        """
        return self.event_route.get((event_key, event_type))

    def find_dagrun(self, dag_id, execution_data) -> DagRun:
        """
        Find DagRun object by dag_id and execution_date
        :param dag_id: the DagRun object dag_id
        :param execution_data: the DagRun object execution_date
        :return: DagRun object
        """
        return self.dag_route.get((dag_id, execution_data))

    def find_dagrun_by_id(self, dagrun_id):
        """
        Find the DagRun object by id.
        :param dagrun_id: DagRun object id field.
        :return: DagRun object
        """
        return self.route.get(dagrun_id)

    def find_pickle_id(self, dagrun_id):
        """
        Find the DagRun object pickle_id
        :param dagrun_id: DagRun object id field.
        :return: pickle_id
        """
        res = self.route.get(dagrun_id)
        if res is None:
            return None
        else:
            return res.pickle_id

    def find_simple_dag(self, dagrun_id):
        return self.simple_dags[dagrun_id]


class SCEventWatcher(EventWatcher):
    """
    The Notification service event watcher which set the messages to scheduler mailbox.
    """

    def __init__(self, mailbox: Mailbox) -> None:
        self.mailbox = mailbox

    def process(self, events: List[Event]):
        for e in events:
            self.mailbox.send_message(e)


class SimpleDagRun(object):
    """
    A simple wrapper for DagRun
    """

    def __init__(self, dag_run_id, simple_dag) -> None:
        self.dag_run_id = dag_run_id
        self.simple_dag = simple_dag


def process_tasks(dag_run, simple_dag, log):
    def _process_scheduleable_ti(session, ti):
        """
        Process the TaskInstance object which can be scheduled.
        :param session:
        :param ti:
        :return:
        """
        from airflow.ti_deps.deps.runnable_exec_date_dep import RunnableExecDateDep
        from airflow.ti_deps.deps.valid_state_dep import ValidStateDep
        from airflow.ti_deps.deps.events_dep import EventTIDep

        EVENT_SCHEDULED_DEPS = {
            RunnableExecDateDep(),
            ValidStateDep(SCHEDULEABLE_STATES),
            EventTIDep(),
        }
        dep_context = DepContext(deps=EVENT_SCHEDULED_DEPS)
        if ti.are_dependencies_met(dep_context=dep_context, session=session):
            ts = TaskState.query_task_state(ti, session=session)
            if ts.action is None or TaskAction(ts.action) in START_ACTION:
                log.debug('Queuing task: %s', ti)
                ti.state = State.SCHEDULED
                log.info("Creating / updating %s in ORM", ti)
                session.merge(ti)
            ts.action = None
            session.merge(ts)
            session.commit()

    def _process_finished_ti(session, ti):
        """
        Process the TaskInstance object which already finished.
        :param session:
        :param ti:
        :return:
        """
        from airflow.ti_deps.deps.runnable_exec_date_dep import RunnableExecDateDep
        from airflow.ti_deps.deps.valid_state_dep import ValidStateDep
        from airflow.ti_deps.deps.events_dep import EventTIDep

        EVENT_SCHEDULED_DEPS = {
            RunnableExecDateDep(),
            ValidStateDep(FINISHED_STATES),
            EventTIDep(),
        }
        dep_context = DepContext(deps=EVENT_SCHEDULED_DEPS)
        if ti.are_dependencies_met(dep_context=dep_context, session=session):
            ts = TaskState.query_task_state(ti, session=session)
            if ts.action is None or TaskAction(ts.action) == TaskAction.NONE:
                return
            if TaskAction(ts.action) == TaskAction.RESTART:
                log.debug('Queuing Finished task: %s', ti)
                ti.state = State.SCHEDULED
                log.info("Creating / updating %s in ORM", ti)
                session.merge(ti)
            ts.action = None
            session.merge(ts)
            session.commit()

    def _process_running_ti(session, ti):
        """
        Process the TaskInstance object which are running.
        :param session:
        :param ti:
        :return:
        """
        from airflow.ti_deps.deps.runnable_exec_date_dep import RunnableExecDateDep
        from airflow.ti_deps.deps.valid_state_dep import ValidStateDep
        from airflow.ti_deps.deps.events_dep import EventTIDep

        EVENT_SCHEDULED_DEPS = {
            RunnableExecDateDep(),
            ValidStateDep(RUNNING_STATES),
            EventTIDep(),
        }
        dep_context = DepContext(deps=EVENT_SCHEDULED_DEPS)
        if ti.are_dependencies_met(dep_context=dep_context, session=session):
            if action_is_stop_or_restart(ti, session):
                log.info("stop or restart task %s ", ti)

    dagbag = models.DagBag(dag_folder=simple_dag.full_filepath)
    dag_run.dag = dagbag.get_dag(simple_dag.dag_id)
    with create_session() as session:
        tis = dag_run.get_task_instances(session=session)
        for ti in tis:
            task = dag_run.dag.get_task(ti.task_id)
            ti.task = task
            if ti.state in SCHEDULEABLE_STATES:
                _process_scheduleable_ti(session, ti)
            elif ti.state in FINISHED_STATES:
                _process_finished_ti(session, ti)
            elif ti.state in RUNNING_STATES:
                _process_running_ti(session, ti)


def dag_run_update_state(dag_run, simple_dag):
    dagbag = models.DagBag(dag_folder=simple_dag.full_filepath)
    with create_session() as session:
        dag_run.dag = dagbag.get_dag(simple_dag.dag_id, session)
        dag_run.update_state(session)


def run_process_func(target, args):
    # use fork the subprocess will heri
    ctx = mp.get_context('forkserver')
    p = None
    try:
        p = ctx.Process(target=target, args=args)
        p.start()
        p.join()
        if 0 != p.exitcode:
            raise Exception("run_process_func {} exitcode {} not equal 0".format(str(target), p.exitcode))
    finally:
        if p is not None:
            p.close()


def load_task_dependencies(dag_id, session):
    dag_model = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
    if dag_model is None:
        return None
    else:
        deps_str = dag_model.task_dependencies
        deps = json.loads(deps_str)
        task_deps = {}
        for k, v in deps.items():
            if len(v) > 0:
                task_deps[k] = set()
                for item in v:
                    task_deps[k].add((item[0], item[1]))
        return task_deps


class EventSchedulerJob(SchedulerJob):
    """
    EventSchedulerJob: The scheduler driven by events.
    The scheduler get the message from notification service, then scheduling the tasks which affected by the events.
    """

    __mapper_args__ = {
        'polymorphic_identity': 'EventSchedulerJob'
    }

    def __init__(self, dag_id=None, dag_ids=None, subdir=settings.DAGS_FOLDER,
                 num_runs=conf.getint('scheduler', 'num_runs', fallback=-1),
                 processor_poll_interval=conf.getfloat('scheduler', 'processor_poll_interval', fallback=1),
                 use_local_nf=conf.getboolean('scheduler', 'use_local_notification', fallback=True),
                 nf_host=conf.get('scheduler', 'notification_host', fallback='localhost'),
                 nf_port=conf.getint('scheduler', 'notification_port', fallback=50051),
                 unit_test_mode=conf.getboolean('core', 'unit_test_mode', fallback=False),
                 executor_heartbeat_interval=conf.getint('scheduler', 'executor_heartbeat_interval', fallback=2),
                 run_duration=None, do_pickle=False, log=None, *args,
                 **kwargs):
        super().__init__(dag_id, dag_ids, subdir, num_runs, processor_poll_interval, run_duration, do_pickle, log,
                         *args, **kwargs)
        self.dag_trigger = None
        self.notification_master = None
        self.use_local_nf = use_local_nf
        self.nf_host = nf_host
        self.nf_port = nf_port
        self.mail_box = Mailbox()
        self.running = True
        self.dagrun_route = DagRunRoute()
        self.unit_test_mode = unit_test_mode
        self.executor_heartbeat_interval = executor_heartbeat_interval
        self.heartbeat_thread = None

    @provide_session
    def _get_dag_runs(self, event, session):
        dag_runs = []
        if EventType.is_in(event.event_type) and EventType(event.event_type) != EventType.UNDEFINED:
            if EventType(event.event_type) == EventType.DAG_RUN_EXECUTABLE:
                dag_run_id = int(event.key)
                dag_run = session.query(DagRun).filter(DagRun.id == dag_run_id).first()
                if dag_run is None:
                    self.log.error("DagRun is None id {0}".format(dag_run_id))
                    return dag_runs
                simple_dag = event.simple_dag
                dag_run.pickle_id = None
                # create route
                self.dagrun_route.add_dagrun(dag_run, simple_dag, session)
                dag_runs.append(dag_run)

            elif EventType(event.event_type) == EventType.TASK_STATUS_CHANGED:
                dag_id, task_id, execution_date = TaskInstanceHelper.from_task_key(event.key)
                state, try_num = TaskInstanceHelper.from_event_value(event.value)
                dag_run = self.dagrun_route.find_dagrun(dag_id, execution_date)
                if dag_run is None:
                    return dag_runs
                self._set_task_instance_state(dag_run, dag_id, task_id, execution_date, state, try_num)

                sync_dag_run = session.query(DagRun).filter(DagRun.id == dag_run.id).first()
                if sync_dag_run.state in State.finished():
                    self.log.info("DagRun finished dag_id {0} execution_date {1} state {2}"
                                  .format(dag_run.dag_id, dag_run.execution_date, sync_dag_run.state))
                    if self.dagrun_route.find_dagrun_by_id(sync_dag_run.id) is not None:
                        self.dagrun_route.remove_dagrun(dag_run, session)
                        self.log.debug("Route remove dag run {0}".format(sync_dag_run.id))
                        self.mail_box.send_message(DagRunFinishedEvent(dag_run.id, sync_dag_run.state))
                else:
                    dag_runs.append(dag_run)

            elif EventType(event.event_type) == EventType.DAG_RUN_FINISHED:
                self.log.debug("DagRun {0} finished".format(event.key))
            elif EventType(event.event_type) == EventType.STOP_SCHEDULER_CMD:
                if self.unit_test_mode:
                    self.running = False
                return dag_runs
        else:
            runs = self.dagrun_route.find_dagruns_by_event(event_key=event.key, event_type=event.event_type)
            if runs is not None:
                for run in runs:
                    task_deps = load_task_dependencies(dag_id=run.dag_id, session=session)
                    tis = run.get_task_instances(session=session)
                    for ti in tis:
                        if ti.task_id not in task_deps:
                            continue
                        if (event.key, event.event_type) in task_deps[ti.task_id]:
                            self.log.debug("{0} handle event {1}".format(ti.task_id, event))
                            ts = TaskState.query_task_state(ti, session=session)
                            handler = ts.event_handler
                            if handler is not None:
                                action = handler.handle_event(event, ti=ti, ts=ts, session=session)
                                ts.action = action
                                session.merge(ts)
                                session.commit()
                                self.log.debug("set task action {0} {1}".format(ti.task_id, action))
                dag_runs.extend(runs)
                session.commit()

        for dag_run in dag_runs:
            run_process_func(target=process_tasks, args=(dag_run, self.dagrun_route.find_simple_dag(dag_run.id), self.log,))
        return dag_runs

    @provide_session
    def _sync_event_to_db(self, event: Event, session=None):
        EventModel.sync_event(event=event, session=session)

    @provide_session
    def _run_event_loop(self, session=None):
        """
        The main process event loop
        :param session: the connection of db session.
        :return: None
        """
        while self.running:
            event: Event = self.mail_box.get_message()
            self.log.debug('EVENT: {0}'.format(event))
            if not self.use_local_nf:
                self._sync_event_to_db(session)
            try:
                dag_runs = self._get_dag_runs(event)
                if dag_runs is None or len(dag_runs) == 0:
                    continue
                # create SimpleDagBag
                simple_dags = []
                for dag_run in dag_runs:
                    simple_dags.append(self.dagrun_route.find_simple_dag(dagrun_id=dag_run.id))
                simple_dag_bag = SimpleDagBag(simple_dags)
                if not self._validate_and_run_task_instances(simple_dag_bag=simple_dag_bag):
                    continue
            except Exception as e:
                self.log.exception(str(e))
        # scheduler end
        self.log.debug("_run_event_loop end")

    @provide_session
    def _init_route(self, session=None):
        """
        Init the DagRunRoute object from db.
        :param session:
        :return:
        """
        # running_dag_runs = session.query(DagRun).filter(DagRun.state == State.RUNNING).all()
        # for dag_run in running_dag_runs:
        #     dag_model = session.query(DagModel).filter(DagModel.dag_id == dag_run.dag_id).first()
        #     dagbag = models.DagBag(dag_model.fileloc)
        #     dag_run.dag = dagbag.get_dag(dag_run.dag_id)
        #     self.dagrun_route.add_dagrun(dag_run)
        # todo init route
        pass

    def _executor_heartbeat(self):
        while self.running:
            self.log.info("executor heartbeat...")
            self.executor.heartbeat()
            time.sleep(self.executor_heartbeat_interval)

    def _start_executor_heartbeat(self):

        self.heartbeat_thread = threading.Thread(target=self._executor_heartbeat, args=())
        self.heartbeat_thread.setDaemon(True)
        self.heartbeat_thread.start()

    def _stop_executor_heartheat(self):
        self.running = False
        if self.heartbeat_thread is not None:
            self.heartbeat_thread.join()

    def _execute(self):
        """
        1. Init the DagRun route.
        2. Start the executor.
        3. Option of start the notification master.
        4. Create the notification client.
        5. Start the DagTrigger.
        6. Run the scheduler event loop.
        :return:
        """
        notification_client = None
        try:
            self._init_route()
            self.executor.set_use_nf(True)
            self.executor.start()
            self.dag_trigger = DagTrigger(subdir=self.subdir,
                                          mailbox=self.mail_box,
                                          run_duration=self.run_duration,
                                          using_sqlite=self.using_sqlite,
                                          num_runs=self.num_runs,
                                          processor_poll_interval=self._processor_poll_interval)
            if self.use_local_nf:
                self.notification_master \
                    = NotificationMaster(service=NotificationService(EventModelStorage()), port=self.nf_port)
                self.notification_master.run()
                self.log.info("start notification service {0}".format(self.nf_port))
                notification_client = NotificationClient(server_uri="localhost:{0}".format(self.nf_port))
            else:
                notification_client \
                    = NotificationClient(server_uri="{0}:{1}".format(self.nf_host, self.nf_port))
            notification_client.start_listen_events(watcher=SCEventWatcher(self.mail_box))
            self.dag_trigger.start()
            self._start_executor_heartbeat()
            self._run_event_loop()
        except Exception as e:
            self.log.exception("Exception when executing _execute {0}".format(str(e)))
        finally:
            self.running = False
            self._stop_executor_heartheat()
            if self.dag_trigger is not None:
                self.dag_trigger.stop()
            if notification_client is not None:
                notification_client.stop_listen_events()
            if self.notification_master is not None:
                self.notification_master.stop()
            self.executor.end()
            self.log.info("Exited execute event scheduler")

    @provide_session
    def _set_task_instance_state(self, dag_run, dag_id, task_id, execution_date, state, try_number, session=None):
        """
        Set the task state to db and maybe set the dagrun object finished to db.
        :param dag_run: DagRun object
        :param dag_id: Dag identify
        :param task_id: task identify
        :param execution_date: the dag run execution date
        :param state: the task state should be set.
        :param try_number: the task try_number.
        :param session:
        :return:
        """
        TI = models.TaskInstance
        qry = session.query(TI).filter(TI.dag_id == dag_id,
                                       TI.task_id == task_id,
                                       TI.execution_date == execution_date)
        ti = qry.first()
        if not ti:
            self.log.warning("TaskInstance %s went missing from the database", ti)
            return
        ts = TaskState.query_task_state(ti, session)
        self.log.debug("set task state dag_id {0} task_id {1} execution_date {2} try_number {3} "
                       "current try_number {4} state {5} ack_id {6} action {7}."
                       .format(dag_id, task_id, execution_date, try_number, ti.try_number, state,
                               ts.ack_id, ts.action))
        is_restart = False
        if state == State.FAILED or state == State.SUCCESS or state == State.SHUTDOWN:
            if ti.try_number == try_number and ti.state == State.QUEUED:
                msg = ("Executor reports task instance {} finished ({}) "
                       "although the task says its {}. Was the task "
                       "killed externally?".format(ti, state, ti.state))
                Stats.incr('scheduler.tasks.killed_externally')
                self.log.error(msg)
                try:
                    dag = self.task_route.find_dagrun(dag_id, execution_date)
                    ti.task = dag.get_task(task_id)
                    ti.handle_failure(msg)
                except Exception:
                    self.log.error("Cannot load the dag bag to handle failure for %s"
                                   ". Setting task to FAILED without callbacks or "
                                   "retries. Do you have enough resources?", ti)
                ti.state = State.FAILED
                session.merge(ti)
            else:
                if ts.action is None:
                    self.log.debug("task dag_id {0} task_id {1} execution_date {2} action is None."
                                   .format(dag_id, task_id, execution_date))
                elif TaskAction(ts.action) == TaskAction.RESTART:
                    # if ts.stop_flag is not None and ts.stop_flag == try_number:
                    ti.state = State.SCHEDULED
                    ts.action = None
                    ts.stop_flag = None
                    ts.ack_id = 0
                    session.merge(ti)
                    session.merge(ts)
                    self.log.debug("task dag_id {0} task_id {1} execution_date {2} try_number {3} restart action."
                                   .format(dag_id, task_id, execution_date, str(try_number)))
                    is_restart = True
                elif TaskAction(ts.action) == TaskAction.STOP:
                    # if ts.stop_flag is not None and ts.stop_flag == try_number:
                    ts.action = None
                    ts.stop_flag = None
                    ts.ack_id = 0
                    session.merge(ts)
                    self.log.debug("task dag_id {0} task_id {1} execution_date {2} try_number {3} stop action."
                                   .format(dag_id, task_id, execution_date, str(try_number)))
                else:
                    self.log.debug("task dag_id {0} task_id {1} execution_date {2} action {3}."
                                   .format(dag_id, task_id, execution_date, ts.action))
            session.commit()

        if not is_restart and ti.state == State.RUNNING:
            self.log.debug("set task dag_id {0} task_id {1} execution_date {2} state {3}"
                           .format(dag_id, task_id, execution_date, state))
            ti.state = state
            session.merge(ti)
        session.commit()
        # update dagrun state
        sync_dag_run = session.query(DagRun).filter(DagRun.id == dag_run.id).first()
        if sync_dag_run.state not in FINISHED_STATES:
            if self.dagrun_route.find_dagrun_by_id(sync_dag_run.id) is None:
                self.log.error("DagRun lost dag_id {0} task_id {1} execution_date {2}"
                               .format(dag_id, task_id, execution_date))
            else:
                run_process_func(target=dag_run_update_state,
                                 args=(dag_run, self.dagrun_route.find_simple_dag(dag_run.id),))

    @provide_session
    def _create_task_instances(self, dag_run, session=None):
        """
        This method schedules the tasks for a single DAG by looking at the
        active DAG runs and adding task instances that should run to the
        queue.
        """

        # update the state of the previously active dag runs
        dag_runs = DagRun.find(dag_id=dag_run.dag_id, state=State.RUNNING, session=session)
        active_dag_runs = []
        for run in dag_runs:
            self.log.info("Examining DAG run %s", run)
            # don't consider runs that are executed in the future unless
            # specified by config and schedule_interval is None
            if run.execution_date > timezone.utcnow() and not dag_run.dag.allow_future_exec_dates:
                self.log.error(
                    "Execution date is in future: %s",
                    run.execution_date
                )
                continue

            if len(active_dag_runs) >= dag_run.dag.max_active_runs:
                self.log.info("Number of active dag runs reached max_active_run.")
                break

            # skip backfill dagruns for now as long as they are not really scheduled
            if run.is_backfill:
                continue

            run.dag = dag_run.dag

            # todo: preferably the integrity check happens at dag collection time
            run.verify_integrity(session=session)
            run.update_state(session=session)
            if run.state == State.RUNNING:
                make_transient(run)
                active_dag_runs.append(run)

    def _process_dags_and_create_dagruns(self, dagbag, dags, dagrun_out):
        """
        Iterates over the dags and processes them. Processing includes:

        1. Create appropriate DagRun(s) in the DB.
        2. Create appropriate TaskInstance(s) in the DB.
        3. Send emails for tasks that have missed SLAs.

        :param dagbag: a collection of DAGs to process
        :type dagbag: airflow.models.DagBag
        :param dags: the DAGs from the DagBag to process
        :type dags: list[airflow.models.DAG]
        :param dagrun_out: A list to add DagRun objects
        :type dagrun_out: list[DagRun]
        :rtype: None
        """
        for dag in dags:
            dag = dagbag.get_dag(dag.dag_id)
            if not dag:
                self.log.error("DAG ID %s was not found in the DagBag", dag.dag_id)
                continue

            if dag.is_paused:
                self.log.info("Not processing DAG %s since it's paused", dag.dag_id)
                continue

            self.log.info("Processing %s", dag.dag_id)

            dag_run = self.create_dag_run(dag)
            if dag_run:
                dag_run.dag = dag
                expected_start_date = dag.following_schedule(dag_run.execution_date)
                if expected_start_date:
                    schedule_delay = dag_run.start_date - expected_start_date
                    Stats.timing(
                        'dagrun.schedule_delay.{dag_id}'.format(dag_id=dag.dag_id),
                        schedule_delay)
                self.log.info("Created %s", dag_run)
                self._create_task_instances(dag_run)
                self.log.info("Created tasks instances %s", dag_run)
                dagrun_out.append(dag_run)
            if conf.getboolean('core', 'CHECK_SLAS', fallback=True):
                self.manage_slas(dag)

    @provide_session
    def process_file(self, file_path, zombies, pickle_dags=False, session=None):
        """
        Process a Python file containing Airflow DAGs.

        This includes:

        1. Execute the file and look for DAG objects in the namespace.
        2. Pickle the DAG and save it to the DB (if necessary).
        3. For each DAG, see what tasks should run and create appropriate task
        instances in the DB.
        4. Record any errors importing the file into ORM
        5. Kill (in ORM) any task instances belonging to the DAGs that haven't
        issued a heartbeat in a while.

        Returns a list of SimpleDag objects that represent the DAGs found in
        the file

        :param file_path: the path to the Python file that should be executed
        :type file_path: unicode
        :param zombies: zombie task instances to kill.
        :type zombies: list[airflow.utils.dag_processing.SimpleTaskInstance]
        :param pickle_dags: whether serialize the DAGs found in the file and
            save them to the db
        :type pickle_dags: bool
        :return: a list of SimpleDagRuns made from the Dags found in the file
        :rtype: list[airflow.utils.dag_processing.SimpleDagBag]
        """
        self.log.info("Processing file %s for tasks to queue", file_path)
        if session is None:
            session = settings.Session()
        # As DAGs are parsed from this file, they will be converted into SimpleDags

        try:
            dagbag = models.DagBag(file_path, include_examples=False)
        except Exception:
            self.log.exception("Failed at reloading the DAG file %s", file_path)
            Stats.incr('dag_file_refresh_error', 1, 1)
            return [], []

        if len(dagbag.dags) > 0:
            self.log.info("DAG(s) %s retrieved from %s", dagbag.dags.keys(), file_path)
        else:
            self.log.warning("No viable dags retrieved from %s", file_path)
            self.update_import_errors(session, dagbag)
            return [], len(dagbag.import_errors)

        # Save individual DAGs in the ORM and update DagModel.last_scheduled_time
        for dag in dagbag.dags.values():
            dag.sync_to_db()

        paused_dag_ids = [dag.dag_id for dag in dagbag.dags.values()
                          if dag.is_paused]
        self.log.info("paused_dag_ids %s", paused_dag_ids)
        self.log.info("self %s", self.dag_ids)

        dag_to_pickle = {}
        # Pickle the DAGs (if necessary) and put them into a SimpleDag
        for dag_id in dagbag.dags:
            # Only return DAGs that are not paused
            if dag_id not in paused_dag_ids:
                dag = dagbag.get_dag(dag_id)
                pickle_id = None
                if pickle_dags:
                    pickle_id = dag.pickle(session).id
                dag_to_pickle[dag.dag_id] = pickle_id

        if len(self.dag_ids) > 0:
            dags = [dag for dag in dagbag.dags.values()
                    if dag.dag_id in self.dag_ids and
                    dag.dag_id not in paused_dag_ids]
        else:
            dags = [dag for dag in dagbag.dags.values()
                    if not dag.parent_dag and
                    dag.dag_id not in paused_dag_ids]

        # Not using multiprocessing.Queue() since it's no longer a separate
        # process and due to some unusual behavior. (empty() incorrectly
        # returns true as described in https://bugs.python.org/issue23582 )
        self.log.info("dags %s", dags)
        dag_run_out = []
        self._process_dags_and_create_dagruns(dagbag, dags, dag_run_out)
        self.log.info("dag run out %s", len(dag_run_out))
        simple_dag_runs = []
        for dag_run in dag_run_out:
            simple_dag_runs.append(SimpleDagRun(dag_run.id, SimpleDag(dag_run.dag)))
        # commit batch
        session.commit()

        # Record import errors into the ORM
        try:
            self.update_import_errors(session, dagbag)
        except Exception:
            self.log.exception("Error logging import errors!")
        try:
            dagbag.kill_zombies(zombies)
        except Exception:
            self.log.exception("Error killing zombies!")

        return simple_dag_runs, len(dagbag.import_errors)
