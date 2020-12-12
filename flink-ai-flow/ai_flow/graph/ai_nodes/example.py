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
from typing import List, Optional
from ai_flow.graph.ai_node import AINode
from ai_flow.meta.example_meta import ExampleMeta
from ai_flow.graph.channel import Channel
from ai_flow.common.properties import ExecuteProperties
from ai_flow.executor.executor import PythonObjectExecutor


class Example(AINode):
    """define example node """

    def __init__(self,
                 example_meta: ExampleMeta,
                 executor: Optional[PythonObjectExecutor] = None,
                 is_source: bool = True,
                 instance_id=None,
                 properties: ExecuteProperties = None) -> None:
        """ create example object
        Args:
            example_meta:
        """
        super().__init__(properties=properties,
                         name=example_meta.name,
                         instance_id=instance_id,
                         output_num=1)
        self.example_meta = example_meta
        self.is_source = is_source
        self.executor = executor

    def outputs(self) -> List[Channel]:
        return [Channel(node_id=self.instance_id, port=0)]
