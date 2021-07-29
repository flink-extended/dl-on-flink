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
import tempfile
from pathlib import Path
from typing import Text, Dict, Any

from hdfs.client import InsecureClient

from ai_flow.plugin_interface.blob_manager_interface import BlobManager
from ai_flow.util.file_util.zip_file_util import make_dir_zipfile
from ai_flow_plugins.blob_manager_plugins.blob_manager_utils import extract_project_zip_file


class HDFSBlobManager(BlobManager):
    """
    HDFSBlobManager is an implementation of BlobManager based on the hdfs file system
    HDFSBlobManager contains configuration items:
    1. hdfs_url: Hostname or IP address of HDFS namenode, prefixed with protocol, followed by WebHDFS port on namenode
    2. hdfs_user: User default. Defaults to the current user's (as determined by `whoami`).
    3. repo_name: The upload directory of the project.
    4. local_repository: The download directory of the project.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        hdfs_url = config.get('hdfs_url', None)
        hdfs_user = config.get('hdfs_user', 'default')
        hdfs_client = InsecureClient(url=hdfs_url, user=hdfs_user)
        self._hdfs_client = hdfs_client
        self._repo_name = config.get('repo_name', '')
        self._local_repo = config.get('local_repository', None)

    def upload_project(self, workflow_snapshot_id: Text, project_path: Text) -> Text:
        """
        Uploads a given project from local to hdfs file system for remote workflow execution.

        :param workflow_snapshot_id: The id of the workflow snapshot, which is the unique identifier for each workflow
                                                           generation.
        :param project_path: The local path of the project.
        :return: The hdfs path of the uploaded project in blob server.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file_name = 'workflow_{}_project.zip'.format(workflow_snapshot_id)
            temp_dir_path = Path(temp_dir)
            zip_file_path = temp_dir_path / zip_file_name
            make_dir_zipfile(project_path, zip_file_path)
            object_key = self._repo_name + '/' + zip_file_name
            self._hdfs_client.upload(hdfs_path=object_key, local_path=str(zip_file_path))
        return object_key

    def download_project(self, workflow_snapshot_id, remote_path: Text, local_path: Text = None) -> Text:
        """
        Downloads a given project from hdfs file system to local for remote workflow execution.

        :param workflow_snapshot_id: The id of the workflow snapshot, which is the unique identifier for each workflow
                                                           generation.
        :param remote_path: The hdfs path of the project.
        :param local_path: The local root path of the downloaded project.
        :return The local path of the download project.
        """
        local_zip_file_name = 'workflow_{}_project'.format(workflow_snapshot_id)
        if local_path is not None:
            repo_path = Path(local_path)
        elif self._local_repo is not None:
            repo_path = Path(self._local_repo)
        else:
            repo_path = Path(tempfile.gettempdir())
        local_zip_file_path = str(repo_path / local_zip_file_name) + '.zip'
        extract_path = str(repo_path / local_zip_file_name)
        self._hdfs_client.download(hdfs_path=remote_path, local_path=local_zip_file_path)
        return extract_project_zip_file(workflow_snapshot_id=workflow_snapshot_id,
                                        local_root_path=repo_path,
                                        zip_file_path=local_zip_file_path,
                                        extract_project_path=extract_path)
