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
import mock
import os
import unittest

from ai_flow.util import json_utils
from ai_flow.workflow.control_edge import MeetAllEventCondition, MeetAnyEventCondition
from typing import Text, List, Optional

from ai_flow.scheduler_service.service.service import SchedulerServiceConfig
from ai_flow.workflow.status import Status
from ai_flow.protobuf.message_pb2 import StateProto

from ai_flow.endpoint.client.scheduler_client import SchedulerClient
from ai_flow.endpoint.server.server import AIFlowServer
from ai_flow.context.project_context import ProjectContext
from ai_flow.plugin_interface.scheduler_interface import Scheduler
from ai_flow.workflow.workflow import Workflow
from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo, WorkflowExecutionInfo, WorkflowInfo

_SQLITE_DB_FILE = 'aiflow.db'
_SQLITE_DB_URI = '%s%s' % ('sqlite:///', _SQLITE_DB_FILE)
_PORT = '50051'


class MockScheduler(Scheduler):
    def stop_workflow_execution_by_context(self, workflow_name: Text, context: Text) -> Optional[WorkflowExecutionInfo]:
        pass

    def delete_workflow(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def start_job_execution(self, job_name: Text, workflow_execution_id: Text) -> JobExecutionInfo:
        pass

    def stop_job_execution(self, job_name: Text, workflow_execution_id: Text) -> JobExecutionInfo:
        pass

    def restart_job_execution(self, job_name: Text, workflow_execution_id: Text) -> JobExecutionInfo:
        pass

    def get_job_executions(self, job_name: Text, workflow_execution_id: Text) -> List[JobExecutionInfo]:
        pass

    def list_job_executions(self, workflow_execution_id: Text) -> List[JobExecutionInfo]:
        pass

    def submit_workflow(self, workflow: Workflow, project_context: ProjectContext) -> WorkflowInfo:
        pass

    def pause_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def resume_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def start_new_workflow_execution(self, project_name: Text, workflow_name: Text, context: Text = None) \
            -> WorkflowExecutionInfo:
        pass

    def stop_all_workflow_execution(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        pass

    def stop_workflow_execution(self, workflow_execution_id: Text) -> WorkflowExecutionInfo:
        pass

    def get_workflow_execution(self, workflow_execution_id: Text) -> WorkflowExecutionInfo:
        pass

    def list_workflow_executions(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        pass


SCHEDULER_CLASS = 'ai_flow.test.scheduler.test_scheduler_service.MockScheduler'


class TestSchedulerService(unittest.TestCase):
    def setUp(self):
        raw_config = {
            'scheduler': {
                'scheduler_class': SCHEDULER_CLASS,
            }
        }
        config = SchedulerServiceConfig(raw_config)
        if os.path.exists(_SQLITE_DB_FILE):
            os.remove(_SQLITE_DB_FILE)
        self.server = AIFlowServer(store_uri=_SQLITE_DB_URI, port=_PORT,
                                   start_default_notification=False,
                                   start_meta_service=False,
                                   start_metric_service=False,
                                   start_model_center_service=False,
                                   start_scheduler_service=True,
                                   scheduler_service_config=config)
        self.server.run()

    def tearDown(self):
        self.server.stop()
        if os.path.exists(_SQLITE_DB_FILE):
            os.remove(_SQLITE_DB_FILE)

    def test_submit_workflow(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            instance = mockScheduler.return_value
            instance.submit_workflow.return_value = WorkflowInfo(workflow_name='test_workflow')
            client = SchedulerClient("localhost:{}".format(_PORT))
            with self.assertRaises(Exception) as context:
                workflow = client.submit_workflow_to_scheduler(namespace='namespace', workflow_name='test_workflow',
                                                               workflow_json='')
            self.assertTrue('workflow json is empty' in str(context.exception))

    def test_pause_workflow(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            instance = mockScheduler.return_value
            self.server.scheduler_service._scheduler = instance

            instance.pause_workflow_scheduling.return_value = WorkflowInfo(workflow_name='test_workflow')
            client = SchedulerClient("localhost:{}".format(_PORT))
            workflow = client.pause_workflow_scheduling(namespace='namespace', workflow_name='test_workflow')
            self.assertTrue('test_workflow', workflow.name)

    def test_resume_workflow(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            instance = mockScheduler.return_value
            self.server.scheduler_service._scheduler = instance

            instance.resume_workflow_scheduling.return_value = WorkflowInfo(workflow_name='test_workflow')
            client = SchedulerClient("localhost:{}".format(_PORT))
            workflow = client.resume_workflow_scheduling(namespace='namespace', workflow_name='test_workflow')
            self.assertTrue('test_workflow', workflow.name)

    def test_start_new_workflow_execution(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            instance = mockScheduler.return_value
            self.server.scheduler_service._scheduler = instance

            instance.start_new_workflow_execution.return_value \
                = WorkflowExecutionInfo(workflow_execution_id='id', status=Status.INIT)
            client = SchedulerClient("localhost:{}".format(_PORT))
            workflow_execution = client.start_new_workflow_execution(namespace='namespace',
                                                                     workflow_name='test_workflow')
            args, kwargs = instance.start_new_workflow_execution.call_args
            self.assertEqual(('namespace', 'test_workflow', None), args)
            self.assertEqual('id', workflow_execution.execution_id)
            self.assertEqual(StateProto.INIT, workflow_execution.execution_state)
            self.assertFalse(workflow_execution.HasField('context'))

    def test_start_new_workflow_execution_with_context(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            self.server.scheduler_service._scheduler = mockScheduler

            mockScheduler.start_new_workflow_execution.return_value \
                = WorkflowExecutionInfo(workflow_execution_id='id', status=Status.INIT, context='test_context')
            client = SchedulerClient("localhost:{}".format(_PORT))
            workflow_execution = client.start_new_workflow_execution(namespace='namespace',
                                                                     workflow_name='test_workflow',
                                                                     context='test_context')
            args, kwargs = mockScheduler.start_new_workflow_execution.call_args
            self.assertEqual(('namespace', 'test_workflow', 'test_context'), args)
            self.assertEqual('id', workflow_execution.execution_id)
            self.assertEqual(StateProto.INIT, workflow_execution.execution_state)
            self.assertEqual('test_context', workflow_execution.context.value)

    def test_start_new_workflow_execution_on_event(self):
        client = SchedulerClient("localhost:{}".format(_PORT))
        c1 = MeetAllEventCondition().add_event('k1', 'v1')
        c2 = MeetAnyEventCondition().add_event('k2', 'v2')
        workflow_proto = client.start_new_workflow_execution_on_events(namespace='namespace',
                                                                      workflow_name='test_workflow',
                                                                      event_conditions=[c1, c2])
        self.assertEqual('namespace', workflow_proto.namespace)
        self.assertEqual('test_workflow', workflow_proto.name)
        self.assertListEqual([c1, c2], json_utils.loads(workflow_proto.properties['event_conditions_json']))

    def test_stop_workflow_execution_on_event(self):
        client = SchedulerClient("localhost:{}".format(_PORT))
        c1 = MeetAllEventCondition().add_event('k1', 'v1')
        c2 = MeetAnyEventCondition().add_event('k2', 'v2')
        workflow_proto = client.stop_workflow_execution_on_events(namespace='namespace',
                                                                 workflow_name='test_workflow',
                                                                 event_conditions=[c1, c2])
        self.assertEqual('namespace', workflow_proto.namespace)
        self.assertEqual('test_workflow', workflow_proto.name)
        self.assertListEqual([c1, c2], json_utils.loads(workflow_proto.properties['event_conditions_json']))

    def test_kill_all_workflow_execution(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            instance = mockScheduler.return_value
            self.server.scheduler_service._scheduler = instance

            instance.stop_all_workflow_execution.return_value \
                = [WorkflowExecutionInfo(workflow_execution_id='id_1', status=Status.INIT),
                   WorkflowExecutionInfo(workflow_execution_id='id_2', status=Status.INIT)]
            client = SchedulerClient("localhost:{}".format(_PORT))
            workflow_execution_list = client.kill_all_workflow_executions(namespace='namespace',
                                                                          workflow_name='test_workflow')
            self.assertEqual(2, len(workflow_execution_list))

    def test_kill_workflow_execution(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            instance = mockScheduler.return_value
            self.server.scheduler_service._scheduler = instance

            instance.stop_workflow_execution.return_value \
                = WorkflowExecutionInfo(workflow_execution_id='id', status=Status.RUNNING)
            client = SchedulerClient("localhost:{}".format(_PORT))
            workflow_execution = client.kill_workflow_execution(execution_id='id')
            self.assertEqual('id', workflow_execution.execution_id)
            self.assertEqual(StateProto.RUNNING, workflow_execution.execution_state)

    def test_get_workflow_execution(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            instance = mockScheduler.return_value
            self.server.scheduler_service._scheduler = instance

            instance.get_workflow_execution.return_value \
                = WorkflowExecutionInfo(workflow_execution_id='id', status=Status.INIT)
            client = SchedulerClient("localhost:{}".format(_PORT))
            workflow_execution = client.get_workflow_execution(execution_id='id')
            self.assertEqual('id', workflow_execution.execution_id)
            self.assertEqual(StateProto.INIT, workflow_execution.execution_state)

    def test_list_workflow_executions(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            instance = mockScheduler.return_value
            self.server.scheduler_service._scheduler = instance

            instance.list_workflow_executions.return_value \
                = [WorkflowExecutionInfo(workflow_execution_id='id_1', status=Status.INIT),
                   WorkflowExecutionInfo(workflow_execution_id='id_2', status=Status.INIT)]
            client = SchedulerClient("localhost:{}".format(_PORT))
            workflow_execution_list = client.list_workflow_executions(namespace='namespace',
                                                                      workflow_name='test_workflow')
            self.assertEqual(2, len(workflow_execution_list))

    def test_start_job(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            instance = mockScheduler.return_value
            self.server.scheduler_service._scheduler = instance

            instance.start_job_execution.return_value \
                = JobExecutionInfo(job_name='job_name',
                                   status=Status.RUNNING,
                                   workflow_execution=WorkflowExecutionInfo(workflow_execution_id='id',
                                                                            status=Status.INIT))
            client = SchedulerClient("localhost:{}".format(_PORT))
            job = client.start_job(job_name='job_name', execution_id='id')
            self.assertEqual('job_name', job.name)
            self.assertEqual(StateProto.RUNNING, job.job_state)
            self.assertEqual('id', job.workflow_execution.execution_id)
            self.assertEqual(StateProto.INIT, job.workflow_execution.execution_state)

    def test_stop_job(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            instance = mockScheduler.return_value
            self.server.scheduler_service._scheduler = instance

            instance.stop_job_execution.return_value \
                = JobExecutionInfo(job_name='job_name',
                                   status=Status.RUNNING,
                                   workflow_execution=WorkflowExecutionInfo(workflow_execution_id='id',
                                                                            status=Status.INIT))
            client = SchedulerClient("localhost:{}".format(_PORT))
            job = client.stop_job(job_name='job_name', execution_id='id')
            self.assertEqual('job_name', job.name)
            self.assertEqual(StateProto.RUNNING, job.job_state)
            self.assertEqual('id', job.workflow_execution.execution_id)
            self.assertEqual(StateProto.INIT, job.workflow_execution.execution_state)

    def test_restart_job(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            instance = mockScheduler.return_value
            self.server.scheduler_service._scheduler = instance

            instance.restart_job_execution.return_value \
                = JobExecutionInfo(job_name='job_name',
                                   status=Status.RUNNING,
                                   workflow_execution=WorkflowExecutionInfo(workflow_execution_id='id',
                                                                            status=Status.INIT))
            client = SchedulerClient("localhost:{}".format(_PORT))
            job = client.restart_job(job_name='job_name', execution_id='id')
            self.assertEqual('job_name', job.name)
            self.assertEqual(StateProto.RUNNING, job.job_state)
            self.assertEqual('id', job.workflow_execution.execution_id)
            self.assertEqual(StateProto.INIT, job.workflow_execution.execution_state)

    def test_get_job(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            instance = mockScheduler.return_value
            self.server.scheduler_service._scheduler = instance

            instance.get_job_executions.return_value \
                = [JobExecutionInfo(job_name='job_name',
                                    status=Status.RUNNING,
                                    workflow_execution=WorkflowExecutionInfo(workflow_execution_id='id',
                                                                             status=Status.INIT))]
            client = SchedulerClient("localhost:{}".format(_PORT))
            job = client.get_job(job_name='job_name', execution_id='id')
            self.assertEqual('job_name', job.name)
            self.assertEqual(StateProto.RUNNING, job.job_state)
            self.assertEqual('id', job.workflow_execution.execution_id)
            self.assertEqual(StateProto.INIT, job.workflow_execution.execution_state)

    def test_list_jobs(self):
        with mock.patch(SCHEDULER_CLASS) as mockScheduler:
            instance = mockScheduler.return_value
            self.server.scheduler_service._scheduler = instance

            instance.list_job_executions.return_value \
                = [JobExecutionInfo(job_name='job_name_1',
                                    status=Status.RUNNING,
                                    workflow_execution=WorkflowExecutionInfo(workflow_execution_id='id',
                                                                             status=Status.INIT)),
                   JobExecutionInfo(job_name='job_name_2',
                                    status=Status.RUNNING,
                                    workflow_execution=WorkflowExecutionInfo(workflow_execution_id='id',
                                                                             status=Status.INIT))]
            client = SchedulerClient("localhost:{}".format(_PORT))
            job_list = client.list_jobs(execution_id='id')
            self.assertEqual(2, len(job_list))
