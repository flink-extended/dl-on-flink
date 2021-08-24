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
#
import unittest
from typing import List

from notification_service.base_notification import EventWatcher, BaseEvent
from notification_service.client import NotificationClient
from notification_service.event_storage import MemoryEventStorage
from notification_service.master import NotificationMaster
from notification_service.service import NotificationService
from airflow.contrib.jobs.scheduler_client import EventSchedulerClient, ExecutionContext
from airflow.events.scheduler_events import SchedulerInnerEventType
from airflow.executors.scheduling_action import SchedulingAction

PORT = 50053


class MockScheduler(object):
    def __init__(self):
        self.client = NotificationClient(server_uri="localhost:{}".format(PORT),
                                         default_namespace="scheduler")

    def start(self, watcher):
        self.client.start_listen_events(watcher=watcher)

    def stop(self):
        self.client.stop_listen_events()


class PassWatcher(EventWatcher):
    def process(self, events: List[BaseEvent]):
        pass


class TestSchedulerClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.storage = MemoryEventStorage()
        cls.master = NotificationMaster(NotificationService(cls.storage), PORT)
        cls.master.run()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.master.stop()

    def setUp(self) -> None:
        self.client = EventSchedulerClient(ns_client=NotificationClient(server_uri="localhost:{}".format(PORT),
                                                                        default_namespace="test_namespace"))
        self.scheduler = MockScheduler()

    def tearDown(self) -> None:
        self.scheduler.stop()

    def test_parse_dag(self):
        class W(EventWatcher):
            def process(self, events: List[BaseEvent]):
                s_client = NotificationClient(server_uri="localhost:{}".format(PORT),
                                              default_namespace="scheduler")
                s_client.send_event(BaseEvent(key=events[0].key, value='',
                                              event_type=SchedulerInnerEventType.PARSE_DAG_RESPONSE.value,
                                              namespace='scheduler'))

        self.scheduler.start(watcher=W())
        result = self.client.trigger_parse_dag(file_path='/test')
        self.assertTrue(result)

    def test_parse_dag_timeout(self):
        self.scheduler.start(watcher=PassWatcher())
        with self.assertRaises(TimeoutError) as context:
            result = self.client.trigger_parse_dag(file_path='/test', timeout=1)
        self.assertTrue('Get response timeout' in str(context.exception))

    def test_schedule_dag(self):
        class W(EventWatcher):
            def process(self, events: List[BaseEvent]):
                s_client = NotificationClient(server_uri="localhost:{}".format(PORT),
                                              default_namespace="scheduler")
                s_client.send_event(BaseEvent(key=events[0].key, value='1',
                                              event_type=SchedulerInnerEventType.RESPONSE.value,
                                              namespace='scheduler'))

        self.scheduler.start(watcher=W())
        result = self.client.schedule_dag(dag_id='1', context='')
        self.assertEqual('1', result.dagrun_id)

    def test_schedule_dag_timeout(self):
        self.scheduler.start(watcher=PassWatcher())
        with self.assertRaises(TimeoutError) as context:
            result = self.client.schedule_dag(dag_id='1', context='', timeout=1)
        self.assertTrue('Get response timeout' in str(context.exception))

    def test_stop_dag_run(self):
        class W(EventWatcher):
            def process(self, events: List[BaseEvent]):
                s_client = NotificationClient(server_uri="localhost:{}".format(PORT),
                                              default_namespace="scheduler")
                s_client.send_event(BaseEvent(key=events[0].key, value='1',
                                              event_type=SchedulerInnerEventType.RESPONSE.value,
                                              namespace='scheduler'))

        self.scheduler.start(watcher=W())
        result = self.client.stop_dag_run(dag_id='1', context=ExecutionContext(dagrun_id='1'))
        self.assertEqual('1', result.dagrun_id)

    def test_stop_dag_run_timeout(self):
        self.scheduler.start(watcher=PassWatcher())
        with self.assertRaises(TimeoutError) as context:
            result = self.client.stop_dag_run(dag_id='1', context=ExecutionContext(dagrun_id='1'), timeout=1)
        self.assertTrue('Get response timeout' in str(context.exception))

    def test_schedule_task(self):
        class W(EventWatcher):
            def process(self, events: List[BaseEvent]):
                s_client = NotificationClient(server_uri="localhost:{}".format(PORT),
                                              default_namespace="scheduler")
                s_client.send_event(BaseEvent(key=events[0].key, value='1',
                                              event_type=SchedulerInnerEventType.RESPONSE.value,
                                              namespace='scheduler'))

        self.scheduler.start(watcher=W())
        result = self.client.schedule_task(dag_id='1', task_id='t_1',
                                           action=SchedulingAction.START,
                                           context=ExecutionContext(dagrun_id='1'))
        self.assertEqual('1', result.dagrun_id)

    def test_schedule_task_timeout(self):
        self.scheduler.start(watcher=PassWatcher())
        with self.assertRaises(TimeoutError) as context:
            result = self.client.schedule_task(dag_id='1', task_id='t_1',
                                               action=SchedulingAction.START,
                                               context=ExecutionContext(dagrun_id='1'),
                                               timeout=1)
        self.assertTrue('Get response timeout' in str(context.exception))


if __name__ == '__main__':
    unittest.main()
