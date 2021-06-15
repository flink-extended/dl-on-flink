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
from ai_flow.graph.edge import DataEdge


class TestEdge(unittest.TestCase):

    def test_json(self):
        channel = DataEdge("a", 0)
        json_text = json_utils.dumps(channel)
        c2: DataEdge = json_utils.loads(json_text)
        self.assertEqual(channel.target_node_id, c2.target_node_id)
        self.assertEqual(channel.port, c2.port)


if __name__ == '__main__':
    unittest.main()
