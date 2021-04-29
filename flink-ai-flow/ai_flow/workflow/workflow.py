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
from typing import List, Dict, Text
from ai_flow.meta.job_meta import State
from ai_flow.graph.node import BaseNode
from ai_flow.graph.edge import JobControlEdge
from ai_flow.workflow.job import BaseJob
from ai_flow.graph.graph import _get_id_generator
from ai_flow.project.project_description import ProjectDesc


class Workflow(BaseNode):

    def __init__(self) -> None:
        super().__init__()
        self.workflow_id: int = None
        self.workflow_name: Text = None
        self.execution_name: Text = None
        self.jobs: Dict[Text, BaseJob] = {}
        self.edges: Dict[Text, List[JobControlEdge]] = {}
        self.workflow_phase = None
        self.start_time = None
        self.end_time = None
        self.project_desc: ProjectDesc = None

    def add_job(self, job: BaseJob):
        if job.instance_id is None:
            instance_id = _get_id_generator(self).generate_id(job)
            job.set_instance_id(instance_id)
        self.jobs[job.instance_id] = job

    def add_edges(self, job_instance_id: Text, dependencies: List[JobControlEdge]):
        self.edges[job_instance_id] = dependencies

    def add_edge(self, job_instance_id: Text, edge: JobControlEdge):
        if job_instance_id not in self.edges:
            self.edges[job_instance_id] = []
        self.edges[job_instance_id].append(edge)


class WorkflowInfo(object):

    def __init__(self, workflow_name: Text = None, properties: Dict = None):
        """
        :param workflow_name: The identify of the ai_flow workflow.
        :param properties: The properties of the workflow.
        """
        self._workflow_name = workflow_name
        if properties is None:
            properties = {}
        self._properties = properties

    @property
    def workflow_name(self):
        return self._workflow_name

    @workflow_name.setter
    def workflow_name(self, value):
        self._workflow_name = value

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value


def submit_workflow(workflow_name: Text = None,
                    args: Dict = None) -> WorkflowInfo:
    """
    Submit the ai flow workflow to the scheduler.
    :param workflow_name: The ai flow workflow identify.
    :param args: The arguments of the submit action.
    :return: The result of the submit action.
    """
    pass


def delete_workflow(workflow_name: Text = None) -> WorkflowInfo:
    """
    Delete the ai flow workflow from the scheduler.
    :param workflow_name: The ai flow workflow identify.
    :return: The result of the action.
    """
    pass


def pause_workflow_scheduling(workflow_name: Text = None) -> WorkflowInfo:
    """
    Pause the ai flow workflow from the scheduler.
    :param workflow_name: The ai flow workflow identify.
    :return: The result of the action.
    """
    pass


def resume_workflow_scheduling(workflow_name: Text = None) -> WorkflowInfo:
    """
    Resume the ai flow workflow from the scheduler.
    :param workflow_name: The ai flow workflow identify.
    :return: The result of the action.
    """
    pass


def get_workflow(workflow_name: Text = None) -> WorkflowInfo:
    """
    Return the workflow information.
    :param workflow_name: The ai flow workflow identify.
    :return: the workflow information.
    """
    pass


def list_workflows() -> List[WorkflowInfo]:
    """
    :return: All workflow information.
    """
    pass


class WorkflowExecutionInfo(object):
    def __init__(self,
                 execution_id: Text,
                 workflow_info: WorkflowInfo = None,
                 state: State = None,
                 properties: Dict = None):
        if properties is None:
            properties = {}
        self._execution_id = execution_id
        self._workflow_info = workflow_info
        self._state = state
        self._properties = properties

    @property
    def execution_id(self):
        return self._execution_id

    @execution_id.setter
    def execution_id(self, value):
        self._execution_id = value

    @property
    def workflow_info(self):
        return self._workflow_info

    @workflow_info.setter
    def workflow_info(self, value):
        self._workflow_info = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value


def start_new_workflow_execution(workflow_name: Text) -> WorkflowExecutionInfo:
    """
    Run the project under the current project path.
    :param workflow_name: The ai flow workflow identify.
    :return: The result of the run action.
    """
    pass


def kill_all_workflow_executions(workflow_name: Text) -> List[WorkflowExecutionInfo]:
    """
    Stop all instances of the workflow.
    :param workflow_name: The ai flow workflow identify.
    :return: The result of the action.
    """
    pass


def kill_workflow_execution(execution_id: Text) -> WorkflowExecutionInfo:
    """
    Stop the instance of the workflow.
    :param execution_id: The ai flow workflow execution identify.
    :return: The result of the action.
    """
    pass


def get_workflow_execution(execution_id: Text) -> WorkflowExecutionInfo:
    """
    Get the WorkflowExecutionInfo from scheduler.
    :param execution_id:
    :return: WorkflowExecutionInfo
    """
    pass


def list_workflow_executions(workflow_name: Text) -> List[WorkflowExecutionInfo]:
    """
    :param workflow_name: The ai flow workflow identify.
    :return: All workflow executions of the workflow.
    """
    pass


class JobInfo(object):
    def __init__(self,
                 job_name: Text,
                 state: State,
                 workflow_execution: WorkflowExecutionInfo
                 ):
        self._job_name = job_name
        self._state = state
        self._workflow_execution = workflow_execution

    @property
    def job_name(self):
        return self._job_name

    @job_name.setter
    def job_name(self, value):
        self._job_name = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def workflow_execution(self):
        return self._workflow_execution

    @workflow_execution.setter
    def workflow_execution(self, value):
        self._workflow_execution = value


def start_job(job_name: Text,
              execution_id: Text) -> JobInfo:
    """
    Start a job defined in the ai flow workflow.
    :param job_name: The job name which task defined in workflow.
    :param execution_id: The ai flow workflow execution identify.
    :return: The result of the action.
    """
    pass


def stop_job(job_name: Text,
             execution_id: Text) -> JobInfo:
    """
    Stop a job defined in the ai flow workflow.
    :param job_name: The job name which task defined in workflow.
    :param execution_id: The ai flow workflow execution identify.
    :return: The result of the action.
    """
    pass


def restart_job(job_name: Text,
                execution_id: Text) -> JobInfo:
    """
    Restart a task defined in the ai flow workflow.
    :param job_name: The job name which task defined in workflow.
    :param execution_id: The ai flow workflow execution identify.
    :return: The result of the action.
    """
    pass


def get_job(job_name: Text,
            execution_id: Text) -> JobInfo:
    """
    Get job information by job name.
    :param job_name:
    :param execution_id:
    :return:
    """
    pass


def list_jobs(execution_id: Text) -> List[JobInfo]:
    """
    List the jobs of the workflow execution.
    :param execution_id:
    :return:
    """
    pass
