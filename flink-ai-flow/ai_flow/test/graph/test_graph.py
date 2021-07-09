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
import unittest

from ai_flow.util import json_utils
from ai_flow.graph.node import Node
from ai_flow.graph.edge import Edge
from ai_flow.graph.graph import Graph


class TestGraph(unittest.TestCase):

    def test_graph_serde(self):
        graph = Graph()
        nodes = []
        for i in range(3):
            node = Node(name=str(i))
            graph.add_node(node)
            nodes.append(node)
        edge = Edge(destination=nodes[0].node_id, source=nodes[1].node_id)
        graph.add_edge(nodes[0].node_id, edge)
        edge = Edge(destination=nodes[0].node_id, source=nodes[2].node_id)
        graph.add_edge(nodes[0].node_id, edge)
        json_text = json_utils.dumps(graph)
        g: Graph = json_utils.loads(json_text)
        self.assertEqual(3, len(g.nodes))
        self.assertEqual(2, len(graph.edges.get(nodes[0].node_id)))


if __name__ == '__main__':
    unittest.main()
