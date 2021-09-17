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
import time
import unittest
from unittest import mock

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

    def tearDown(self) -> None:
        self.notification.stop()

    def test_start_stop(self):
        scheduler_service_config = SchedulerServiceConfig(self.config)
        workflow_event_manager = WorkflowEventManager('localhost:50051', 'sqlite:///:memory:', scheduler_service_config)
        workflow_event_manager.start()
        workflow_event_manager.stop()

    def test_workflow_event_manager_restart_event_processor(self):
        scheduler_service_config = SchedulerServiceConfig(self.config)
        workflow_event_manager = \
            WorkflowEventManager('localhost:50051', 'sqlite:///:memory:', scheduler_service_config)
        with mock.patch.object(workflow_event_manager, '_create_event_processor_process',
                               wraps=workflow_event_manager._create_event_processor_process) as create_process:
            previous_process = workflow_event_manager.event_processor_process
            workflow_event_manager.start()
            try:
                # kill the process
                previous_process.kill()
                time.sleep(5)
                create_process.assert_called_once()
                self.assertNotEqual(previous_process, workflow_event_manager.event_processor_process)
            finally:
                workflow_event_manager.stop()

    def test_notify_event_arrived(self):
        scheduler_service_config = SchedulerServiceConfig(self.config)
        workflow_event_manager = \
            WorkflowEventManager('localhost:50051', 'sqlite:///:memory:', scheduler_service_config)
        event = BaseEvent("k1", "v1")
        with mock.patch.object(workflow_event_manager, 'conn') as mock_conn:
            workflow_event_manager.notify_event_arrived(event)
            mock_conn.send.assert_called_once_with(event)

        with mock.patch.object(workflow_event_manager, 'conn') as mock_conn:
            mock_conn.send.side_effect = [Exception("Boom!"), Exception("Boom!"), None]
            workflow_event_manager.notify_event_arrived(event)
            self.assertEqual(3, mock_conn.send.call_count)


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
