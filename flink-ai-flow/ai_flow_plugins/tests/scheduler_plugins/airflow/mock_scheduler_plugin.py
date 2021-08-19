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
from typing import Text, List, Optional, Dict

from ai_flow.plugin_interface.scheduler_interface import Scheduler, JobExecutionInfo, WorkflowExecutionInfo, \
    WorkflowInfo
from ai_flow.context.project_context import ProjectContext
from ai_flow.workflow.workflow import Workflow
from ai_flow.workflow.status import Status
from ai_flow_plugins.scheduler_plugins.airflow.dag_generator import DAGGenerator


class MockScheduler(Scheduler):

    def __init__(self, config: Dict):
        super().__init__(config)
        self.dag_generator = DAGGenerator()

    def stop_workflow_execution_by_context(self, workflow_name: Text, context: Text) -> Optional[WorkflowExecutionInfo]:
        workflow_info = WorkflowInfo(workflow_name='workflow_name', namespace='project_name')
        workflow_execution_info = WorkflowExecutionInfo(workflow_execution_id='1',
                                                        workflow_info=workflow_info,
                                                        status=Status.KILLED,
                                                        start_date=str(int(time.time() * 1000)))
        return workflow_execution_info

    def submit_workflow(self, workflow: Workflow, project_context: ProjectContext, args: Dict = None) -> WorkflowInfo:
        code_text = self.dag_generator.generate(workflow=workflow,
                                                project_name=project_context.project_name)
        return WorkflowInfo(workflow_name=workflow.workflow_name, properties={'code': code_text})

    def delete_workflow(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        return WorkflowInfo(workflow_name=workflow_name, namespace=project_name)

    def pause_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        return WorkflowInfo(workflow_name=workflow_name, namespace=project_name)

    def resume_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        return WorkflowInfo(workflow_name=workflow_name, namespace=project_name)

    def start_new_workflow_execution(self, project_name: Text, workflow_name: Text, context: Text = None) \
            -> Optional[WorkflowExecutionInfo]:
        workflow_info = WorkflowInfo(workflow_name=workflow_name, namespace=project_name)
        workflow_execution_info = WorkflowExecutionInfo(workflow_execution_id='1',
                                                        workflow_info=workflow_info,
                                                        status=Status.RUNNING,
                                                        start_date=str(int(time.time()*1000)))
        return workflow_execution_info

    def stop_all_workflow_execution(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        workflow_info = WorkflowInfo(workflow_name=workflow_name, namespace=project_name)
        workflow_execution_info = WorkflowExecutionInfo(workflow_execution_id='1',
                                                        workflow_info=workflow_info,
                                                        status=Status.KILLED,
                                                        start_date=str(int(time.time() * 1000)))
        return [workflow_execution_info]

    def stop_workflow_execution(self, execution_id: Text) -> Optional[WorkflowExecutionInfo]:
        workflow_info = WorkflowInfo(workflow_name='workflow_name', namespace='project_name')
        workflow_execution_info = WorkflowExecutionInfo(workflow_execution_id='1',
                                                        workflow_info=workflow_info,
                                                        status=Status.KILLED,
                                                        start_date=str(int(time.time() * 1000)))
        return workflow_execution_info

    def get_workflow_execution(self, execution_id: Text) -> Optional[WorkflowExecutionInfo]:
        workflow_info = WorkflowInfo(workflow_name='workflow_name', namespace='project_name')
        workflow_execution_info = WorkflowExecutionInfo(workflow_execution_id='1',
                                                        workflow_info=workflow_info,
                                                        status=Status.KILLED,
                                                        start_date=str(int(time.time() * 1000)),
                                                        end_date=str(int(time.time() * 1000)))
        return workflow_execution_info

    def list_workflow_executions(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        workflow_info = WorkflowInfo(workflow_name='workflow_name', namespace='project_name')
        workflow_execution_info = WorkflowExecutionInfo(workflow_execution_id='1',
                                                        workflow_info=workflow_info,
                                                        status=Status.KILLED,
                                                        start_date=str(int(time.time() * 1000)))
        return [workflow_execution_info]

    def start_job_execution(self, job_name: Text, execution_id: Text) -> JobExecutionInfo:
        workflow_info = WorkflowInfo(workflow_name='workflow_name', namespace='project_name')
        workflow_execution_info = WorkflowExecutionInfo(workflow_execution_id='1',
                                                        workflow_info=workflow_info,
                                                        status=Status.KILLED,
                                                        start_date=str(int(time.time() * 1000)))
        job_execution_info: JobExecutionInfo = JobExecutionInfo(job_name=job_name,
                                                                status=Status.RUNNING,
                                                                workflow_execution=workflow_execution_info,
                                                                start_date=str(int(time.time() * 1000))
                                                                )
        return job_execution_info

    def stop_job_execution(self, job_name: Text, execution_id: Text) -> JobExecutionInfo:
        workflow_info = WorkflowInfo(workflow_name='workflow_name', namespace='project_name')
        workflow_execution_info = WorkflowExecutionInfo(workflow_execution_id='1',
                                                        workflow_info=workflow_info,
                                                        status=Status.KILLED,
                                                        start_date=str(int(time.time() * 1000)))
        job_execution_info: JobExecutionInfo = JobExecutionInfo(job_name=job_name,
                                                                status=Status.KILLED,
                                                                workflow_execution=workflow_execution_info,
                                                                start_date=str(int(time.time() * 1000))
                                                                )
        return job_execution_info

    def restart_job_execution(self, job_name: Text, execution_id: Text) -> JobExecutionInfo:
        workflow_info = WorkflowInfo(workflow_name='workflow_name', namespace='project_name')
        workflow_execution_info = WorkflowExecutionInfo(workflow_execution_id='1',
                                                        workflow_info=workflow_info,
                                                        status=Status.KILLED,
                                                        start_date=str(int(time.time() * 1000)))
        job_execution_info: JobExecutionInfo = JobExecutionInfo(job_name=job_name,
                                                                status=Status.RUNNING,
                                                                workflow_execution=workflow_execution_info,
                                                                start_date=str(int(time.time() * 1000))
                                                                )
        return job_execution_info

    def get_job_executions(self, job_name: Text, execution_id: Text) -> List[JobExecutionInfo]:
        workflow_info = WorkflowInfo(workflow_name='workflow_name', namespace='project_name')
        workflow_execution_info = WorkflowExecutionInfo(workflow_execution_id='1',
                                                        workflow_info=workflow_info,
                                                        status=Status.KILLED,
                                                        start_date=str(int(time.time() * 1000)))
        job_execution_info: JobExecutionInfo = JobExecutionInfo(job_name=job_name,
                                                                status=Status.RUNNING,
                                                                workflow_execution=workflow_execution_info,
                                                                start_date=str(int(time.time() * 1000)),
                                                                end_date=str(int(time.time() * 1000))
                                                                )
        return [job_execution_info]

    def list_job_executions(self, execution_id: Text) -> List[JobExecutionInfo]:
        workflow_info = WorkflowInfo(workflow_name='workflow_name', namespace='project_name')
        workflow_execution_info = WorkflowExecutionInfo(workflow_execution_id='1',
                                                        workflow_info=workflow_info,
                                                        status=Status.KILLED,
                                                        start_date=str(int(time.time() * 1000)))
        job_execution_info: JobExecutionInfo = JobExecutionInfo(job_name='job_name',
                                                                status=Status.RUNNING,
                                                                workflow_execution=workflow_execution_info,
                                                                start_date=str(int(time.time() * 1000))
                                                                )
        return [job_execution_info]