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
import inspect
import os
import sys
import tempfile
import time
from typing import Optional, Tuple, Text
from tempfile import NamedTemporaryFile
from ai_flow.airflow.dag_generator import DAGGenerator
from ai_flow.api.configuration import project_config
from ai_flow.common import json_utils
from ai_flow.common.scheduler_type import SchedulerType
from ai_flow.graph.graph import default_graph, AIGraph
from ai_flow.project.blob_manager import BlobManagerFactory
from ai_flow.project.project_description import get_project_description_from, ProjectDesc
from ai_flow.project.project_util import file_path_to_absolute_module
from ai_flow.rest_endpoint.service.client.aiflow_client import AIFlowClient
from ai_flow.translator.base_translator import get_default_translator
from ai_flow.workflow.workflow import Workflow
from ai_flow.api.ai_flow_context import default_af_job_context
from ai_flow.api.execution import AirflowOperation


class Project(object):
    """
    The Project which covers the ai flow life cycle.
    """

    def __init__(self) -> None:
        super().__init__()
        self.translator = get_default_translator()
        self.client = None
        self.project_desc: ProjectDesc = None

    def get_client(self) -> Optional[AIFlowClient]:
        """
        Get the ai flow client.

        :return: AIFlowClient.
        """
        if self.client is None:
            self.client = AIFlowClient(server_uri=project_config().get_master_uri())
        return self.client

    def generate_workflow(self, ai_graph: AIGraph) -> Workflow:
        """
        Generate the workflow based on the ai graph.

        :param ai_graph: The ai graph constructed from project.
        :return: Workflow.
        """
        workflow = self.translator.translate(ai_graph, self.project_desc)
        return workflow

    def upload_project_package(self, workflow: Workflow):
        """
        Upload the project package.

        :param workflow: The generated workflow.
        """
        # todo need to add update project uri
        with open(self.project_desc.get_absolute_temp_path() + "/"
                  + self.project_desc.project_config.get_project_uuid() + "_workflow.json", 'w') as f:
            f.write(json_utils.dumps(workflow))
        blob_manager = BlobManagerFactory.get_blob_manager(self.project_desc.project_config)
        uploaded_project_path = blob_manager.upload_blob(str(workflow.workflow_id), self.project_desc.project_path)
        self.project_desc.project_config['uploaded_project_path'] = uploaded_project_path
        for job in workflow.jobs.values():
            job.job_config.project_path = uploaded_project_path
            job.job_config.project_local_path = self.project_desc.project_path

    def set_entry_module_path(self, workflow: Workflow):
        """
        Set entry model path.
        :param workflow: The generated workflow.
        """
        if self.project_desc.project_config.get('entry_module_path') is None:
            entry_module_path = (file_path_to_absolute_module(sys.argv[0])).split('.')[-1]
            self.project_desc.project_config['entry_module_path'] = entry_module_path
        for job in workflow.jobs.values():
            job.job_config.properties.update(self.project_desc.project_config)

    def submit_workflow(self, ex_workflow: Workflow) -> Optional[int]:
        """
        Submit Workflow.

        :param ex_workflow: The generated workflow.
        :return: Workflow id.
        """
        return self.get_client().submit_workflow(json_utils.dumps(ex_workflow))[1]

    def wait_for_result(self, workflow_id: int) -> Optional[int]:
        """
        Wait for the results which generates from the specific workflow.

        :param workflow_id: The workflow id.
        :return: Schedule result of the workflow.
        """
        res = self.get_client().is_alive_workflow(workflow_id=workflow_id)
        while res[1]:
            time.sleep(1)
            res = self.get_client().is_alive_workflow(workflow_id=workflow_id)

        return self.get_client().get_workflow_execution_result(workflow_id=workflow_id)[1]

    def stop_workflow_execution(self, workflow_execution_id: int) -> Tuple[int, int, Text]:
        """
        Stop the specific workflow execution.

        :param workflow_execution_id: The workflow id.
        :return: Return_code, Workflow_id, Message of the workflow execution.
        """
        return self.get_client().stop_workflow(workflow_id=workflow_execution_id)


_default_project = Project()


def run(project_path: Text = None, dag_id: Text = None,
        scheduler_type: SchedulerType = SchedulerType.AIFLOW):
    """
    Run project under the current project path.

    :param project_path: The path of the project path.
    :param dag_id: The airflow dag id.
    :param scheduler_type: The scheduler type of workflow.
    :return: Workflow id or airflow generated code.
    """
    project_desc = generate_project_desc(project_path)
    if scheduler_type == SchedulerType.AIRFLOW:
        return _submit_to_airflow(project_desc=project_desc, dag_id=dag_id)
    else:
        return submit_ai_flow(ai_graph=default_graph(), project_desc=project_desc)


def submit(project_path: Text = None,
           dag_id: Text = None,
           default_args=None):
    return deploy_to_airflow(project_path, dag_id, default_args)


def generate_airflow_file_text(project_path: Text,
                               dag_id=None
                               ) -> Optional[str]:
    """
    generator airflow code.
    :param project_path: The path of the project path.
    :param dag_id: The airflow dag id.
    :return: Workflow id.
    """
    project_desc = generate_project_desc(project_path)

    return _generate_airflow_file_text(project_desc=project_desc, dag_id=dag_id)


def _generate_airflow_file_text(ai_graph: AIGraph = default_graph(),
                                project_desc: ProjectDesc = ProjectDesc(),
                                dag_id=None,
                                default_args=None
                                ) -> Optional[str]:
    """
    Submit ai flow to schedule.

    :param ai_graph: The ai graph constructed from project.
    :param project_desc: The project description.
    :return: Workflow id.
    """
    ex_workflow = generate_workflow(ai_graph, project_desc)
    for job in ex_workflow.jobs.values():
        register_job_meta(workflow_id=ex_workflow.workflow_id, job=job)
    _default_project.upload_project_package(ex_workflow)
    return DAGGenerator().generator(ex_workflow, dag_id, default_args)


