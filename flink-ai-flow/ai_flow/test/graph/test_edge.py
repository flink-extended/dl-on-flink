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
from ai_flow.graph.edge import Edge


class TestEdge(unittest.TestCase):

    def test_edge_serde(self):
        edge = Edge("a", 'b')
        json_text = json_utils.dumps(edge)
        c2: Edge = json_utils.loads(json_text)
        self.assertEqual(edge.source, c2.source)


if __name__ == '__main__':
    unittest.main()
