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
    """
    Nodes are part of the graph(ai_flow.graph.graph.Graph),
    and there are edges(ai_flow.graph.edge.Edge) connected between nodes
    """
    def __init__(self,
                 name: Text = None,
                 properties: Properties = None,
                 output_num: int = 0) -> None:
        """
        :param name: the name of Node
        :param properties: node properties
        :param output_num: each node has outputs, this represents the number of outputs
        """
        super().__init__()
        self.name = name
        if properties is None:
            self.properties = Properties()
        else:
            self.properties = properties
        # node_id is the unique identifier of the node.
        self.node_id = _get_id_generator().generate_id(self)
        self.output_num = output_num

    def outputs(self) -> Union[None, List[Channel]]:
        """
        Return: The outputs(ai_flow.graph.channel.Channel) of the node.
        """
        return None
