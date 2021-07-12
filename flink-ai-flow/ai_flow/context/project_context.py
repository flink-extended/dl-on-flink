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
import os
from typing import List, Text
from ai_flow.project.project_config import ProjectConfig
from ai_flow.util.json_utils import Jsonable


class ProjectContext(Jsonable):
    """
    ProjectContext maintains the directory structure and information of an ai flow project.
    A common ai flow project would follow the directory structure as bellow.

    SimpleProject
        |- workflows # Directory for storing workflow definitions
           |- workflow_name1 # Is a directory store workflow named workflow_name1.
           |- workflow_name2 # Is a directory store workflow named workflow_name2.
           |- workflow_name3 # Is a directory store workflow named workflow_name3.
              |- workflow_name3.py # Workflow defined file.
              |- workflow_name3.yaml # Workflow configuration file.
        |- dependencies # Resource storage directory on which workflow execution depends.
            |-python # Python file resource storage directory on which workflow execution depends.
            |-jar # Jar resource storage directory on which workflow execution depends.
            |-go #  Go resource storage directory on which workflow execution depends.
        |- generated # The File storage directory generated in the process of translator generating workflow.
        |- resources # Store the resource files of the project.
        └─ project.yaml # The project configuration file.
    """

    def __init__(self) -> None:
        super().__init__()
        self.project_path: Text = None
        self.project_config: ProjectConfig = None

    @property
    def project_name(self):
        return self.project_config.get_project_name()

    def get_resources_path(self) -> Text:
        return os.path.join(self.project_path, 'resources')

    def get_generated_path(self) -> Text:
        return os.path.join(self.project_path, 'generated')

    def list_resources_paths(self) -> List:
        return os.listdir(self.get_resources_path())

    def get_dependencies_path(self) -> Text:
        return os.path.join(self.project_path, 'dependencies')

    def get_project_config_file(self) -> Text:
        return os.path.join(self.project_path, 'project.yaml')

    def get_python_dependencies_path(self) -> Text:
        return os.path.join(self.get_dependencies_path(), 'python')

    def get_jar_dependencies_path(self) -> Text:
        return os.path.join(self.get_dependencies_path(), 'jar')

    def list_jar_paths(self) -> List:
        return os.listdir(self.get_jar_dependencies_path())

    def get_go_dependencies_path(self) -> Text:
        return os.path.join(self.get_dependencies_path(), 'go')

    def get_workflows_path(self) -> Text:
        return os.path.join(self.project_path, 'workflows')

    def list_workflows(self) -> List[Text]:
        return os.listdir(self.get_workflows_path())

    def get_workflow_path(self, workflow_name) -> Text:
        return os.path.join(self.get_workflows_path(), workflow_name)

    def get_workflow_config_file(self, workflow_name) -> Text:
        return os.path.join(self.get_workflow_path(workflow_name), '{}.yaml'.format(workflow_name))

    def get_workflow_entry_file(self, workflow_name) -> Text:
        return os.path.join(self.get_workflow_path(workflow_name), '{}.py'.format(workflow_name))

    def get_workflow_entry_module(self, workflow_name) -> Text:
        return workflow_name


def build_project_context(project_path: Text) -> ProjectContext:
    """
    Load a project context for a given project path.
    :param project_path: the path of a ai flow project.
    :return: a ProjectContext object that contains the structure information of this project.
    """
    project_context = ProjectContext()
    project_path = os.path.abspath(project_path)
    project_context.project_path = project_path
    project_context.project_config = ProjectConfig()
    project_context.project_config.load_from_file(project_context.get_project_config_file())
    return project_context


__current_project_context__ = ProjectContext()

__current_project_config__ = ProjectConfig()


def init_project_config(project_config_file):
    """
    Load project configuration of the ai flow project.
    """
    __current_project_config__.load_from_file(project_config_file)


def init_project_context(project_path: Text):
    """
    Load project configuration and project context of the ai flow project.
    """
    global __current_project_context__, __current_project_config__
    project_context = build_project_context(project_path)
    __current_project_context__ = project_context
    init_project_config(project_context.get_project_config_file())


def current_project_context() -> ProjectContext:
    """
    return: The current project context(ai_flow.context.project_context.ProjectContext).
    """
    return __current_project_context__


def current_project_config() -> ProjectConfig:
    """
    :return: The current project configuration(ai_flow.project.project_config.ProjectConfig)
    """
    return __current_project_config__
