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
from enum import Enum
from typing import Text
from ai_flow.util.json_utils import Jsonable


class ModelVersionMeta(Jsonable):
    def __init__(self,
                 version: Text,
                 model_id: int,
                 model_path: Text = None,
                 model_metric: Text = None,
                 model_flavor: Text = None,
                 workflow_execution_id: int = None,
                 version_desc: Text = None,
                 current_stage: Text = None
                 ) -> None:
        self.version = version
        self.model_id = model_id
        self.model_path = model_path
        self.model_metric = model_metric
        self.model_flavor = model_flavor
        self.workflow_execution_id = workflow_execution_id
        self.version_desc = version_desc
        self.current_stage = current_stage


def create_model_version(version: Text,
                         model_id: int,
                         model_path: Text = None,
                         model_metric: Text = None,
                         model_flavor: Text = None,
                         workflow_execution_id: int = None,
                         version_desc: Text = None,
                         current_stage: Text = None):
    return ModelVersionMeta(version=version, model_id=model_id, model_path=model_path, model_metric=model_metric,
                            model_flavor=model_flavor, workflow_execution_id=workflow_execution_id,
                            version_desc=version_desc, current_stage=current_stage)


class ModelMeta(Jsonable):
    def __init__(self,
                 name: Text,
                 model_type: Text,
                 model_desc: Text = None,
                 project_id: Text = None,
                 uuid: int = None
                 ) -> None:
        self.name = name
        self.model_type = model_type
        self.model_desc = model_desc
        self.project_id = project_id
        self.uuid = uuid


def create_model(name: Text,
                 model_type: Text,
                 model_desc: Text = None,
                 project_id: Text = None) -> ModelMeta:
    return ModelMeta(name, model_type, model_desc, project_id)


class ModelType(str, Enum):
    CHECKPOINT = 'CHECKPOINT'
    SAVED_MODEL = 'SAVED_MODEL'
    H5 = 'H5'
