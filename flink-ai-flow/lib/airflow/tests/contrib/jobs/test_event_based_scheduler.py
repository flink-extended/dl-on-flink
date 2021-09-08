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
import os
import pickle
import sqlalchemy
import time
import unittest
import threading

from airflow.models.serialized_dag import SerializedDagModel

from airflow.utils.types import DagRunType

from airflow.utils import timezone
from airflow.utils.state import State
from typing import List

from airflow.executors.scheduling_action import SchedulingAction
from airflow.contrib.jobs.scheduler_client import EventSchedulerClient
from airflow.models.taskexecution import TaskExecution
from notification_service.base_notification import BaseEvent, UNDEFINED_EVENT_TYPE
from notification_service.client import NotificationClient
from notification_service.event_storage import MemoryEventStorage
from notification_service.master import NotificationMaster
from notification_service.service import NotificationService

from airflow.contrib.jobs.event_based_scheduler_job import EventBasedSchedulerJob, SchedulerEventWatcher, \
    EventBasedScheduler
from airflow.executors.local_executor import LocalExecutor
from airflow.models import TaskInstance, Message, DagBag, DagRun
from airflow.jobs.base_job import BaseJob
from airflow.utils.mailbox import Mailbox
from airflow.utils.session import create_session, provide_session
from airflow.events.scheduler_events import StopSchedulerEvent, StopDagEvent, TaskSchedulingEvent
from tests.test_utils import db

TEST_DAG_FOLDER = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir, 'dags')
EVENT_BASED_SCHEDULER_DAG = 'event_based_scheduler_dag'


