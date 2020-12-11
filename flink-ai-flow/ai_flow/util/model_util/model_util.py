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
import uuid
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path

from typing import Text, Dict

import oss2

from ai_flow.util.file_util.zip_file_util import make_dir_zipfile, make_file_zipfile


class ModelMananger(ABC):

    @abstractmethod
    def download_model(self, remote_path, local_path=None):
        pass

    @abstractmethod
    def save_model(self, local_path, remote_path=None):
        pass


class OSSModelManager(ModelMananger):

    def __init__(self, config: Dict[Text, Text]):
        ack_id = config.get('blob_server.access_key_id', None)
        ack_secret = config.get('blob_server.access_key_secret', None)
        endpoint = config.get('blob_server.endpoint', None)
        bucket_name = config.get('blob_server.bucket', None)
        auth = oss2.Auth(ack_id, ack_secret)
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)

    def download_model(self, remote_path, local_path=None):
        """
        download an uploaded model in Aliyun OSS.
        :param remote_path: the object key of the file in oss.
        :param local_path: the user specified local path of the downloaded file. the local_path must be a directory
        :return: the downloaded file path.
        """
        if local_path is not None:
            local_file_dir = local_path
        else:
            local_file_dir = 'tmp_model-' + str(uuid.uuid1())
        tmp_dir = Path(tempfile.gettempdir())
        tmp_zip_file = str(tmp_dir / local_file_dir) + '.zip'
        oss_object_key = remote_path
        self.bucket.get_object_to_file(key=oss_object_key, filename=tmp_zip_file)
        with zipfile.ZipFile(tmp_zip_file, 'r') as zip_ref:
            top_name = zip_ref.namelist()[0]
            extract_path = str(tmp_dir / local_file_dir)
            zip_ref.extractall(extract_path)
        downloaded_local_path = Path(extract_path) / top_name
        return str(downloaded_local_path)

    def save_model(self, local_path, remote_path=None) -> Text:
        """
        save a local export model to remote storage(Aliyun OSS)
        :param local_path: the local path of the model, the oss storage only supports binary files, thus we have to
        make the local path file a zip.
        :param remote_path: the object_key of the uploaded file in oss with the pattern like abc/efg/123.jpg
        :return: the object_key of uploaded file.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = Path(local_path)
            zip_file_name = os.path.splitext(local_path.name)[0] + '.zip'
            temp_dir_path = Path(temp_dir)
            zip_file_path = temp_dir_path / zip_file_name
            if local_path.is_dir():
                make_dir_zipfile(str(local_path), zip_file_path)
            else:
                make_file_zipfile(str(local_path), zip_file_path)
            if remote_path is None:
                object_key = 'ai-flow-model-manager/' + zip_file_name
            else:
                object_key = remote_path
            self.bucket.put_object_from_file(key=object_key, filename=str(zip_file_path))
        return object_key
