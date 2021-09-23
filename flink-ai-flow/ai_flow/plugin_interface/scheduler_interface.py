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
from abc import ABC, abstractmethod
from typing import Dict, Text, List, Optional
from ai_flow.util import json_utils
from ai_flow.workflow.workflow import Workflow
from ai_flow.context.project_context import ProjectContext


class WorkflowInfo(json_utils.Jsonable):

    def __init__(self,
                 namespace: Text = None,
                 workflow_name: Text = None,
                 properties: Dict = None):
        self._namespace = namespace
        self._workflow_name = workflow_name
        if properties is None:
            properties = {}
        self._properties = properties

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, value):
        self._namespace = value

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

    def __str__(self) -> str:
        return json_utils.dumps(self)


class WorkflowExecutionInfo(json_utils.Jsonable):
    def __init__(self,
                 workflow_execution_id: Text,
                 workflow_info: WorkflowInfo = None,
                 status: Text = None,
                 properties: Dict = None,
                 start_date: Text = None,
                 end_date: Text = None):
        if properties is None:
            properties = {}
        self._properties = properties
        self._workflow_execution_id = workflow_execution_id
        self._workflow_info = workflow_info
        self._status = status
        self._start_date = start_date
        self._end_date = end_date

    @property
    def workflow_execution_id(self):
        return self._workflow_execution_id

    @workflow_execution_id.setter
    def workflow_execution_id(self, value):
        self._workflow_execution_id = value

    @property
    def workflow_info(self):
        return self._workflow_info

    @workflow_info.setter
    def workflow_info(self, value):
        self._workflow_info = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        self._start_date = value

    @property
    def end_date(self):
        return self._start_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    def __str__(self) -> str:
        return json_utils.dumps(self)


class JobExecutionInfo(json_utils.Jsonable):
    def __init__(self,
                 job_name: Text = None,
                 status: Text = None,
                 workflow_execution: WorkflowExecutionInfo = None,
                 job_execution_id: Text = None,
                 start_date: Text = None,
                 end_date: Text = None,
                 properties: Dict = None,
                 ):
        self._job_name = job_name
        self._status = status
        self._workflow_execution = workflow_execution
        self._start_date = start_date
        self._end_date = end_date
        self._job_execution_id = job_execution_id
        if properties is None:
            properties = {}
        self._properties = properties

    @property
    def job_name(self):
        return self._job_name

    @job_name.setter
    def job_name(self, value):
        self._job_name = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def workflow_execution(self):
        return self._workflow_execution

    @workflow_execution.setter
    def workflow_execution(self, value):
        self._workflow_execution = value

    @property
    def job_execution_id(self):
        return self._job_execution_id

    @job_execution_id.setter
    def job_execution_id(self, value):
        self._job_execution_id = value

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        self._start_date = value

    @property
    def end_date(self):
        return self._start_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value

    def __str__(self) -> str:
        return json_utils.dumps(self)


class Scheduler(ABC):
    def __init__(self, config: Dict):
        self._config = config

    @property
    def config(self):
        return self._config

    @abstractmethod
    def submit_workflow(self, workflow: Workflow, project_context: ProjectContext) -> WorkflowInfo:
        """
        Submit the workflow to scheduler.
        :param workflow: ai_flow.workflow.workflow.Workflow type.
        :param project_context: ai_flow.context.project_context.ProjectContext type.
        :return: The workflow information.
        """
        pass

    @abstractmethod
    def pause_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        """
        Make the scheduler stop scheduling the workflow.
        :param project_name: The project name.
        :param workflow_name: The workflow name.
        :return: The workflow information.
        """
        pass

    @abstractmethod
    def resume_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        """
        Make the scheduler resume scheduling the workflow.
        :param project_name: The project name.
        :param workflow_name: The workflow name.
        :return: The workflow information.
        """
        pass

    @abstractmethod
    def start_new_workflow_execution(self, project_name: Text, workflow_name: Text) -> Optional[WorkflowExecutionInfo]:
        """
        Make the scheduler new a workflow execution.
        :param project_name: The project name.
        :param workflow_name: The workflow name.
        :return: The workflow execution information.
        """
        pass

    @abstractmethod
    def stop_all_workflow_execution(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        """
        Stop all workflow execution of the workflow.
        :param project_name: The project name.
        :param workflow_name: The workflow name.
        :return: The workflow execution information.
        """
        pass

    @abstractmethod
    def stop_workflow_execution(self, execution_id: Text) -> Optional[WorkflowExecutionInfo]:
        """
        Stop the workflow execution by execution id.
        :param execution_id: The workflow execution id.
        :return: The workflow execution information.
        """
        pass

    @abstractmethod
    def get_workflow_execution(self, execution_id: Text) -> Optional[WorkflowExecutionInfo]:
        """
        Get the workflow execution information.
        :param execution_id: The workflow execution id.
        :return: The workflow execution information.
        """
        pass

    @abstractmethod
    def list_workflow_executions(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        """
        List all workflow executions by workflow name.
        :param project_name: The project name.
        :param workflow_name: The workflow name.
        :return: The workflow execution information.

        """
        pass

    @abstractmethod
    def start_job_execution(self, job_name: Text, execution_id: Text) -> JobExecutionInfo:
        """
        Make the scheduler start a new job execution.
        :param job_name: The job name.
        :param execution_id: The workflow execution id.
        :return: The job execution information.
        """
        pass

    @abstractmethod
    def stop_job_execution(self, job_name: Text, execution_id: Text) -> JobExecutionInfo:
        """
        Make the scheduler stop the job execution.
        :param job_name: The job name.
        :param execution_id: The workflow execution id.
        :return: The job execution information.
        """
        pass

    @abstractmethod
    def restart_job_execution(self, job_name: Text, execution_id: Text) -> JobExecutionInfo:
        """
        Make the scheduler restart a job execution. If job status is running, first stop the job and then start it.
        :param job_name: The job name.
        :param execution_id: The workflow execution id.
        :return: The job execution information.
        """
        pass

    @abstractmethod
    def get_job_executions(self, job_name: Text, execution_id: Text) -> List[JobExecutionInfo]:
        """
        Get the job execution information by job name.
        :param job_name: The job name.
        :param execution_id: The workflow execution id.
        :return: The job execution information.
        """
        pass

    @abstractmethod
    def list_job_executions(self, execution_id: Text) -> List[JobExecutionInfo]:
        """
        List the job execution information by the workflow execution id.
        :param execution_id: The workflow execution id.
        :return: The job execution information.
        """
        pass
