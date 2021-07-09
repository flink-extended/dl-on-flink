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
from typing import Text, List, Union, Dict
from ai_flow.common.properties import Properties
from ai_flow.util.json_utils import Jsonable
from ai_flow.graph.channel import Channel


class _IdGenerator(Jsonable):

    def __init__(self) -> None:
        super().__init__()
        self.node_type_to_num: Dict[Text, int] = {}

    def generate_id(self, node) -> Text:
        node_type = type(node).__name__
        if node_type in self.node_type_to_num:
            self.node_type_to_num[node_type] += 1
        else:
            self.node_type_to_num[node_type] = 0
        return node_type + "_" + str(self.node_type_to_num[node_type])


__id_generator__ = _IdGenerator()


def _get_id_generator():
    return __id_generator__


class Node(Jsonable):
    """abstract node"""
    def __init__(self,
                 name: Text = None,
                 properties: Properties = None,
                 output_num: int = 0) -> None:
        """
        :param name: the node name
        :param properties: node properties
        :param output_num: the node output number
        """
        super().__init__()
        self.name = name
        if properties is None:
            self.properties = Properties()
        else:
            self.properties = properties
        self.node_id = _get_id_generator().generate_id(self)
        self.output_num = output_num

    def outputs(self) -> Union[None, List[Channel]]:
        return None
