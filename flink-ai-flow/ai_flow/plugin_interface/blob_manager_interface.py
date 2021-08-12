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
from abc import ABC, abstractmethod
from typing import Text, Dict

from ai_flow.common.configuration import AIFlowConfiguration
from ai_flow.common.module_load import import_string


class BlobConfig(AIFlowConfiguration):

    def __init__(self, config: Dict):
        super().__init__()
        if config is None:
            raise Exception(
                'The `{}` option is not configured in the {} option. Please add it!'.format('blob', 'project.yaml'))
        self['blob_manager_class'] = None
        if config.get('blob_manager_class') is None:
            raise Exception(
                'The `blob_manager_class` option of blob config is not configured. '
                'Please add the `blob_manager_class` option under the `blob` option!')
        self['blob_manager_class'] = config.get('blob_manager_class')
        self['blob_manager_config'] = {}
        if config.get('blob_manager_config') is not None:
            self['blob_manager_config'] = config.get('blob_manager_config')


    def blob_manager_class(self):
        return self.get('blob_manager_class')

    def set_blob_manager_class(self, value):
        self['blob_manager_class'] = value

    def blob_manager_config(self):
        return self['blob_manager_config']

    def set_blob_manager_config(self, value):
        self['blob_manager_config'] = value


class BlobManager(ABC):
    """
    A BlobManager is responsible for uploading and downloading files and resource for an execution of an ai flow project.
    """
    def __init__(self, config: Dict):
        self.config = config

    @abstractmethod
    def upload_project(self, workflow_snapshot_id: Text, project_path: Text) -> Text:
        """
        upload a given project to blob server for remote execution.

        :param workflow_snapshot_id: It is the unique identifier for each workflow generation.
        :param project_path: the path of this project.
        :return the uri of the uploaded project file in blob server.
        """
        pass

    @abstractmethod
    def download_project(self, workflow_snapshot_id, remote_path: Text, local_path: Text = None) -> Text:
        """
        download the needed resource from remote blob server to local process for remote execution.

        :param workflow_snapshot_id: It is the unique identifier for each workflow generation.
        :param remote_path: The project package uri.
        :param local_path: Download file root path.
        :return Local project path.
        """
        pass

    def cleanup_project(self, workflow_snapshot_id, remote_path: Text):
        """
        clean up the project files downloaded or created during this execution.
        :param workflow_snapshot_id: It is the unique identifier for each workflow generation.
        :param remote_path: The project package uri.
        """
        pass


class BlobManagerFactory:
    @classmethod
    def create_blob_manager(cls, class_name, config: Dict) -> BlobManager:
        """
        :param class_name: The class name of a (~class:`ai_flow.plugin_interface.blob_manager_interface.BlobManager`)
        :param config: The configuration of the BlobManager.
        """
        if class_name is None:
            return None
        class_object = import_string(class_name)
        return class_object(config)
