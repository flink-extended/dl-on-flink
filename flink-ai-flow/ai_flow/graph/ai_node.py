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
from ai_flow.common.properties import ExecuteProperties
from ai_flow.graph.node import BaseNode
from ai_flow.workflow.job import BaseJobConfig


class AINode(BaseNode):
    def __init__(self,
                 name: Text = None,
                 instance_id: Text = None,
                 properties: ExecuteProperties = None,
                 output_num: int = 1) -> None:
        super().__init__(properties=None,
                         name=name,
                         instance_id=instance_id,
                         output_num=output_num)
        if properties is None:
            self.execute_properties = ExecuteProperties()
        else:
            self.execute_properties = properties
        self.properties = self.execute_properties.common_properties
        self.config: BaseJobConfig = BaseJobConfig()
