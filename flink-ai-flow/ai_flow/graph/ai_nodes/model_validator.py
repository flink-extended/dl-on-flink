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
from typing import Text, List
from ai_flow.meta.artifact_meta import ArtifactMeta
from ai_flow.meta.model_meta import ModelMeta, ModelVersionMeta
from ai_flow.common.properties import ExecuteProperties
from ai_flow.executor.executor import BaseExecutor
from ai_flow.graph.ai_nodes.executable import ExecutableNode
from ai_flow.graph.channel import NoneChannel, Channel


class ModelValidator(ExecutableNode):

    def __init__(self,
                 model: ModelMeta,
                 executor: BaseExecutor,
                 model_version_meta: ModelVersionMeta = None,
                 base_model_version_meta: ModelVersionMeta = None,
                 properties: ExecuteProperties = None,
                 name: Text = None,
                 instance_id: Text = None,
                 output_num: int = 0) -> None:
        super().__init__(executor=executor,
                         properties=properties,
                         name=name,
                         instance_id=instance_id,
                         output_num=output_num)
        self.model = model
        self.model_version_meta = model_version_meta
        self.base_model_version_meta = base_model_version_meta

