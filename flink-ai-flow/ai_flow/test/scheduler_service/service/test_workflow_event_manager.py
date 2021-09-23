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
import time
import unittest
from unittest import mock

from ai_flow import WorkflowMeta
from notification_service.base_notification import BaseEvent

from notification_service.master import NotificationMaster

from notification_service.event_storage import MemoryEventStorage

from notification_service.service import NotificationService

from ai_flow.scheduler_service.service.config import SchedulerServiceConfig
from ai_flow.scheduler_service.service.workflow_event_manager import WorkflowEventManager, WorkflowEventWatcher


class TestWorkflowEventManager(unittest.TestCase):
    def setUp(self) -> None:
        self.notification = NotificationMaster(NotificationService(MemoryEventStorage()), 50051)
        self.notification.run()
        self.config = \
            {'scheduler':
                {
                    'scheduler_class': 'ai_flow_plugins.scheduler_plugins.airflow.airflow_scheduler.AirFlowScheduler',
                    'scheduler_config': {'airflow_deploy_path': '/tmp', 'notification_service_uri': 'localhost:50051'}
                }}
        scheduler_service_config = SchedulerServiceConfig(self.config)
        self.workflow_event_manager = \
            WorkflowEventManager('localhost:50051', 'sqlite:///aiflow.db', scheduler_service_config)

    def tearDown(self) -> None:
        if os.path.exists("aiflow.db"):
            os.remove("aiflow.db")
        self.notification.stop()

    def test_start_stop(self):
        self.workflow_event_manager.start()
        self.assertTrue(self.workflow_event_manager.event_processor_process.is_alive())
        self.assertIsNotNone(self.workflow_event_manager.listen_event_handler)
        self.assertTrue(self.workflow_event_manager.process_watcher_thread.is_alive())
        self.workflow_event_manager.stop()
        self.assertFalse(self.workflow_event_manager.event_processor_process.is_alive())
        self.assertFalse(self.workflow_event_manager.process_watcher_thread.is_alive())

    def test_workflow_event_manager_restart_event_processor(self):
        with mock.patch.object(self.workflow_event_manager, '_create_event_processor_process',
                               wraps=self.workflow_event_manager._create_event_processor_process) as create_process:
            previous_process = self.workflow_event_manager.event_processor_process
            self.workflow_event_manager.start()
            try:
                # kill the process
                previous_process.kill()
                time.sleep(10)
                create_process.assert_called_once()
                self.assertNotEqual(previous_process, self.workflow_event_manager.event_processor_process)
            finally:
                self.workflow_event_manager.stop()

    def test_notify_event_arrived(self):
        event = BaseEvent("k1", "v1")
        with mock.patch.object(self.workflow_event_manager, 'conn') as mock_conn:
            self.workflow_event_manager.notify_event_arrived(event)
            mock_conn.send.assert_called_once_with(event)

        with mock.patch.object(self.workflow_event_manager, 'conn') as mock_conn:
            mock_conn.send.side_effect = [Exception("Boom!"), Exception("Boom!"), None]
            self.workflow_event_manager.notify_event_arrived(event)
            self.assertEqual(3, mock_conn.send.call_count)

    def test__get_event_version_to_listen(self):
        with mock.patch.object(self.workflow_event_manager, 'store') as store:
            store.list_workflows.return_value = None
            self.assertIsNone(self.workflow_event_manager._get_event_version_to_listen())
            store.list_workflows.return_value = [WorkflowMeta('w1', 0)]
            self.assertIsNone(self.workflow_event_manager._get_event_version_to_listen())
            store.list_workflows.return_value = [WorkflowMeta('w1', 1, last_event_version=1),
                                                 WorkflowMeta('w2', 2, last_event_version=2),
                                                 WorkflowMeta('w1', 3, last_event_version=1),
                                                 WorkflowMeta('w1', 2, last_event_version=None)]
            self.assertEqual(1, self.workflow_event_manager._get_event_version_to_listen())

    def test__start_listen_events(self):
        with mock.patch.object(self.workflow_event_manager, '_get_event_version_to_listen') as get_version_method, \
                mock.patch.object(self.workflow_event_manager, 'notification_client') as notification_client:
            get_version_method.return_value = 10
            self.workflow_event_manager._start_listen_events()
            notification_client.start_listen_events.assert_called_once_with(mock.ANY, version=10)

    def test__stop_listen_events(self):
        with mock.patch.object(self.workflow_event_manager, 'listen_event_handler') as handler, \
                mock.patch.object(self.workflow_event_manager, 'notification_client') as notification_client:
            self.workflow_event_manager._stop_listen_events()
            handler.stop.assert_called_once()
            notification_client.stop_listen_events.assert_called_once()

    def test__restart_event_listener(self):
        with mock.patch.object(self.workflow_event_manager, '_start_listen_events') as start, \
                mock.patch.object(self.workflow_event_manager, '_stop_listen_events') as stop:
            self.workflow_event_manager._restart_event_listener()
            start.assert_called_once()
            stop.assert_called_once()


class TestWorkflowEventWatcher(unittest.TestCase):
    def test_process(self):
        workflow_event_manager = mock.MagicMock()
        watcher = WorkflowEventWatcher(workflow_event_manager)
        e1 = BaseEvent("k1", "v1")
        e2 = BaseEvent("k2", "v2")
        e3 = BaseEvent("k3", "v3")
        events = [e1, e2, e3]
        watcher.process(events)
        workflow_event_manager.notify_event_arrived.assert_has_calls([mock.call(e1), mock.call(e2), mock.call(e3)])