def deploy_to_airflow(project_path: Text = None,
                      dag_id: Text = None,
                      default_args=None):
    """
    Run project under the current project path.

    :param project_path: The description of the project..
    :param dag_id: The airflow dag id.
    :param default_args:
    :return: (airflow dag file path, airflow dag code).
    """
    project_desc = generate_project_desc(project_path)
    if dag_id is None:
        dag_id = default_af_job_context().global_workflow_config.name
    if dag_id is None:
        dag_id = project_desc.project_name
    deploy_path = project_desc.project_config.get_airflow_deploy_path()
    if deploy_path is None:
        raise Exception("airflow_deploy_path config not set!")
    airflow_file_path = deploy_path + '/' + dag_id + '.py'
    if os.path.exists(airflow_file_path):
        os.remove(airflow_file_path)
    generated_code = _generate_airflow_file_text(ai_graph=default_graph(),
                                                 project_desc=project_desc,
                                                 dag_id=dag_id,
                                                 default_args=default_args)
    with NamedTemporaryFile(mode='w+t', prefix=dag_id, suffix='.py', dir='/tmp', delete=False) as f:
        f.write(generated_code)
    os.rename(f.name, airflow_file_path)
    return airflow_file_path


def _submit_to_airflow(project_desc: ProjectDesc = ProjectDesc(), dag_id: Text = None):
    airflow_operation = AirflowOperation(
        notification_server_uri=project_desc.project_config.get_notification_service_uri())
    return airflow_operation.trigger_workflow_execution(project_desc, dag_id)


def generate_project_desc(project_path: Text = None) -> ProjectDesc:
    """
    Run project under the current project path.

    :param project_path: The path of the project path.
    :return: project description.
    """
    if project_path is None:
        # generate project structure automatically without `project_path` parameter.
        def generate_project(code):
            """
            generate project automatically without project path.

            :param code: project code.
            :return: project description.
            """
            project_path = tempfile.mkdtemp()
            # generate project config file.
            project_config().dump_to_file(project_path + '/project.yaml')
            # generate project structure.
            os.makedirs(project_path + '/python_codes')
            os.makedirs(project_path + '/jar_dependencies')
            os.makedirs(project_path + '/resources')
            open(project_path + '/python_codes/__init__.py', 'w')
            fd, temp_file = tempfile.mkstemp(suffix='.py', dir=project_path + '/python_codes')
            with open(temp_file, 'w') as f:
                f.write(code)
            # generate project description.
            project_desc: ProjectDesc = get_project_description_from(project_path)
            project_desc.project_name = project_config().get_project_name()
            project_desc.project_config['entry_module_path'] = (file_path_to_absolute_module(temp_file)).split('.')[-1]
            return project_desc

        return generate_project(inspect.getsource(sys._getframe().f_back.f_back))
    else:
        # parse project description
        project_desc: ProjectDesc = get_project_description_from(project_path)
        project_desc.project_name = project_config().get_project_name()
        return project_desc


def submit_ai_flow(ai_graph: AIGraph = default_graph(),
                   project_desc: ProjectDesc = ProjectDesc()
                   ) -> Optional[int]:
    """
    Submit ai flow to schedule.

    :param ai_graph: The ai graph constructed from project.
    :param project_desc: The project description.
    :return: Workflow id.
    """
    ex_workflow = generate_workflow(ai_graph, project_desc)
    _default_project.upload_project_package(ex_workflow)
    return _default_project.submit_workflow(ex_workflow=ex_workflow)


def register_job_meta(workflow_id: int, job):
    start_time = time.time()
    if job.job_config.job_name is None:
        name = job.instance_id
    else:
        name = job.job_config.job_name
    job_name = str(workflow_id) + '_' + name[0:20] + '_' + str(start_time)
    job_meta = _default_project.get_client().register_job(name=job_name,
                                                          job_id=job.instance_id,
                                                          workflow_execution_id=workflow_id,
                                                          start_time=round(start_time))
    job.uuid = job_meta.uuid
    job.job_name = job_name


def generate_workflow(ai_graph, project_desc):
    _default_project.project_desc = project_desc
    if project_desc.project_path is None:
        project_desc.project_path = '/tmp'
    if not os.path.exists(project_desc.get_absolute_temp_path()):
        os.mkdir(project_desc.get_absolute_temp_path())
    if not os.path.exists(project_desc.get_absolute_log_path()):
        os.mkdir(project_desc.get_absolute_log_path())
    ex_workflow = _default_project.generate_workflow(ai_graph=ai_graph)
    _default_project.set_entry_module_path(ex_workflow)
    return ex_workflow


def compile_workflow(project_path: Text = None) -> Workflow:
    project_desc = generate_project_desc(project_path)
    return generate_workflow(ai_graph=default_graph(), project_desc=project_desc)


def wait_workflow_execution_finished(workflow_execution_id: int) -> Optional[int]:
    """
    Wait for the results which generates from the specific workflow execution.

    :param workflow_execution_id: The workflow execution id.
    :return: Schedule result of the workflow.
    """
    return _default_project.wait_for_result(workflow_id=workflow_execution_id)


def stop_execution_by_id(workflow_execution_id: int) -> Tuple[int, int, Text]:
    """
    Stop the workflow execution by id.

    :param workflow_execution_id: The workflow execution id.
    :return: Return_code, Workflow_id, Message of the workflow execution.
    """
    return _default_project.stop_workflow_execution(workflow_execution_id=workflow_execution_id)
