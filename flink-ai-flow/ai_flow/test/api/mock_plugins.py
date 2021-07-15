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
from typing import Text, Dict, Optional, List

from ai_flow.runtime.job_runtime_env import JobRuntimeEnv

from ai_flow.ai_graph.ai_graph import AISubGraph
from ai_flow.plugin_interface.job_plugin_interface import JobPluginFactory, register_job_plugin_factory, \
    JobHandle, JobController
from ai_flow.translator.translator import JobGenerator
from ai_flow.workflow.job import Job
from ai_flow.plugin_interface.blob_manager_interface import BlobManager
from ai_flow.plugin_interface.scheduler_interface import Scheduler, JobExecutionInfo, WorkflowExecutionInfo, \
    WorkflowInfo

from ai_flow.context.project_context import ProjectContext
from ai_flow.workflow.status import Status
from ai_flow.workflow.workflow import Workflow


class MockBlobManger(BlobManager):
    def __init__(self, config):
        super().__init__(config)

    def upload_project(self, workflow_snapshot_id: Text, project_path: Text) -> Text:
        return project_path

    def download_project(self, workflow_snapshot_id, remote_path: Text, local_path: Text = None) -> Text:
        return remote_path


class MockJobFactory(JobPluginFactory, JobGenerator, JobController):

    def get_result(self, job_handle: JobHandle, blocking: bool = True):
        pass

    def get_job_status(self, job_handle: JobHandle) -> Status:
        pass

    def get_job_generator(self) -> JobGenerator:
        return self

    def get_job_controller(self) -> JobController:
        return self

    def job_type(self) -> Text:
        return 'mock'

    def generate(self, sub_graph: AISubGraph, resource_dir: Text = None) -> Job:
        return Job(job_config=sub_graph.config)

    def submit_job(self, job: Job, job_runtime_env: JobRuntimeEnv) -> JobHandle:
        pass

    def stop_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv):
        pass

    def cleanup_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv):
        pass


class MockScheduler(Scheduler):

    def delete_workflow(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        return WorkflowInfo(namespace=project_name, workflow_name=workflow_name)

    def submit_workflow(self, workflow: Workflow, project_context: ProjectContext) -> WorkflowInfo:
        return WorkflowInfo(namespace=project_context.project_name, workflow_name=workflow.workflow_name)

    def pause_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        return WorkflowInfo(namespace=project_name, workflow_name=workflow_name)

    def resume_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        return WorkflowInfo(namespace=project_name, workflow_name=workflow_name)

    def start_new_workflow_execution(self, project_name: Text, workflow_name: Text) -> Optional[WorkflowExecutionInfo]:
        return WorkflowExecutionInfo(workflow_execution_id='1', status=Status.RUNNING)

    def stop_all_workflow_execution(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        return [WorkflowExecutionInfo(workflow_execution_id='1', status=Status.RUNNING),
                WorkflowExecutionInfo(workflow_execution_id='2', status=Status.RUNNING)]

    def stop_workflow_execution(self, workflow_execution_id: Text) -> Optional[WorkflowExecutionInfo]:
        return WorkflowExecutionInfo(workflow_execution_id='1', status=Status.RUNNING)

    def get_workflow_execution(self, workflow_execution_id: Text) -> Optional[WorkflowExecutionInfo]:
        return WorkflowExecutionInfo(workflow_execution_id='1', status=Status.RUNNING)

    def list_workflow_executions(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        return [WorkflowExecutionInfo(workflow_execution_id='1', status=Status.RUNNING),
                WorkflowExecutionInfo(workflow_execution_id='2', status=Status.RUNNING)]

    def start_job_execution(self, job_name: Text, workflow_execution_id: Text) -> JobExecutionInfo:
        return JobExecutionInfo(job_name='task_1', status=Status.RUNNING)

    def stop_job_execution(self, job_name: Text, workflow_execution_id: Text) -> JobExecutionInfo:
        return JobExecutionInfo(job_name='task_1', status=Status.RUNNING)

    def restart_job_execution(self, job_name: Text, workflow_execution_id: Text) -> JobExecutionInfo:
        return JobExecutionInfo(job_name='task_1', status=Status.RUNNING)

    def get_job_executions(self, job_name: Text, workflow_execution_id: Text) -> List[JobExecutionInfo]:
        return [JobExecutionInfo(job_name='task_1', status=Status.RUNNING)]

    def list_job_executions(self, workflow_execution_id: Text) -> List[JobExecutionInfo]:
        return [JobExecutionInfo(job_name='task_1', status=Status.RUNNING),
                JobExecutionInfo(job_name='task_2', status=Status.RUNNING)]


register_job_plugin_factory(MockJobFactory())
