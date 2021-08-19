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
from typing import Text, List, Optional, Dict

from ai_flow.common.module_load import import_string
from ai_flow.plugin_interface.job_plugin_interface import JobController, JobHandle
from ai_flow.plugin_interface.scheduler_interface import Scheduler, JobExecutionInfo, WorkflowExecutionInfo, \
    WorkflowInfo
from ai_flow.context.project_context import ProjectContext
from ai_flow.runtime.job_runtime_env import JobRuntimeEnv
from ai_flow.runtime.job_runtime_util import prepare_job_runtime_env
from ai_flow.workflow.status import Status
from ai_flow.workflow.workflow import Workflow, WorkflowPropertyKeys


class SingleJobScheduler(Scheduler):

    def __init__(self, config: Dict):
        super().__init__(config)
        self.workflow: Workflow = None
        self.project_context: ProjectContext = None
        self.job_controller: JobController = None
        self.job_handler: JobHandle = None
        self.job_runtime_env: JobRuntimeEnv = None

    def submit_workflow(self, workflow: Workflow, project_context: ProjectContext) -> WorkflowInfo:
        self.workflow = workflow
        self.project_context = project_context
        return WorkflowInfo(workflow_name=workflow.workflow_name)

    def stop_workflow_execution_by_context(self, workflow_name: Text, context: Text) -> Optional[WorkflowExecutionInfo]:
        pass

    def delete_workflow(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def pause_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def resume_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def start_new_workflow_execution(self, project_name: Text, workflow_name: Text, context: Text = None) \
            -> Optional[WorkflowExecutionInfo]:
        pass

    def stop_all_workflow_execution(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        pass

    def stop_workflow_execution(self, execution_id: Text) -> Optional[WorkflowExecutionInfo]:
        pass

    def get_workflow_execution(self, execution_id: Text) -> Optional[WorkflowExecutionInfo]:
        pass

    def list_workflow_executions(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        pass

    def start_job_execution(self, job_name: Text, execution_id: Text) -> JobExecutionInfo:
        job = self.workflow.jobs[job_name]
        plugins = self.workflow.properties.get(WorkflowPropertyKeys.JOB_PLUGINS)
        module, name = plugins.get(job.job_config.job_type)
        class_object = import_string('{}.{}'.format(module, name))
        self.job_controller: JobController = class_object()
        job_execution_info = JobExecutionInfo(job_execution_id='1', job_name=job_name,
                                              workflow_execution
                                              =WorkflowExecutionInfo(workflow_execution_id='1',
                                                                     workflow_info=WorkflowInfo(
                                                                         workflow_name=self.workflow.workflow_name)))
        self.job_runtime_env: JobRuntimeEnv = prepare_job_runtime_env(
            root_working_dir=self.project_context.project_path + '/temp',
            workflow_snapshot_id=self.workflow.workflow_snapshot_id,
            workflow_name=self.workflow.workflow_name,
            job_execution_info=job_execution_info,
            project_context=self.project_context)

        self.job_handler = self.job_controller.submit_job(job=job, job_runtime_env=self.job_runtime_env)
        return job_execution_info

    def stop_job_execution(self, job_name: Text, execution_id: Text) -> JobExecutionInfo:
        self.job_controller.stop_job(self.job_handler, self.job_runtime_env)
        self.job_controller.cleanup_job(self.job_handler, self.job_runtime_env)
        return JobExecutionInfo(job_execution_id='1', job_name=job_name)

    def restart_job_execution(self, job_name: Text, execution_id: Text) -> JobExecutionInfo:
        return JobExecutionInfo(job_execution_id='1', job_name=job_name)

    def get_job_executions(self, job_name: Text, execution_id: Text) -> List[JobExecutionInfo]:
        try:
            result = self.job_controller.get_result(job_handle=self.job_handler)
            print(result)
            self.job_controller.cleanup_job(self.job_handler, self.job_runtime_env)
        except Exception as e:
            return [JobExecutionInfo(job_execution_id='1', job_name=job_name,
                                     status=Status.FAILED, properties={'err': str(e)})]
        return [JobExecutionInfo(job_execution_id='1', job_name=job_name, status=Status.FINISHED)]

    def list_job_executions(self, execution_id: Text) -> List[JobExecutionInfo]:
        pass
