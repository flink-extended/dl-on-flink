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
    An AIGraph represents a user-defined workflow.
    AIGraph consists of AINodes and edges. The edges are of two kinds: the data edge(:class:`~ai_flow.ai_graph.data_edge.DataEdge`) between
    :class:`~ai_flow.ai_graph.ai_node.AINode` in a job and the control edge
    (:class:`~ai_flow.workflow.control_edge.ControlEdge`) between jobs.
    """

    def __init__(self) -> None:
        super().__init__()
        self.nodes: Dict[Text, AINode] = {}

    def add_node(self, node: AINode):
        """
        Adds an :class:`~ai_flow.ai_graph.ai_node.AINode` to AIGraph.

        :param node: :class:`~ai_flow.ai_graph.ai_node.AINode` to add in the graph.
        """
        if current_workflow_config() is not None \
                and current_job_name() is not None \
                and current_job_name() in current_workflow_config().job_configs:
            node.config = current_workflow_config().job_configs.get(current_job_name())
        self.nodes[node.node_id] = node

    def get_node_by_id(self, node_id: Text) -> Optional[AINode]:
        """
        Returns the node whose `node_id` field is node_id.

        :param node_id: id of the :class:`~ai_flow.ai_graph.ai_node.AINode`.
        :return :class:`~ai_flow.ai_graph.ai_node.AINode`.
        """
        if node_id in self.nodes:
            return self.nodes[node_id]
        else:
            return None

    def add_channel(self, node_id: Text, channel: Channel):
        """
        Adds a data edge to AIGraph.

        :param node_id: node_id of the data receiving node.
        :param channel: An output of the data sending node.
        """
        edge = DataEdge(destination=node_id, source=channel.node_id, port=channel.port)
        self.add_edge(node_id=node_id, edge=edge)


__current_ai_graph__ = AIGraph()


def current_graph() -> AIGraph:
    """
    Returns the current AIGraph.

    :return :class:`~ai_flow.ai_graph.ai_graph.AIGraph`.
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
    It consists of a set of ai nodes(:class:`~ai_flow.ai_graph.ai_node.AINode`),
    all :class:`~ai_flow.ai_graph.ai_node.AINode` in sub-graph share the same job configuration
    (:class:`~ai_flow.workflow.job_config.JobConfig`).
    """

    def __init__(self,
                 config: JobConfig,
                 ) -> None:
        """
        :param config: :class:`~ai_flow.workflow.job_config.JobConfig` of the job represented by the sub-graph.
        """
        super().__init__()
        self.config: JobConfig = config
        self.edges: Dict[Text, List[DataEdge]] = {}

    def add_node(self, node: AINode):
        """
        Adds an :class:`~ai_flow.ai_graph.ai_node.AINode` to AISubGraph.

        :param node: :class:`~ai_flow.ai_graph.ai_node.AINode` to add in the sub-graph.
        """
        self.nodes[node.node_id] = node
