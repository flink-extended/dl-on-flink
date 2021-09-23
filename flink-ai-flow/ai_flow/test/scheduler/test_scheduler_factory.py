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
from typing import Text, List, Dict

from ai_flow.context.project_context import ProjectContext
from ai_flow.scheduler.scheduler_factory import SchedulerFactory
from ai_flow.plugin_interface.scheduler_interface import Scheduler
from ai_flow.workflow.workflow import Workflow
from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo, WorkflowExecutionInfo, WorkflowInfo


class UnitTestScheduler(Scheduler):
    def start_job_execution(self, job_name: Text, execution_id: Text) -> JobExecutionInfo:
        pass

    def stop_job_execution(self, job_name: Text, execution_id: Text) -> JobExecutionInfo:
        pass

    def restart_job_execution(self, job_name: Text, execution_id: Text) -> JobExecutionInfo:
        pass

    def get_job_executions(self, job_name: Text, execution_id: Text) -> List[JobExecutionInfo]:
        pass

    def list_job_executions(self, execution_id: Text) -> List[JobExecutionInfo]:
        pass

    def submit_workflow(self, workflow: Workflow, project_context: ProjectContext) -> WorkflowInfo:
        pass

    def pause_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def resume_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def start_new_workflow_execution(self, project_name: Text, workflow_name: Text) -> WorkflowExecutionInfo:
        pass

    def stop_all_workflow_execution(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        pass

    def stop_workflow_execution(self, execution_id: Text) -> WorkflowExecutionInfo:
        pass

    def get_workflow_execution(self, execution_id: Text) -> WorkflowExecutionInfo:
        pass

    def list_workflow_executions(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        pass


class TestSchedulerFactory(unittest.TestCase):

    def test_create_scheduler(self):
        print(Scheduler.__class__.__name__, Scheduler.__class__.__module__)
        class_name = 'ai_flow.test.scheduler.test_scheduler_factory.UnitTestScheduler'
        sc = SchedulerFactory.create_scheduler(class_name=class_name, config={})
        self.assertTrue(isinstance(sc, Scheduler))
