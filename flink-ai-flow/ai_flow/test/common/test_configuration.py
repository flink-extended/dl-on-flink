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
import os
from ai_flow.common.configuration import AIFlowConfiguration
from ai_flow.util.path_util import get_file_dir


class TestConfiguration(unittest.TestCase):

    def test_dump_load_configuration(self):
        config = AIFlowConfiguration()
        test_yaml = get_file_dir(__file__) + "/test.yaml"
        config['a'] = 'a'
        config.dump_to_file(test_yaml)
        config.clear()
        config.load_from_file(test_yaml)
        self.assertEqual('a', config['a'])
        if os.path.exists(test_yaml):
            os.remove(test_yaml)


if __name__ == '__main__':
    unittest.main()
