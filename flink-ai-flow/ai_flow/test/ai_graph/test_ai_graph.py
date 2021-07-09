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
import unittest
from ai_flow.graph.channel import Channel
from ai_flow.ai_graph.ai_node import AINode
from ai_flow.ai_graph.ai_graph import current_graph, add_ai_node_to_graph


class TestAIGraph(unittest.TestCase):

    def test_add_ai_node_to_graph(self):
        node1 = AINode(processor=None, arg1='arg1_1', arg2='arg2_1')
        add_ai_node_to_graph(node1, inputs=None)
        node2 = AINode(processor=None, arg1='arg1_2', arg2='arg2_2')
        add_ai_node_to_graph(node2, inputs=None)
        node3 = AINode(processor=None, arg1='arg1_3', arg2='arg2_3')
        add_ai_node_to_graph(node3, inputs=[Channel(node1.node_id, 0), Channel(node2.node_id, 0)])
        self.assertEqual(3, len(current_graph().nodes))
        self.assertEqual(1, len(current_graph().edges))


if __name__ == '__main__':
    unittest.main()
