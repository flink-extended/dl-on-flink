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
from typing import Dict, Text, Optional
from ai_flow.meta.job_meta import ExecutionMode
from ai_flow.common.json_utils import Jsonable
from ai_flow.project.project_config import ProjectConfig


class JobContext(Jsonable):
    def __init__(self, execution_mode: ExecutionMode = ExecutionMode.BATCH) -> None:
        super().__init__()
        self.execution_mode = execution_mode
        self.job_uuid = None
        self.job_name = None
        self.job_instance_id = None
        self.workflow_execution_id: int = None
        self.properties: Dict[Text, Jsonable] = {}
        self.project_config: ProjectConfig = None

    def get_execution_mode(self) -> ExecutionMode:
        return self.execution_mode

    def get_property(self, key: Text)->Optional[Jsonable]:
        if key in self.properties:
            return self.properties[key]
        else:
            return None

    def set_property(self, key: Text, value: Jsonable):
        self.properties[key] = value
