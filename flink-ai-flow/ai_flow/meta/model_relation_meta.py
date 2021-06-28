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
from typing import Text

from ai_flow.util.json_utils import Jsonable


class ModelRelationMeta(Jsonable):
    def __init__(self,
                 name: Text,
                 project_id: int,
                 uuid: int = None):
        self.name = name
        self.project_id = project_id
        self.uuid = uuid

    def __str__(self):
        return '<\n' \
               'ModelRelation\n' \
               'uuid:{}\n' \
               'name:{},\n' \
               'project_id:{}\n' \
               '>'.format(
            self.uuid, self.name, self.project_id)


class ModelVersionRelationMeta(Jsonable):
    def __init__(self,
                 version: Text,
                 model_id: int,
                 project_snapshot_id: int):
        self.version = version
        self.model_id = model_id
        self.project_snapshot_id = project_snapshot_id

    def __str__(self):
        return '<\n' \
               'ModelVersionRelation\n' \
               'version:{},\n' \
               'model_id:{},\n' \
               'project_snapshot_id:{}\n' \
               '>'.format(self.version, self.model_id, self.project_snapshot_id)


def create_model_relation(name: Text,
                          project_id: int):
    return ModelRelationMeta(name=name, project_id=project_id)


def create_model_version_relation(version: Text,
                                  model_id: int,
                                  project_snapshot_id: int):
    return ModelVersionRelationMeta(version=version, model_id=model_id, project_snapshot_id=project_snapshot_id)
