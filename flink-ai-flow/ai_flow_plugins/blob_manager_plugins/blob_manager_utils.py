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
import zipfile
import time
import fcntl
from pathlib import Path


def extract_project_zip_file(workflow_snapshot_id,
                             local_root_path,
                             zip_file_path,
                             extract_project_path) -> str:
    """
    :param workflow_snapshot_id: It is the unique identifier for each workflow generation.
    :param local_root_path: It is the root download path.
    :param zip_file_path: It is the project zip file path.
    :param extract_project_path: It is the decompression path of the project zip file.
    :return: The project path.
    """
    lock_file = os.path.join(local_root_path, '{}.lock'.format(workflow_snapshot_id))
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        top_dir = os.path.split(zip_ref.namelist()[0])[0]
        downloaded_local_path = str(Path(extract_project_path) / top_dir)
        if os.path.exists(lock_file):
            while os.path.exists(lock_file):
                time.sleep(1)
            return downloaded_local_path
        else:
            if not os.path.exists(downloaded_local_path):
                f = open(lock_file, 'w')
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    if not os.path.exists(downloaded_local_path):
                        zip_ref.extractall(extract_project_path)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                f.close()
                try:
                    os.remove(lock_file)
                except OSError:
                    pass
            return downloaded_local_path
