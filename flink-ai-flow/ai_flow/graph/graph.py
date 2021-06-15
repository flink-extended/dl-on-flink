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
from ai_flow.graph.node import BaseNode
from ai_flow.graph.channel import Channel
from ai_flow.graph.ai_node import AINode
from typing import Dict, List, Text, Optional
from ai_flow.graph.edge import Edge, DataEdge, ControlEdge
from ai_flow.util.json_utils import Jsonable, loads, dumps
import networkx as nx
import matplotlib.pyplot as plt
from ai_flow.api.ai_flow_context import default_af_job_context, ENGINE_NAME
from ai_flow.workflow.job_config import BaseJobConfig

_id_generator_map = {}


def _get_id_generator(graph: object):
    if graph in _id_generator_map:
        return _id_generator_map[graph]
    else:
        _id_generator_map[graph] = _IdGenerator()
        return _id_generator_map[graph]


class _IdGenerator(Jsonable):

    def __init__(self) -> None:
        super().__init__()
        self.node_type_to_num: Dict[Text, int] = {}

    def generate_id(self, node: BaseNode) -> Text:
        node_type = type(node).__name__
        if node_type in self.node_type_to_num:
            num = self.node_type_to_num[node_type]
            self.node_type_to_num[node_type] = num + 1
        else:
            self.node_type_to_num[node_type] = 0
        return node_type + "_" + str(self.node_type_to_num[node_type])


class Graph(BaseNode):

    def __init__(self) -> None:
        super().__init__()
        self.nodes: Dict[Text, BaseNode] = {}
        self.edges: Dict[Text, List[Edge]] = {}

    def add_node(self, node: BaseNode):
        instance_id = _get_id_generator(self).generate_id(node)
        node.set_instance_id(instance_id)
        self.nodes[instance_id] = node

    def add_edge(self, instance_id: Text, edge: Edge):
        if instance_id in self.edges:
            for e in self.edges[instance_id]:
                if e == edge:
                    return
            self.edges[instance_id].append(edge)
        else:
            self.edges[instance_id] = []
            self.edges[instance_id].append(edge)

    def is_in_graph(self, node_id: Text) -> bool:
        return node_id in self.nodes

    def get_node_by_id(self, node_id: Text) -> Optional[BaseNode]:
        if node_id in self.nodes:
            return self.nodes[node_id]
        else:
            return None

    def clear_graph(self):
        self.nodes.clear()
        self.edges.clear()


class AIGraph(Graph):

    def __init__(self) -> None:
        super().__init__()
        self.nodes: Dict[Text, AINode] = {}

    def add_node(self, node: AINode):
        instance_id = _get_id_generator(self).generate_id(node)
        node.set_instance_id(instance_id)
        node.config = default_af_job_context().merge_config()
        node.properties[ENGINE_NAME] = node.config.engine
        self.nodes[instance_id] = node

    def get_node_by_id(self, node_id: Text) -> Optional[AINode]:
        if node_id in self.nodes:
            return self.nodes[node_id]
        else:
            return None

    def add_channel(self, instance_id: Text, channel: Channel):
        edge = DataEdge(source_node_id=instance_id, target_node_id=channel.node_id, port=channel.port)
        self.add_edge(instance_id=instance_id, edge=edge)


_default_ai_graph = AIGraph()


def compile_graph(graph: Graph = _default_ai_graph) -> str:
    return dumps(graph)


def show_graph(graph: Graph = _default_ai_graph) -> None:
    g = nx.Graph()
    for n in graph.edges:
        for e in graph.edges[n]:
            g.add_edge(n, e.target_node_id)

    pos = nx.kamada_kawai_layout(g)  # positions for all ai_nodes
    # ai_nodes
    nx.draw_networkx_nodes(g, pos)
    # edges
    nx.draw_networkx_edges(g, pos, width=1, edge_color='r', arrowsize=10, arrows=True)
    # labels
    nx.draw_networkx_labels(g, pos, font_size=5, font_family='sans-serif')
    plt.axis('off')
    plt.show()


def load_graph(json_text: str) -> Graph:
    graph: Graph = loads(json_text)
    return graph


def default_graph() -> AIGraph:
    return _default_ai_graph


class AISubGraph(AIGraph):

    def __init__(self,
                 config: BaseJobConfig,
                 ) -> None:
        super().__init__()
        self.config: BaseJobConfig = config
        self.edges: Dict[Text, List[DataEdge]] = {}

    def add_node(self, node: AINode):
        self.nodes[node.instance_id] = node


class SplitGraph(AIGraph):
    def __init__(self) -> None:
        super().__init__()
        self.nodes: Dict[Text, AISubGraph] = {}
        self.edges: Dict[Text, List[ControlEdge]] = {}

    def add_node(self, node: AISubGraph):
        instance_id = _get_id_generator(self).generate_id(node)
        node.set_instance_id(instance_id)
        self.nodes[instance_id] = node
