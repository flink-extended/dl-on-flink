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
from typing import Text
from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo
from ai_flow.project.project_config import ProjectConfig
from ai_flow.workflow.workflow_config import WorkflowConfig, load_workflow_config

from ai_flow.util import serialization_utils


class JobRuntimeEnv(object):
    """
    JobRuntimeEnv represents the environment information needed for an ai flow job to run. It contains:
    1. project configuration.
    2. workflow configuration.
    3. Job running depends on resource files.
    4. Information when the job is executed.
    """

    def __init__(self,
                 working_dir: Text,
                 workflow_name: Text = None,
                 job_execution_info: JobExecutionInfo = None):
        self._working_dir: Text = working_dir
        self._workflow_name: Text = workflow_name
        self._job_execution_info: JobExecutionInfo = job_execution_info
        self._workflow_config: WorkflowConfig = None
        self._project_config: ProjectConfig = None

    @property
    def working_dir(self) -> Text:
        """
        return: The working directory of the job.
        """
        return self._working_dir

    @property
    def workflow_name(self) -> Text:
        """
        return: The name of the workflow which the job belongs.
        """
        if self._workflow_name is None:
            self._workflow_name = serialization_utils.read_object_from_serialized_file(
                os.path.join(self.working_dir, 'workflow_name'))
        return self._workflow_name

    @property
    def job_name(self) -> Text:
        """
        return: The name of the job.
        """
        if self._job_execution_info is None:
            return self.job_execution_info.job_name
        return self._job_execution_info.job_name

    @property
    def log_dir(self) -> Text:
        """
        return: The directory where job logs are stored.
        """
        return os.path.join(self._working_dir, 'logs')

    @property
    def resource_dir(self) -> Text:
        """
        return: The directory where job resource files are stored.
        """
        return os.path.join(self._working_dir, 'resources')

    @property
    def generated_dir(self) -> Text:
        """
        return: The directory where the job stores the generated executable files.
        """
        return os.path.join(self._working_dir, 'generated')

    @property
    def dependencies_dir(self) -> Text:
        """
        return: The directory where the job runs dependent files.
        """
        return os.path.join(self._working_dir, 'dependencies')

    @property
    def python_dep_dir(self) -> Text:
        """
        return: The directory where the job runs dependent python files.
        """
        return os.path.join(self.dependencies_dir, 'python')

    @property
    def go_dep_dir(self) -> Text:
        """
        return: The directory where the job runs dependent go files.
        """
        return os.path.join(self.dependencies_dir, 'go')

    @property
    def jar_dep_dir(self) -> Text:
        """
        return: The directory where the job runs dependent jar files.
        """
        return os.path.join(self.dependencies_dir, 'jar')

    @property
    def project_config_file(self) -> Text:
        """
        return: The project configuration file path.
        """
        return os.path.join(self.working_dir, 'project.yaml')

    @property
    def project_config(self) -> ProjectConfig:
        """
        return: The project configuration(ai_flow.project.project_config.ProjectConfig)
        """
        if self._project_config is None:
            self._project_config = ProjectConfig()
            self._project_config.load_from_file(self.project_config_file)
        return self._project_config

    @property
    def workflow_config_file(self) -> Text:
        """
        return: The workflow configuration file path.
        """
        return os.path.join(self.working_dir, '{}.yaml'.format(self.workflow_name))

    @property
    def workflow_config(self) -> WorkflowConfig:
        """
        return: The workflow configuration(ai_flow.workflow.workflow_config.WorkflowConfig)
        """
        if self._workflow_config is None:
            self._workflow_config = load_workflow_config(config_path=self.workflow_config_file)
        return self._workflow_config

    @property
    def workflow_entry_file(self) -> Text:
        """
        return: The path of file that defines the workflow.
        """
        return os.path.join(self.working_dir, '{}.py'.format(self.workflow_name))

    @property
    def job_execution_info(self) -> JobExecutionInfo:
        """
        return: Information when the job is executed.
        """
        if self._job_execution_info is None:
            self._job_execution_info = serialization_utils.read_object_from_serialized_file(
                os.path.join(self.working_dir, 'job_execution_info'))
        return self._job_execution_info

    def save_workflow_name(self):
        if self._workflow_name is None:
            return
        file_path = os.path.join(self.working_dir, 'workflow_name')
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, 'wb') as fp:
            fp.write(serialization_utils.serialize(self._workflow_name))

    def save_job_execution_info(self):
        if self._job_execution_info is None:
            return
        file_path = os.path.join(self.working_dir, 'job_execution_info')
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, 'wb') as fp:
            fp.write(serialization_utils.serialize(self._job_execution_info))
