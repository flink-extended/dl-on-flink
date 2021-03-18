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
import datetime
import os
import pickle
import time
import unittest
from typing import List

import psutil
from airflow.models.taskexecution import TaskExecution
from notification_service.base_notification import BaseEvent, UNDEFINED_EVENT_TYPE
from notification_service.client import NotificationClient
from notification_service.event_storage import MemoryEventStorage, DbEventStorage
from notification_service.master import NotificationMaster
from notification_service.service import NotificationService

from airflow.contrib.jobs.event_based_scheduler_job import EventBasedSchedulerJob, SchedulerEventWatcher, \
    EventBasedScheduler
from airflow.executors.local_executor import LocalExecutor
from airflow.models import TaskInstance, Message
from airflow.utils.mailbox import Mailbox
from airflow.utils.session import create_session, provide_session
from tests.test_utils import db


class TestEventBasedScheduler(unittest.TestCase):

    def setUp(self):
        db.clear_db_dags()
        db.clear_db_serialized_dags()
        db.clear_db_runs()
        db.clear_db_task_execution()
        db.clear_db_message()

        self.storage = MemoryEventStorage()
        self.master = NotificationMaster(NotificationService(self.storage), 50091)
        self.master.run()
        self.client = NotificationClient(server_uri="localhost:50091",
                                         default_namespace="test_namespace")

    def tearDown(self):
        self.master.stop()

    def test_event_based_scheduler(self):
        import time
        pid = os.fork()
        if pid == 0:
            try:
                ppid = os.fork()
                if ppid == 0:
                    # Fork twice to avoid the sleeping in main process block scheduler
                    self.start_scheduler()
            except Exception as e:
                print("Failed to execute task %s.", str(e))
        else:
            try:
                self.wait_for_task("event_based_scheduler_dag", "sleep_1000_secs", "running")
                print("Waiting for task starting")
                time.sleep(20)
                self.send_event("stop")
                self.wait_for_task("event_based_scheduler_dag", "sleep_1000_secs", "killed")
                tes: List[TaskExecution] = self.get_task_execution("event_based_scheduler_dag", "python_sleep")
                self.assertEqual(len(tes), 1)
                self.send_event("any_key")
                self.wait_for_task_execution("event_based_scheduler_dag", "python_sleep", 2)
                self.wait_for_task("event_based_scheduler_dag", "python_sleep", "running")
            finally:
                parent = psutil.Process(pid)
                for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                    child.kill()
                parent.kill()

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

    def start_scheduler(self):
        self.scheduler = EventBasedSchedulerJob(
            dag_directory="../../dags/test_event_based_scheduler.py",
            server_uri="localhost:50091",
            executor=LocalExecutor(3)
        )
        print("scheduler starting")

        self.scheduler.run()

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

    def tearDown(self):
        pass
