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
import os
import tempfile
import time
import unittest

from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, TableDescriptor, Schema

from dl_on_flink_tensorflow.tf_cluster_config import TFClusterConfig
from dl_on_flink_tensorflow.tf_utils import train, inference, tensorboard
from tests.flink_ml_tensorflow.utils import add_dl_on_flink_jar, \
    get_resource_folder, find_jar_path

add_dl_on_flink_jar()

from dl_on_flink_tensorflow.tensorflow_on_flink_mlconf import MLCONSTANTS


class TestTFUtils(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.env.add_jars("file://{}".format(find_jar_path()))
        self.env.set_parallelism(1)
        self.t_env = StreamTableEnvironment.create(self.env)
        self.statement_set = self.t_env.create_statement_set()

    def test_train_without_input(self):
        config = TFClusterConfig.new_builder() \
            .set_worker_count(2) \
            .set_ps_count(1) \
            .set_node_entry(os.path.join(get_resource_folder(), "add.py"),
                            "map_func") \
            .build()

        train(self.statement_set, config)

        self.statement_set.execute().wait()

    def testIterationTrain(self):
        source_table = self.t_env.from_data_stream(
            self.env.from_collection([1, 2, 3, 4], Types.INT()))
        config = TFClusterConfig.new_builder() \
            .set_node_entry(os.path.join(get_resource_folder(),
                                         "print_input_iter.py"), "map_func") \
            .set_worker_count(1) \
            .set_property("input_types", "INT_32") \
            .build()
        train(self.statement_set, config, source_table, 4)
        self.statement_set.execute().wait()

    def testIterationTrainWithEarlyTermination(self):
        source_table = self.t_env.from_data_stream(
            self.env.from_collection([1, 2, 3, 4], Types.INT()))
        config = TFClusterConfig.new_builder() \
            .set_node_entry(os.path.join(get_resource_folder(),
                                         "print_input_iter.py"), "map_func") \
            .set_worker_count(1) \
            .set_property("input_types", "INT_32") \
            .build()
        train(self.statement_set, config, source_table, 1024)
        self.statement_set.execute().wait()

    def test_inference(self):
        config = TFClusterConfig.new_builder() \
            .set_worker_count(2) \
            .set_ps_count(1) \
            .set_node_entry(os.path.join(get_resource_folder(),
                                         "input_output.py"),
                            "map_func") \
            .set_property("input_types",
                          "INT_32,INT_64,FLOAT_32,FLOAT_64,STRING") \
            .set_property("output_types",
                          "INT_32,INT_64,FLOAT_32,FLOAT_64,STRING") \
            .build()

        schema = Schema.new_builder() \
            .column("f0", "INT") \
            .column("f1", "BIGINT") \
            .column("f2", "FLOAT") \
            .column("f3", "DOUBLE") \
            .column("f4", "STRING") \
            .build()
        descriptor = TableDescriptor.for_connector("datagen") \
            .schema(schema) \
            .option("number-of-rows", "10") \
            .build()
        input_table = self.t_env.from_descriptor(descriptor)
        output_table = inference(self.statement_set, input_table, config,
                                 schema)
        self.statement_set.add_insert(TableDescriptor.for_connector("print")
                                      .build(), output_table)
        self.statement_set.execute().wait()

    def test_tensorboard(self):
        tmpdir = tempfile.gettempdir()
        config = TFClusterConfig.new_builder() \
            .set_worker_count(2) \
            .set_ps_count(1) \
            .set_node_entry(os.path.join(get_resource_folder(),
                                         "add_withtb.py"), "map_func") \
            .set_property(MLCONSTANTS.CHECKPOINT_DIR,
                          os.path.join(tmpdir, str(time.time_ns()))) \
            .build()

        train(self.statement_set, config)
        tensorboard_config = config.to_builder() \
            .set_node_entry(os.path.join(get_resource_folder(),
                                         "tensorboard.py"), "main") \
            .build()

        tensorboard(self.statement_set, tensorboard_config)
        self.statement_set.execute().wait()
