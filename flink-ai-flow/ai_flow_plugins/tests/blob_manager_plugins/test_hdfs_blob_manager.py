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
from ai_flow.util.path_util import get_file_dir
from ai_flow.plugin_interface.blob_manager_interface import BlobManagerFactory


class TestOSSBlobManager(unittest.TestCase):

    @unittest.skipUnless((os.environ.get('blob_server.hdfs_url') is not None
                          and os.environ.get('blob_server.hdfs_user') is not None
                          and os.environ.get('blob_server.repo_name') is not None), 'need set hdfs')
    def test_project_upload_download_oss(self):
        project_path = get_file_dir(__file__)
        config = {
            'blob_manager_class': 'ai_flow_plugins.blob_manager_plugins.hdfs_blob_manager.HDFSBlobManager',
            'local_repository': '/tmp',
            'hdfs_url': os.environ.get('hdfs_url'),
            'hdfs_user': os.environ.get('hdfs_user'),
            'repo_name': os.environ.get('repo_name')
        }

        blob_manager = BlobManagerFactory.get_blob_manager(config)
        uploaded_path = blob_manager.upload_project('1', project_path)

        downloaded_path = blob_manager.download_project('1', uploaded_path)
        self.assertEqual('/tmp/workflow_1_project/project', downloaded_path)


if __name__ == '__main__':
    unittest.main()
