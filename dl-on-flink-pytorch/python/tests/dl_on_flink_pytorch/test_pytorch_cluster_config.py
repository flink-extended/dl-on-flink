#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import unittest

from dl_on_flink_framework.context import Context

from dl_on_flink_pytorch.pytorch_cluster_config import PytorchClusterConfig
from tests.dl_on_flink_pytorch.utils import add_dl_on_flink_jar

add_dl_on_flink_jar()


class TestPytorchClusterConfig(unittest.TestCase):

    def test_set_world_size(self):
        builder = PytorchClusterConfig.new_builder()
        builder.set_node_entry(entry) \
            .set_world_size(2)
        config = builder.build()
        self.assertEqual(2, config.get_node_count("worker"))

    def test__to_j_pytorch_cluster_config(self):
        builder = PytorchClusterConfig.new_builder()
        builder.set_node_entry(entry) \
            .set_world_size(2) \
            .set_property("k", "v")

        config = builder.build()
        j_pytorch_cluster_config = config._to_j_pytorch_cluster_config()

        pytorch_default_properties = {
            "sys:ml_runner_class":
                "org.flinkextended.flink.ml.pytorch.PyTorchRunner",
            "sys:decoding_class":
                "org.flinkextended.flink.ml.operator.coding.RowCSVCoding",
            "sys:encoding_class":
                "org.flinkextended.flink.ml.operator.coding.RowCSVCoding"
        }

        self.assertDictEqual({"worker": 2},
                             dict(j_pytorch_cluster_config.getNodeTypeCntMap()))
        self.assertDictEqual({**pytorch_default_properties,
                              "k": "v"},
                             dict(j_pytorch_cluster_config.getProperties()))
        self.assertEqual(__file__,
                         j_pytorch_cluster_config.getEntryPythonFilePath())
        self.assertIn(__file__, j_pytorch_cluster_config.getPythonFilePaths())


def entry(context: Context):
    print(context)
