#
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
import os
from typing import Text, List, Optional

from ai_flow.context.project_context import ProjectContext
from ai_flow.endpoint.server.server_runner import AIFlowServerRunner
from ai_flow.plugin_interface.scheduler_interface import Scheduler, JobExecutionInfo, WorkflowExecutionInfo, \
    WorkflowInfo
from ai_flow.workflow.workflow import Workflow


class MockScheduler(Scheduler):

    def delete_workflow(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def submit_workflow(self, workflow: Workflow, project_context: ProjectContext) -> WorkflowInfo:
        pass

    def pause_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def resume_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def start_new_workflow_execution(self, project_name: Text, workflow_name: Text) -> Optional[WorkflowExecutionInfo]:
        pass

    def stop_all_workflow_execution(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        pass

    def stop_workflow_execution(self, workflow_execution_id: Text) -> Optional[WorkflowExecutionInfo]:
        pass

    def get_workflow_execution(self, workflow_execution_id: Text) -> Optional[WorkflowExecutionInfo]:
        pass

    def list_workflow_executions(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
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


class TestServerRunner(unittest.TestCase):

    def test_server_start_stop(self):
        server_runner = AIFlowServerRunner(config_file=os.path.dirname(__file__) + '/master_config.yaml')
        server_runner.start(is_block=False)
        server_runner.stop()


if __name__ == '__main__':
    unittest.main()
