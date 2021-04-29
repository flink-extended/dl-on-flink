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
from tempfile import NamedTemporaryFile
from typing import Dict, Text, List

from airflow.models.dag import DagTag, DagModel
from airflow.models.dagcode import DagCode
from airflow.models.serialized_dag import SerializedDagModel
from airflow.utils.db import create_session

from ai_flow.airflow.dag_generator import DAGGenerator
from ai_flow.project.project_description import ProjectDesc
from ai_flow.scheduler.scheduler_interface import AbstractScheduler, SchedulerConfig
from ai_flow.workflow.workflow import Workflow, WorkflowInfo, JobInfo, WorkflowExecutionInfo


class AirFlowScheduler(AbstractScheduler):

    def __init__(self, config: SchedulerConfig):
        super().__init__(config)
        self.dag_generator = DAGGenerator()

    def submit_workflow(self, workflow: Workflow, project_desc: ProjectDesc, args: Dict = None) -> WorkflowInfo:
        code_text = self.dag_generator.generator(workflow, workflow.workflow_name, args)
        deploy_path = self.config.properties.get('airflow_deploy_path')
        if deploy_path is None:
            raise Exception("airflow_deploy_path config not set!")
        airflow_file_path = os.path.join(deploy_path, workflow.workflow_name + '.py')
        if os.path.exists(airflow_file_path):
            os.remove(airflow_file_path)
        with NamedTemporaryFile(mode='w+t', prefix=workflow.workflow_name, suffix='.py', dir='/tmp', delete=False) as f:
            f.write(code_text)
        os.rename(f.name, airflow_file_path)
        return WorkflowInfo(workflow_name=workflow.workflow_name)

    def delete_workflow(self, workflow_name: Text, project_name: Text) -> WorkflowInfo:
        deploy_path = self.config.properties.get('airflow_deploy_path')
        if deploy_path is None:
            raise Exception("airflow_deploy_path config not set!")
        airflow_file_path = os.path.join(deploy_path, workflow_name + '.py')
        if os.path.exists(airflow_file_path):
            os.remove(airflow_file_path)

        # todo stop all workflow executions
        with create_session() as session:
            session.query(DagTag).filter(DagTag.dag_id == workflow_name).delete()
            session.query(DagModel).filter(DagModel.dag_id == workflow_name).delete()
            session.query(DagCode).filter(DagCode.dag_id == workflow_name).delete()
            session.query(SerializedDagModel).filter(SerializedDagModel.dag_id == workflow_name).delete()
        return WorkflowInfo(workflow_name=workflow_name)

    def pause_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def resume_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def get_workflow(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        pass

    def list_workflows(self, project_name: Text, workflow_name: Text) -> List[WorkflowInfo]:
        pass

    def start_new_workflow_execution(self, project_name: Text, workflow_name: Text) -> WorkflowExecutionInfo:
        pass

    def kill_all_workflow_execution(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        pass

    def kill_workflow_execution(self, execution_id: Text) -> WorkflowExecutionInfo:
        pass

    def get_workflow_execution(self, execution_id: Text) -> WorkflowExecutionInfo:
        pass

    def list_workflow_execution(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        pass

    def start_job(self, job_name: Text, execution_id: Text) -> JobInfo:
        pass

    def stop_job(self, job_name: Text, execution_id: Text) -> JobInfo:
        pass

    def restart_job(self, job_name: Text, execution_id: Text) -> JobInfo:
        pass

    def get_job(self, job_name: Text, execution_id: Text) -> JobInfo:
        pass

    def list_job(self, execution_id: Text) -> List[JobInfo]:
        pass
