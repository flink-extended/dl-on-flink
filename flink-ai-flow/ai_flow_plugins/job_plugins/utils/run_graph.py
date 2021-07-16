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
from typing import List, Dict, Text

from ai_flow.ai_graph.ai_graph import AISubGraph
from ai_flow.ai_graph.ai_node import AINode
from ai_flow.ai_graph.data_edge import DataEdge
from ai_flow.util import json_utils


class RunGraph(json_utils.Jsonable):
    """
    RunGraph consists of AINode, Processor and each AINode dependent data edge arranged in the order of execution.
    """
    def __init__(self) -> None:
        super().__init__()
        self.nodes: List[AINode] = []
        self.processor_bytes: List[bytes] = []
        self.dependencies: Dict[Text, List[DataEdge]] = {}


def build_run_graph(sub_graph: AISubGraph) -> RunGraph:
    run_graph = RunGraph()
    processed_nodes = set()
    node_list: List[AINode] = []
    for n in sub_graph.nodes.values():
        node_list.append(n)
    for e in sub_graph.edges:
        data_channel_list = []
        for c in sub_graph.edges[e]:
            cc: DataEdge = c
            data_channel_list.append(cc)
        run_graph.dependencies[e] = data_channel_list

    node_size = len(sub_graph.nodes)
    processed_size = len(processed_nodes)
    while processed_size != node_size:
        p_nodes = []
        for i in range(len(node_list)):
            if node_list[i].node_id in sub_graph.edges:
                flag = True
                for c in sub_graph.edges[node_list[i].node_id]:
                    if c.source in processed_nodes:
                        pass
                    else:
                        flag = False
                        break
            else:
                flag = True
            if flag:
                p_nodes.append(node_list[i])
        if 0 == len(p_nodes):
            raise Exception("graph has circle!")
        for n in p_nodes:
            run_graph.nodes.append(n)
            run_graph.processor_bytes.append(n.processor)
            node_list.remove(n)
            processed_nodes.add(n.node_id)
        processed_size = len(processed_nodes)
    return run_graph
