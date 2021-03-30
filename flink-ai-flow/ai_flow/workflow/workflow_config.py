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
from typing import Dict, Text, Any
from ai_flow.common.json_utils import Jsonable, loads
from ai_flow.workflow.job_config import BaseJobConfig, get_job_config_class
from ai_flow.common import yaml_utils


GLOBAL_CONFIG_KEY = "global_config_key"
WORKFLOW_NAME = "workflow_name"


class WorkFlowConfig(Jsonable):

    def __init__(self) -> None:
        super().__init__()
        self.name = None
        self.job_configs: Dict[Text, BaseJobConfig] = {}

    def add_job_config(self, config_key: Text, job_config: BaseJobConfig):
        self.job_configs[config_key] = job_config

    def set_upload_project_path_for_jobs(self, uploaded_project_path: Text):
        for job_id, job_config in self.job_configs.items():
            job_config.project_path = uploaded_project_path

    def set_properties_for_jobs(self, properties: Dict[str, Any]):
        for job_id, job_config in self.job_configs.items():
            job_config.properties.update(properties)


def load_workflow_config(config_path: Text) -> WorkFlowConfig:
    if config_path.endswith('.json'):
        with open(config_path, 'r') as f:
            workflow_config_json = f.read()
        workflow_config: WorkFlowConfig = loads(workflow_config_json)
        return workflow_config
    elif config_path.endswith('.yaml'):
        workflow_data = yaml_utils.load_yaml_file(config_path)
        workflow_config: WorkFlowConfig = WorkFlowConfig()
        for k, v in workflow_data.items():
            if k == GLOBAL_CONFIG_KEY:
                continue
            elif k == WORKFLOW_NAME:
                workflow_config.name = v
                continue
            job_config_class = get_job_config_class(v['platform'], v['engine'])
            job_config = job_config_class()
            job_config_class.from_dict(v, job_config)
            workflow_config.add_job_config(k, job_config)
        return workflow_config
    else:
        return None
