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
from typing import Dict, Text
from ai_flow.util.json_utils import Jsonable, loads
from ai_flow.workflow.job_config import JobConfig
from ai_flow.workflow.periodic_config import PeriodicConfig
from ai_flow.util import yaml_utils

WORKFLOW_PROPERTIES = "properties"  # The configuration item that represents the properties of the workflow.
WORKFLOW_DEPENDENCIES = "dependencies"  # The configuration item of the workflow represents the dependency files.
PERIODIC_CONFIG = "periodic_config"  # The configuration item of the workflow represents the workflow periodic running.


class WorkflowConfig(Jsonable):
    """WorkflowConfig is the configuration information of the Workflow(ai_flow.workflow.workflow.Workflow)."""

    def __init__(self, workflow_name: Text = None) -> None:
        super().__init__()
        self.workflow_name = workflow_name
        self.job_configs: Dict[Text, JobConfig] = {}
        self.properties: Dict[Text, Jsonable] = {}
        self.dependencies: Dict = None
        self.periodic_config: PeriodicConfig = None
        self.job_periodic_config_dict: Dict[Text, PeriodicConfig] = {}

    def add_job_config(self, config_key: Text, job_config: JobConfig):
        self.job_configs[config_key] = job_config


def load_workflow_config(config_path: Text) -> WorkflowConfig:
    """
    Load the workflow configuration file.
    :param config_path: Workflow configuration file path.
    return: WorkflowConfig.
    """
    if config_path.endswith('.json'):
        with open(config_path, 'r') as f:
            workflow_config_json = f.read()
        workflow_config: WorkflowConfig = loads(workflow_config_json)
        return workflow_config
    elif config_path.endswith('.yaml'):
        # -5 is length of .yaml; The config file name equals workflow name.
        workflow_name = os.path.basename(config_path)[:-5]
        workflow_data = yaml_utils.load_yaml_file(config_path)

        workflow_config: WorkflowConfig = WorkflowConfig(workflow_name=workflow_name)

        if PERIODIC_CONFIG in workflow_data:
            p_data = workflow_data.get(PERIODIC_CONFIG)
            workflow_config.periodic_config = PeriodicConfig.from_dict(p_data)

        if WORKFLOW_PROPERTIES in workflow_data:
            workflow_config.properties = workflow_data[WORKFLOW_PROPERTIES]

        if WORKFLOW_DEPENDENCIES in workflow_data:
            workflow_config.dependencies = workflow_data[WORKFLOW_DEPENDENCIES]

        for k, v in workflow_data.items():
            if k == WORKFLOW_DEPENDENCIES or k == WORKFLOW_PROPERTIES or k == PERIODIC_CONFIG:
                continue
            job_config = JobConfig.from_dict({k: v})
            workflow_config.add_job_config(k, job_config)
            if PERIODIC_CONFIG in v:
                p_data = v.get(PERIODIC_CONFIG)
                periodic_config = PeriodicConfig.from_dict(p_data)
                workflow_config.job_periodic_config_dict[k] = periodic_config
        return workflow_config
    else:
        return None