class TestEventBasedScheduler(unittest.TestCase):

    def setUp(self):
        db.clear_db_jobs()
        db.clear_db_dags()
        db.clear_db_serialized_dags()
        db.clear_db_runs()
        db.clear_db_task_execution()
        db.clear_db_message()
        db.clear_db_event_progress()
        self.scheduler = None
        self.port = 50102
        self.storage = MemoryEventStorage()
        self.master = NotificationMaster(NotificationService(self.storage), self.port)
        self.master.run()
        self.client = NotificationClient(server_uri="localhost:{}".format(self.port),
                                         default_namespace="test_namespace")
        time.sleep(1)

    def tearDown(self):
        self.master.stop()

    def _get_task_instance(self, dag_id, task_id, session):
        return session.query(TaskInstance).filter(
            TaskInstance.dag_id == dag_id,
            TaskInstance.task_id == task_id
        ).first()

    def schedule_task_function(self):
        stopped = False
        while not stopped:
            with create_session() as session:
                ti_sleep_1000_secs = self._get_task_instance(EVENT_BASED_SCHEDULER_DAG, 'sleep_1000_secs', session)
                ti_python_sleep = self._get_task_instance(EVENT_BASED_SCHEDULER_DAG, 'python_sleep', session)
                if ti_sleep_1000_secs and ti_sleep_1000_secs.state == State.SCHEDULED and \
                   ti_python_sleep and ti_python_sleep.state == State.SCHEDULED:
                    self.client.send_event(BaseEvent(key='start', value='', event_type='', namespace='test_namespace'))

                    while not stopped:
                        ti_sleep_1000_secs.refresh_from_db()
                        ti_python_sleep.refresh_from_db()
                        if ti_sleep_1000_secs and ti_sleep_1000_secs.state == State.RUNNING and \
                           ti_python_sleep and ti_python_sleep.state == State.RUNNING:
                            time.sleep(10)
                            break
                        else:
                            time.sleep(1)
                    self.client.send_event(BaseEvent(key='stop', value='',
                                                     event_type=UNDEFINED_EVENT_TYPE, namespace='test_namespace'))
                    self.client.send_event(BaseEvent(key='restart', value='',
                                                     event_type=UNDEFINED_EVENT_TYPE, namespace='test_namespace'))
                    while not stopped:
                        ti_sleep_1000_secs.refresh_from_db()
                        ti_python_sleep.refresh_from_db()
                        if ti_sleep_1000_secs and ti_sleep_1000_secs.state == State.KILLED and \
                           ti_python_sleep and ti_python_sleep.state == State.RUNNING:
                            stopped = True
                        else:
                            time.sleep(1)
                else:
                    time.sleep(1)
        self.client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_event_based_scheduler(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_event_based_scheduler.py')
        t = threading.Thread(target=self.schedule_task_function)
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)

    def test_replay_message(self):
        key = "stop"
        mailbox = Mailbox()
        mailbox.set_scheduling_job_id(1234)
        watcher = SchedulerEventWatcher(mailbox)
        self.client.start_listen_events(
            watcher=watcher,
            start_time=int(time.time() * 1000),
            version=None
        )
        self.send_event(key)
        msg: BaseEvent = mailbox.get_message()
        self.assertEqual(msg.key, key)
        with create_session() as session:
            msg_from_db = session.query(Message).first()
            expect_non_unprocessed = EventBasedScheduler.get_unprocessed_message(1000)
            self.assertEqual(0, len(expect_non_unprocessed))
            unprocessed = EventBasedScheduler.get_unprocessed_message(1234)
            self.assertEqual(unprocessed[0].serialized_message, msg_from_db.data)
        deserialized_data = pickle.loads(msg_from_db.data)
        self.assertEqual(deserialized_data.key, key)
        self.assertEqual(msg, deserialized_data)

    def send_event(self, key):
        event = self.client.send_event(BaseEvent(key=key,
                                                 event_type=UNDEFINED_EVENT_TYPE,
                                                 value="value1"))
        self.assertEqual(key, event.key)

    @provide_session
    def get_task_execution(self, dag_id, task_id, session):
        return session.query(TaskExecution).filter(TaskExecution.dag_id == dag_id,
                                                   TaskExecution.task_id == task_id).all()

    @provide_session
    def get_latest_job_id(self, session):
        return session.query(BaseJob).order_by(sqlalchemy.desc(BaseJob.id)).first().id

    def start_scheduler(self, file_path, event_start_time=int(time.time()*1000)):
        self.scheduler = EventBasedSchedulerJob(
            dag_directory=file_path,
            server_uri="localhost:{}".format(self.port),
            event_start_time=event_start_time,
            executor=LocalExecutor(3),
            max_runs=-1,
            refresh_dag_dir_interval=30
        )
        print("scheduler starting")
        self.scheduler.run()

    def wait_for_running(self):
        while True:
            if self.scheduler is not None:
                time.sleep(5)
                break
            else:
                time.sleep(1)

    def wait_for_task_execution(self, dag_id, task_id, expected_num):
        result = False
        check_nums = 100
        while check_nums > 0:
            time.sleep(2)
            check_nums = check_nums - 1
            tes = self.get_task_execution(dag_id, task_id)
            if len(tes) == expected_num:
                result = True
                break
        self.assertTrue(result)

    def wait_for_task(self, dag_id, task_id, expected_state):
        result = False
        check_nums = 100
        while check_nums > 0:
            time.sleep(2)
            check_nums = check_nums - 1
            with create_session() as session:
                ti = session.query(TaskInstance).filter(
                    TaskInstance.dag_id == dag_id,
                    TaskInstance.task_id == task_id
                ).first()
            if ti and ti.state == expected_state:
                result = True
                break
        self.assertTrue(result)

    def test_notification(self):
        self.client.send_event(BaseEvent(key='a', value='b'))

    def run_a_task_function(self):
        while True:
            with create_session() as session:
                tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'single',
                                                          TaskExecution.task_id == 'task_1').all()
                if len(tes) > 0:
                    break
                else:
                    time.sleep(1)
        self.client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_run_a_task(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_single_task_dag.py')
        print(dag_file)
        t = threading.Thread(target=self.run_a_task_function, args=())
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)
        tes: List[TaskExecution] = self.get_task_execution("single", "task_1")
        self.assertEqual(len(tes), 1)

    def run_event_task_function(self):
        client = NotificationClient(server_uri="localhost:{}".format(self.port),
                                    default_namespace="")
        while True:
            with create_session() as session:
                tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'event_dag',
                                                          TaskExecution.task_id == 'task_1').all()
                if len(tes) > 0:
                    time.sleep(5)
                    client.send_event(BaseEvent(key='start', value='', event_type='', namespace=''))
                    while True:
                        with create_session() as session_2:
                            tes_2 = session_2.query(TaskExecution).filter(TaskExecution.dag_id == 'event_dag',
                                                                          TaskExecution.task_id == 'task_2',
                                                                          TaskExecution.state == State.SUCCESS).all()
                            if len(tes_2) > 0:
                                break
                            else:
                                time.sleep(1)
                    break
                else:
                    time.sleep(1)
        time.sleep(5)
        client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_run_event_task(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_event_task_dag.py')
        t = threading.Thread(target=self.run_event_task_function, args=())
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)
        tes: List[TaskExecution] = self.get_task_execution("event_dag", "task_2")
        self.assertEqual(len(tes), 1)

    def run_task_retry_function(self):
        client = NotificationClient(server_uri="localhost:{}".format(self.port),
                                    default_namespace="")
        while True:
            with create_session() as session:
                dagruns = session.query(DagRun).filter(DagRun.dag_id == 'task_retry',
                                                       DagRun.state == State.RUNNING).all()
                if len(dagruns) > 0:
                    client.send_event(BaseEvent(key='start', value='', event_type='', namespace=''))
                    break
                else:
                    time.sleep(1)
        flag_1 = True
        while True:
            with create_session() as session:
                tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'task_retry',
                                                          TaskExecution.task_id == 'task_1',
                                                          TaskExecution.state == State.FAILED).all()
                if len(tes) == 1 and flag_1:
                    client.send_event(BaseEvent(key='start', value='', event_type='', namespace=''))
                    flag_1 = False
                elif len(tes) == 2:
                    break
                else:
                    time.sleep(1)
        client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_task_retry(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_task_retry_dag.py')
        t = threading.Thread(target=self.run_task_retry_function, args=())
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)
        tes: List[TaskExecution] = self.get_task_execution("task_retry", "task_1")
        self.assertEqual(len(tes), 2)

    def run_kill_task_retry_function(self):
        client = NotificationClient(server_uri="localhost:{}".format(self.port),
                                    default_namespace="")
        while True:
            with create_session() as session:
                dagrun = session.query(DagRun).filter(DagRun.dag_id == 'kill_task_retry',
                                                      DagRun.state == State.RUNNING).first()
                if dagrun is not None:
                    client.send_event(BaseEvent(key='start', value='', event_type='', namespace=''))
                    break
                else:
                    time.sleep(1)
        while True:
            with create_session() as session:
                ti = session.query(TaskInstance).filter(TaskInstance.dag_id == 'kill_task_retry',
                                                        TaskInstance.task_id == 'task_1').first()
                if ti is not None and ti.state == State.RUNNING:
                    client.send_event(TaskSchedulingEvent(dag_id=ti.dag_id,
                                                          task_id=ti.task_id,
                                                          execution_date=ti.execution_date,
                                                          try_number=ti.try_number,
                                                          action=SchedulingAction.STOP).to_event())
                    break
                else:
                    time.sleep(1)
        while True:
            with create_session() as session:
                te = session.query(TaskExecution).filter(TaskExecution.dag_id == 'kill_task_retry',
                                                         TaskExecution.task_id == 'task_1').first()
                if te is not None and te.state == State.KILLED:
                    break
                else:
                    time.sleep(1)
        client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_kill_task_retry(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_kill_task_retry_dag.py')
        t = threading.Thread(target=self.run_kill_task_retry_function, args=())
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)
        tes: List[TaskExecution] = self.get_task_execution("kill_task_retry", "task_1")
        self.assertEqual(len(tes), 1)

    def run_recover_message_function(self):
        client = NotificationClient(server_uri="localhost:{}".format(self.port),
                                    default_namespace="")
        while True:
            with create_session() as session:
                tes_2 = session.query(TaskExecution).filter(TaskExecution.dag_id == 'event_dag',
                                                            TaskExecution.task_id == 'task_2',
                                                            TaskExecution.state == State.SUCCESS).all()
                if len(tes_2) > 1:
                    break
                else:
                    time.sleep(1)
        client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_recover_message(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_event_task_dag.py')
        t = threading.Thread(target=self.run_event_task_function, args=())
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)
        tes: List[TaskExecution] = self.get_task_execution("event_dag", "task_2")
        self.assertEqual(len(tes), 1)
        time.sleep(10)
        client = NotificationClient(server_uri="localhost:{}".format(self.port),
                                    default_namespace="")
        client.send_event(BaseEvent(key='start', value='', event_type='', namespace=''))
        time.sleep(5)

        t = threading.Thread(target=self.run_recover_message_function, args=())
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file, None)

        tes: List[TaskExecution] = self.get_task_execution("event_dag", "task_2")
        self.assertEqual(len(tes), 2)

    def run_trigger_dag_function(self, dag_file):
        time.sleep(5)
        ns_client = NotificationClient(server_uri="localhost:{}".format(self.port), default_namespace="")
        client = EventSchedulerClient(ns_client=ns_client)
        while True:
            with create_session() as session:
                tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'trigger_dag',
                                                          TaskExecution.task_id == 'task_1').all()
                if len(tes) > 0:
                    break
                else:
                    client.trigger_parse_dag(dag_file)
                    result = client.schedule_dag('trigger_dag')
                    print('result {}'.format(result.dagrun_id))
                time.sleep(5)
        ns_client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_run_trigger_dag(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_run_trigger_dag.py')
        t = threading.Thread(target=self.run_trigger_dag_function, args=(dag_file,))
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)
        tes: List[TaskExecution] = self.get_task_execution("trigger_dag", "task_1")
        self.assertEqual(len(tes), 1)

    def run_no_dag_file_function(self, dag_file):
        time.sleep(5)
        ns_client = NotificationClient(server_uri="localhost:{}".format(self.port), default_namespace="")
        client = EventSchedulerClient(ns_client=ns_client)
        with create_session() as session:
            client.trigger_parse_dag(dag_file)
            result = client.schedule_dag('no_dag')
            print('result {}'.format(result.dagrun_id))
            time.sleep(5)
        ns_client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_no_dag_file_trigger_dag(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_run_trigger_dag.py')
        t = threading.Thread(target=self.run_no_dag_file_function, args=(dag_file,))
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)
        tes: List[TaskExecution] = self.get_task_execution("trigger_dag", "task_1")
        self.assertEqual(len(tes), 0)

    def run_trigger_task_function(self):
        # waiting parsed dag file done,
        time.sleep(5)
        ns_client = NotificationClient(server_uri="localhost:{}".format(self.port), default_namespace="a")
        client = EventSchedulerClient(ns_client=ns_client)
        execution_context = client.schedule_dag('trigger_task')
        while True:
            with create_session() as session:
                tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'trigger_task',
                                                          TaskExecution.task_id == 'task_1').all()
                if len(tes) > 0:
                    client.schedule_task('trigger_task', 'task_2', SchedulingAction.START, execution_context)
                    while True:
                        with create_session() as session_2:
                            tes_2 = session_2.query(TaskExecution).filter(TaskExecution.dag_id == 'trigger_task',
                                                                          TaskExecution.task_id == 'task_2').all()
                            if len(tes_2) > 0:
                                break
                            else:
                                time.sleep(1)
                    break
                else:
                    time.sleep(1)
        ns_client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_task_trigger_dag(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_task_trigger_dag.py')
        t = threading.Thread(target=self.run_trigger_task_function, args=())
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)
        tes: List[TaskExecution] = self.get_task_execution("trigger_task", "task_2")
        self.assertEqual(len(tes), 1)

    def stop_dag_function(self):
        stopped = False
        while not stopped:
            tes = self.get_task_execution(EVENT_BASED_SCHEDULER_DAG, 'sleep_to_be_stopped')
            if tes and len(tes) == 1:
                self.client.send_event(StopDagEvent(EVENT_BASED_SCHEDULER_DAG).to_event())
                while not stopped:
                    tes2 = self.get_task_execution(EVENT_BASED_SCHEDULER_DAG, 'sleep_to_be_stopped')
                    if tes2[0].state == State.KILLED:
                        stopped = True
                        time.sleep(5)
                    else:
                        time.sleep(1)
            else:
                time.sleep(1)
        self.client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_stop_dag(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_event_based_scheduler.py')
        t = threading.Thread(target=self.stop_dag_function)
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)
        with create_session() as session:
            from airflow.models import DagModel
            dag_model: DagModel = DagModel.get_dagmodel(EVENT_BASED_SCHEDULER_DAG)
            self.assertTrue(dag_model.is_paused)
            self.assertEqual(dag_model.get_last_dagrun().state, "killed")
            for ti in session.query(TaskInstance).filter(TaskInstance.dag_id == EVENT_BASED_SCHEDULER_DAG):
                self.assertTrue(ti.state in [State.SUCCESS, State.KILLED])
            for te in session.query(TaskExecution).filter(TaskExecution.dag_id == EVENT_BASED_SCHEDULER_DAG):
                self.assertTrue(te.state in [State.SUCCESS, State.KILLED])

    def run_cron_periodic_task_function(self):
        while True:
            with create_session() as session:
                tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'single',
                                                          TaskExecution.task_id == 'task_1').all()
                if len(tes) > 2:
                    break
                else:
                    time.sleep(1)
        self.client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_run_cron_periodic_task(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_periodic_cron_task_dag.py')
        t = threading.Thread(target=self.run_cron_periodic_task_function, args=())
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)
        tes: List[TaskExecution] = self.get_task_execution("single", "task_1")
        self.assertGreater(len(tes), 1)

    def run_interval_periodic_task_function(self):
        while True:
            with create_session() as session:
                tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'single',
                                                          TaskExecution.task_id == 'task_1').all()
                if len(tes) > 2:
                    break
                else:
                    time.sleep(1)
        self.client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_run_interval_periodic_task(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_periodic_interval_task_dag.py')
        t = threading.Thread(target=self.run_interval_periodic_task_function, args=())
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)
        tes: List[TaskExecution] = self.get_task_execution("single", "task_1")
        self.assertGreater(len(tes), 1)

    def run_one_task_function(self):
        self.wait_for_running()
        self.client.send_event(BaseEvent(key='a', value='a'))
        time.sleep(5)
        self.client.send_event(BaseEvent(key='a', value='a'))
        while True:
            with create_session() as session:
                tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'single',
                                                          TaskExecution.task_id == 'task_1').all()
                if len(tes) >= 2:
                    break
                else:
                    time.sleep(1)
        self.client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_run_one_task(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_multiple_trigger_task_dag.py')
        t = threading.Thread(target=self.run_one_task_function, args=())
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)

    def schedule_with_task_status_change_check(self):
        self.wait_for_running()
        while True:
            with create_session() as session:
                tis = session.query(TaskExecution).filter(TaskExecution.dag_id == 'schedule_on_state',
                                                          TaskExecution.state == State.SUCCESS).all()
                if len(tis) >= 2:
                    break
                else:
                    time.sleep(1)
        self.client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_schedule_with_task_status_change(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_schedule_with_task_status_change.py')
        t = threading.Thread(target=self.schedule_with_task_status_change_check, args=())
        t.setDaemon(True)
        t.start()
        self.start_scheduler(dag_file)

    def test_dag_run_event_filter_by_context(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_dag_context_extractor.py')
        scheduler = EventBasedSchedulerJob(
            dag_directory=dag_file,
            server_uri="localhost:{}".format(self.port),
            executor=LocalExecutor(3),
            max_runs=-1,
            refresh_dag_dir_interval=30
        ).scheduler
        dag = DagBag(dag_file).dags['test_dag_context_extractor']
        SerializedDagModel.write_dag(dag=dag)

        dr1 = dag.create_dagrun(state=State.RUNNING,
                                execution_date=timezone.datetime(2016, 1, 1),
                                run_type=DagRunType.SCHEDULED,
                                context='test_context')
        dr2 = dag.create_dagrun(state=State.RUNNING,
                                execution_date=timezone.datetime(2016, 1, 2),
                                run_type=DagRunType.SCHEDULED,
                                context='invalid_context')
        with create_session() as session:
            dag_runs = scheduler._find_dagruns_by_event(BaseEvent(key='k', value='v'), session)
            self.assertEqual(1, len(dag_runs))
            self.assertEqual(dr1.dag_id, dag_runs[0].dag_id)

            dag_runs = scheduler._find_dagruns_by_event(BaseEvent(key='broadcast', value='v'), session)
            self.assertEqual(2, len(dag_runs))
            self.assertIn(dr1.dag_id, [dr.dag_id for dr in dag_runs])
            self.assertIn(dr2.dag_id, [dr.dag_id for dr in dag_runs])

    def test_context_extractor_tolerate_context_extractor_exception(self):
        dag_file = os.path.join(TEST_DAG_FOLDER, 'test_dag_context_extractor_throw_exception.py')
        scheduler = EventBasedSchedulerJob(
            dag_directory=dag_file,
            server_uri="localhost:{}".format(self.port),
            executor=LocalExecutor(3),
            max_runs=-1,
            refresh_dag_dir_interval=30
        ).scheduler
        dag = DagBag(dag_file).dags['test_dag_context_extractor']
        SerializedDagModel.write_dag(dag=dag)

        dr1 = dag.create_dagrun(state=State.RUNNING,
                                execution_date=timezone.datetime(2016, 1, 1),
                                run_type=DagRunType.SCHEDULED,
                                context='test_context')
        dr2 = dag.create_dagrun(state=State.RUNNING,
                                execution_date=timezone.datetime(2016, 1, 2),
                                run_type=DagRunType.SCHEDULED,
                                context='invalid_context')
        with create_session() as session:
            dag_runs = scheduler._find_dagruns_by_event(BaseEvent(key='k', value='v'), session)
            self.assertEqual(0, len(dag_runs))
