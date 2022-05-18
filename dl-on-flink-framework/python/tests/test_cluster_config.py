#  Copyright 2022 Deep Learning on Flink Authors
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import unittest

from dl_on_flink_framework.cluster_config import ClusterConfig
from dl_on_flink_framework.context import Context


class TestClusterConfig(unittest.TestCase):

    def test_set_node_entry(self):
        builder = ClusterConfig.new_builder()
        builder.set_node_entry(entry)
        config = builder.build()
        self.assertEqual(__file__, config.get_entry_python_file_path())
        self.assertEqual("entry", config.get_entry_func_name())

    def test_add_node_type(self):
        builder = ClusterConfig.new_builder()
        builder.set_node_entry(entry) \
            .add_node_type("worker", 2) \
            .add_node_type("ps", 3) \
            .add_node_type("worker", 1)

        config = builder.build()
        self.assertDictEqual({"worker": 1, "ps": 3},
                             config.get_node_type_cnt_map())
        self.assertEqual(1, config.get_node_count("worker"))
        self.assertEqual(3, config.get_node_count("ps"))

    def test_set_property(self):
        builder = ClusterConfig.new_builder()
        builder.set_node_entry(entry) \
            .set_property("k", "v")

        config = builder.build()
        self.assertDictEqual({"k": "v"}, config.get_properties())
        self.assertEqual("v", config.get_property("k"))


def entry(context: Context):
    print(context)
