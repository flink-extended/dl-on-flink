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
import unittest

from dl_on_flink_framework.context import Context

from dl_on_flink_tensorflow.tf_cluster_config import TFClusterConfig
from tests.flink_ml_tensorflow.utils import add_dl_on_flink_jar

add_dl_on_flink_jar()


class TestTFClusterConfig(unittest.TestCase):

    def test_set_node_entry(self):
        builder = TFClusterConfig.new_builder()
        builder.set_node_entry(entry) \
            .set_worker_count(1)
        config = builder.build()
        self.assertEqual(__file__, config.get_entry_python_file_path())
        self.assertEqual("entry", config.get_entry_func_name())

    def test_add_node_type(self):
        builder = TFClusterConfig.new_builder()
        builder.set_node_entry(entry) \
            .add_node_type("worker", 2) \
            .add_node_type("ps", 3) \
            .add_node_type("worker", 1)

        config = builder.build()
        self.assertEqual(1, config.get_node_count("worker"))
        self.assertEqual(3, config.get_node_count("ps"))

    def test_set_property(self):
        builder = TFClusterConfig.new_builder()
        builder.set_node_entry(entry) \
            .set_worker_count(1) \
            .set_property("k", "v")

        config = builder.build()
        self.assertEqual("v", config.get_property("k"))

    def test_set_worker_ps_count(self):
        builder = TFClusterConfig.new_builder()
        builder.set_node_entry(entry) \
            .set_worker_count(2) \
            .set_ps_count(1)

        config = builder.build()
        self.assertEqual(2, config.get_node_count("worker"))
        self.assertEqual(1, config.get_node_count("ps"))

    def test_set_worker_zero_chief(self):
        builder = TFClusterConfig.new_builder()
        builder.set_node_entry(entry) \
            .set_worker_count(1) \
            .set_is_worker_zero_chief(True)

        config = builder.build()
        self.assertEqual("true", config.get_property("tf_is_worker_zero_chief"))

    def test__to_j_tf_cluster_config(self):
        builder = TFClusterConfig.new_builder()
        builder.set_node_entry(entry) \
            .set_worker_count(2) \
            .set_ps_count(1) \
            .set_property("k", "v") \
            .set_is_worker_zero_chief(True)
        config = builder.build()
        j_tf_cluster_config = config._to_j_tf_cluster_config()

        tf_default_properties = {
            "am_state_machine_class": "org.flinkextended.flink.ml.tensorflow."
                                      "cluster.TFAMStateMachineImpl",
            "sys:ml_runner_class": "org.flinkextended.flink.ml.tensorflow."
                                   "cluster.node.runner.TFMLRunner",
            "sys:record_reader_class": "org.flinkextended.flink.ml.tensorflow."
                                       "data.TFRecordReaderImpl",
            "sys:record_writer_class": "org.flinkextended.flink.ml.tensorflow."
                                       "data.TFRecordWriterImpl"
        }

        self.assertDictEqual({"worker": 2, "ps": 1},
                             dict(j_tf_cluster_config.getNodeTypeCntMap()))
        self.assertDictEqual({**tf_default_properties,
                              "k": "v", "tf_is_worker_zero_chief": "true"},
                             dict(j_tf_cluster_config.getProperties()))
        self.assertEqual(__file__, j_tf_cluster_config.getEntryPythonFilePath())
        self.assertIn(__file__, j_tf_cluster_config.getPythonFilePaths())


def entry(context: Context):
    print(context)
