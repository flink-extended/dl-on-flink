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
import unittest

from notification_service.master import NotificationMaster

from notification_service.event_storage import MemoryEventStorage

from notification_service.service import NotificationService

from ai_flow.scheduler_service.service.config import SchedulerServiceConfig
from ai_flow.scheduler_service.service.workflow_event_manager import WorkflowEventManager


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
