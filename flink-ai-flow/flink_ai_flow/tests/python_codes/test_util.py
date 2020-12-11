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
from ai_flow.api.configuration import set_project_config_file, project_config
from ai_flow.common import path_util


def get_project_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_master_config_file():
    return get_project_path() + "/master.yaml"


def get_project_config_file():
    return get_project_path() + "/project.yaml"


def set_project_config(main_file):
    set_project_config_file(get_project_config_file())
    project_config()['entry_module_path'] = path_util.get_module_name(main_file)


def get_job_config_file():
    return get_project_path() + "/resources/vvp_flink_config.yaml"
