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
import unittest
import os
import shutil
import threading
from ai_flow.util.path_util import get_file_dir
from ai_flow.plugin_interface.blob_manager_interface import BlobConfig, BlobManagerFactory


class TestLocalBlobManager(unittest.TestCase):

    def test_project_upload_download_local(self):
        project_path = get_file_dir(__file__)
        config = {'blob_manager_class': 'ai_flow_plugins.blob_manager_plugins.local_blob_manager.LocalBlobManager'}
        blob_config = BlobConfig(config)
        blob_manager = BlobManagerFactory.create_blob_manager(blob_config.blob_manager_class(),
                                                              blob_config.blob_manager_config())
        uploaded_path = blob_manager.upload_project('1', project_path)
        self.assertEqual(uploaded_path, project_path)

        downloaded_path = blob_manager.download_project('1', uploaded_path)
        self.assertEqual(project_path, downloaded_path)

    def test_project_upload_download_local_2(self):
        project_path = get_file_dir(__file__)
        config = {
            'blob_manager_class': 'ai_flow_plugins.blob_manager_plugins.local_blob_manager.LocalBlobManager',
            'blob_manager_config': {
                'local_repository': '/tmp',
                'remote_repository': '/tmp'
            }
        }
        blob_config = BlobConfig(config)
        blob_manager = BlobManagerFactory.create_blob_manager(blob_config.blob_manager_class(),
                                                              blob_config.blob_manager_config())

        uploaded_path = blob_manager.upload_project('1', project_path)

        downloaded_path = blob_manager.download_project('1', uploaded_path)
        self.assertEqual('/tmp/workflow_1_project/blob_manager_plugins', downloaded_path)

    def test_project_download_local_same_time(self):
        project_path = get_file_dir(__file__)
        upload_path = '/tmp/upload'
        download_path = '/tmp/download'
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        config = {
            'blob_manager_class': 'ai_flow_plugins.blob_manager_plugins.local_blob_manager.LocalBlobManager',
            'blob_manager_config': {
                'local_repository': download_path,
                'remote_repository': upload_path
            }
        }
        blob_config = BlobConfig(config)
        blob_manager = BlobManagerFactory.create_blob_manager(blob_config.blob_manager_class(),
                                                              blob_config.blob_manager_config())

        uploaded_path = blob_manager.upload_project('1', project_path)
        download_project_path = "/tmp/download/workflow_1_project"
        if os.path.exists(download_project_path):
            shutil.rmtree(download_project_path)

        def download_project():
            blob_manager.download_project('1', uploaded_path)

        t1 = threading.Thread(target=download_project, args=())
        t1.setDaemon(True)
        t1.start()
        t2 = threading.Thread(target=download_project, args=())
        t2.setDaemon(True)
        t2.start()
        t1.join()
        t2.join()
        downloaded_path = blob_manager.download_project('1', uploaded_path)
        self.assertEqual('/tmp/download/workflow_1_project/blob_manager_plugins', downloaded_path)
        if os.path.exists(upload_path):
            shutil.rmtree(upload_path)
        if os.path.exists(download_path):
            shutil.rmtree(download_path)


if __name__ == '__main__':
    unittest.main()
