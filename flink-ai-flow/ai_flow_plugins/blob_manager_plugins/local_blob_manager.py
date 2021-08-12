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
import shutil
import tempfile
from typing import Text, Dict, Any
from pathlib import Path
from ai_flow.plugin_interface.blob_manager_interface import BlobManager
from ai_flow.util.file_util.zip_file_util import make_dir_zipfile
from ai_flow_plugins.blob_manager_plugins.blob_manager_utils import extract_project_zip_file


class LocalBlobManager(BlobManager):
    """
    LocalBlobManager is an implementation of BlobManager based on the local file system.
    LocalBlobManager contains 2 configuration items:
    1. local_repository: It represents the root path of the downloaded project package.
                         If local_path is set, local_path is used first.
    2. remote_repository: It represents the root path of the upload project package.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._local_repo = config.get('local_repository', None)
        self._remote_repo = config.get('remote_repository', None)

    def upload_project(self, workflow_snapshot_id: Text, project_path: Text) -> Text:
        """
        upload a given project to blob server for remote execution.

        :param workflow_snapshot_id: It is the unique identifier for each workflow generation.
        :param project_path: The path of this project.
        :return The uri of the uploaded project file in blob server.
        """
        if self._remote_repo is not None:
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_file_name = 'workflow_{}_project.zip'.format(workflow_snapshot_id)
                upload_file_path = Path('{}/{}'.format(self._remote_repo, zip_file_name))
                if os.path.exists(upload_file_path):
                    os.remove(upload_file_path)
                temp_dir_path = Path(temp_dir)
                zip_file_path = temp_dir_path / zip_file_name
                make_dir_zipfile(project_path, zip_file_path)
                shutil.move(zip_file_path, upload_file_path)
                return str(upload_file_path)
        else:
            return project_path

    def download_project(self, workflow_snapshot_id, remote_path: Text, local_path: Text = None) -> Text:
        """
        download the needed resource from remote blob server to local process for remote execution.

        :param workflow_snapshot_id: It is the unique identifier for each workflow generation.
        :param remote_path: The project package uri.
        :param local_path: Download file root path.
        :return The local project path.
        """
        if self._local_repo is not None:
            repo_path = local_path if local_path is not None else self._local_repo
            local_zip_file_name = 'workflow_{}_project'.format(workflow_snapshot_id)
            extract_path = str(Path(repo_path) / local_zip_file_name)
            return extract_project_zip_file(workflow_snapshot_id=workflow_snapshot_id,
                                            local_root_path=repo_path,
                                            zip_file_path=remote_path,
                                            extract_project_path=extract_path)
        else:
            return remote_path

    def cleanup_project(self, workflow_snapshot_id, remote_path: Text):
        """
        clean up the project files downloaded or created during this execution.
        :param workflow_snapshot_id: It is the unique identifier for each workflow generation.
        :param remote_path: The project package uri.
        """
        pass

