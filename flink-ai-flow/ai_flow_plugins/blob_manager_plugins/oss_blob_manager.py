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
import tempfile
import zipfile
from typing import Text, Dict, Any
from pathlib import Path
import oss2
from ai_flow.plugin_interface.blob_manager_interface import BlobManager
from ai_flow.util.file_util.zip_file_util import make_dir_zipfile


class OssBlobManager(BlobManager):
    """
    OssBlobManager is an implementation of BlobManager based on the oss file system
    OssBlobManager contains configuration items:
    1. access_key_id: The oss access key.
    2. access_key_secret: The oss access secret.
    3. bucket: The oss bucket name.
    4. local_repository: It represents the root path of the downloaded project package.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        ack_id = config.get('access_key_id', None)
        ack_secret = config.get('access_key_secret', None)
        endpoint = config.get('endpoint', None)
        bucket_name = config.get('bucket', None)
        auth = oss2.Auth(ack_id, ack_secret)
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)
        self.repo_name = config.get('repo_name', '')
        self._local_repo = config.get('local_repository', None)

    def upload_project(self, workflow_snapshot_id: Text, project_path: Text) -> Text:
        """
        upload a given project to blob server for remote execution.

        :param workflow_snapshot_id: It is the unique identifier for each workflow generation.
        :param project_path: The path of this project.
        :return The uri of the uploaded project file in blob server.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file_name = 'workflow_{}_project.zip'.format(workflow_snapshot_id)
            temp_dir_path = Path(temp_dir)
            zip_file_path = temp_dir_path / zip_file_name
            make_dir_zipfile(project_path, zip_file_path)
            object_key = self.repo_name + '/' + zip_file_name
            self.bucket.put_object_from_file(key=object_key, filename=str(zip_file_path))
        return object_key

    def download_project(self, workflow_snapshot_id, remote_path: Text, local_path: Text = None) -> Text:
        """
        download the needed resource from remote blob server to local process for remote execution.

        :param workflow_snapshot_id: It is the unique identifier for each workflow generation.
        :param remote_path: The project package uri.
        :param local_path: Download file root path.
        :return The local project path.
        """
        local_zip_file_name = 'workflow_{}_project'.format(workflow_snapshot_id)
        oss_object_key = remote_path
        if local_path is not None:
            tmp_dir = Path(local_path)
        elif self._local_repo is not None:
            tmp_dir = Path(self._local_repo)
        else:
            tmp_dir = Path(tempfile.gettempdir())
        local_zip_file_path = str(tmp_dir / local_zip_file_name) + '.zip'
        self.bucket.get_object_to_file(oss_object_key, filename=local_zip_file_path)
        with zipfile.ZipFile(local_zip_file_path, 'r') as zip_ref:
            top_dir = os.path.split(zip_ref.namelist()[0])[0]
            extract_path = str(tmp_dir / local_zip_file_name)
            zip_ref.extractall(extract_path)
        downloaded_local_path = Path(extract_path) / top_dir
        return str(downloaded_local_path)
