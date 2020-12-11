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
from ai_flow.common.properties import Properties
from ai_flow.common.json_utils import Jsonable
from ai_flow.graph.channel import Channel, NoneChannel


class BaseNode(Jsonable):
    """abstract node"""
    def __init__(self,
                 name: Text = None,
                 instance_id: Text = None,
                 properties: Properties = None,
                 output_num: int = 1) -> None:
        """

        :param name: the node name
        :param instance_id: the identity of node
        :param properties: node properties
        :param output_num: the node output number
        """
        super().__init__()
        self.name = name
        if properties is None:
            self.properties = Properties()
        else:
            self.properties = properties
        self.instance_id = instance_id
        self.output_num = output_num

    def set_instance_id(self, instance_id: Text):
        self.instance_id = instance_id
        if self.name is None or len(self.name) == 0:
            self.name = instance_id

    def outputs(self) -> List[Channel]:
        return [NoneChannel(self.instance_id)]
