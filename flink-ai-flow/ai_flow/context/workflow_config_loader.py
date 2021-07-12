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
from typing import Text
from ai_flow.workflow.workflow_config import WorkflowConfig, load_workflow_config

__current_workflow_config__ = WorkflowConfig()


def init_workflow_config(workflow_config_file: Text):
    """
    Load the workflow configuration(ai_flow.workflow.workflow_config.WorkflowConfig) of the current workflow.
    """
    global __current_workflow_config__
    __current_workflow_config__ = load_workflow_config(workflow_config_file)


def current_workflow_config() -> WorkflowConfig:
    """
    return: the workflow configuration of the current workflow.
    """
    return __current_workflow_config__


def set_current_workflow_config(workflow_config):
    global __current_workflow_config__
    __current_workflow_config__ = workflow_config
