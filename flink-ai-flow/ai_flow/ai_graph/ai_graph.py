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
from ai_flow.graph.graph import Graph
from ai_flow.graph.channel import Channel
from ai_flow.ai_graph.ai_node import AINode
from typing import Dict, List, Text, Optional, Union
from ai_flow.ai_graph.data_edge import DataEdge
from ai_flow.workflow.job_config import JobConfig
from ai_flow.context.workflow_config_loader import current_workflow_config
from ai_flow.context.job_context import current_job_name


class AIGraph(Graph):
    """
    The program defined by ai flow will be represented by AIGraph.
    AIGraph consists of AINode and edges.
    AIGraph contains two kinds of edges, the data edge(ai_flow.ai_graph.data_edge.DataEdge) between AINodes in a job
    and the control edge between(ai_flow.workflow.control_edge.ControlEdge) jobs
    """

    def __init__(self) -> None:
        super().__init__()
        self.nodes: Dict[Text, AINode] = {}

    def add_node(self, node: AINode):
        """
        Add an ai node(ai_flow.ai_graph.ai_node.AINode) to AIGraph.
        """
        if current_workflow_config() is not None \
                and current_job_name() is not None \
                and current_job_name() in current_workflow_config().job_configs:
            node.config = current_workflow_config().job_configs.get(current_job_name())
        self.nodes[node.node_id] = node

    def get_node_by_id(self, node_id: Text) -> Optional[AINode]:
        """
        Return the node whose node_id field is node_id.
        """
        if node_id in self.nodes:
            return self.nodes[node_id]
        else:
            return None

    def add_channel(self, node_id: Text, channel: Channel):
        """
        Add a data edge to AIGraph.
        :param node_id: node_id of the data receiving node.
        :param channel: An output of the data sending node.
        """
        edge = DataEdge(destination=node_id, source=channel.node_id, port=channel.port)
        self.add_edge(node_id=node_id, edge=edge)


__current_ai_graph__ = AIGraph()


def current_graph() -> AIGraph:
    """
    Return the current AIGraph.
    """
    return __current_ai_graph__


def add_ai_node_to_graph(node, inputs: Union[None, Channel, List[Channel]]):
    current_graph().add_node(node)
    if isinstance(inputs, Channel):
        current_graph().add_channel(node_id=node.node_id, channel=inputs)

    elif isinstance(inputs, List):
        for c in inputs:
            current_graph().add_channel(node_id=node.node_id, channel=c)


class AISubGraph(AIGraph):
    """
    It consists of a set of ai nodes(ai_flow.ai_graph.ai_node.AINode),
    all ai nodes have the same job configuration(ai_flow.workflow.job_config.JobConfig)
    """
    def __init__(self,
                 config: JobConfig,
                 ) -> None:
        super().__init__()
        self.config: JobConfig = config
        self.edges: Dict[Text, List[DataEdge]] = {}

    def add_node(self, node: AINode):
        self.nodes[node.node_id] = node
