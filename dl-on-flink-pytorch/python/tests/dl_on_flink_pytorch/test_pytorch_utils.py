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
import importlib.util
import os
import sys
import unittest

from pyflink.common import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, Schema, TableDescriptor

from dl_on_flink_pytorch.pytorch_cluster_config import PytorchClusterConfig
from dl_on_flink_pytorch.pytorch_utils import inference, train
from tests.dl_on_flink_pytorch.utils import find_jar_path, get_resource_folder


def _get_entry(path, func_name):
    spec = importlib.util.spec_from_file_location(path, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[path] = module
    spec.loader.exec_module(module)
    return getattr(module, func_name)


class TestPytorchUtils(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.env.add_jars("file://{}".format(find_jar_path()))
        self.env.set_parallelism(1)
        self.t_env = StreamTableEnvironment.create(self.env)
        self.statement_set = self.t_env.create_statement_set()

    def test_train_without_input(self):
        config = PytorchClusterConfig.new_builder() \
            .set_world_size(3) \
            .set_node_entry(
            _get_entry(os.path.join(get_resource_folder(), "all_gather.py"),
                       "main")) \
            .build()

        train(self.statement_set, config)

        self.statement_set.execute().wait()

    def testTrainWithInput(self):
        source_table = self.t_env.from_data_stream(
            self.env.from_collection([1, 2, 3, 4], Types.INT()))
        config = PytorchClusterConfig.new_builder() \
            .set_node_entry(_get_entry(os.path.join(get_resource_folder(),
                                                    "with_input.py"),
                                       "main")) \
            .set_world_size(2) \
            .set_property("input_types", "INT_32") \
            .build()
        train(self.statement_set, config, source_table)
        self.statement_set.execute().wait()

    def testIterationTrain(self):
        source_table = self.t_env.from_data_stream(
            self.env.from_collection([1, 2, 3, 4], Types.INT()).map(
                lambda i: i, Types.INT()).set_parallelism(2))
        config = PytorchClusterConfig.new_builder() \
            .set_node_entry(_get_entry(os.path.join(get_resource_folder(),
                                                    "with_input_iter.py"),
                                       "main")) \
            .set_world_size(2) \
            .set_property("input_types", "INT_32") \
            .build()
        train(self.statement_set, config, source_table, 4)
        self.statement_set.execute().wait()

    def testIterationTrainWithEarlyTermination(self):
        source_table = self.t_env.from_data_stream(
            self.env.from_collection([1, 2, 3, 4], Types.INT()).map(
                lambda i: i, Types.INT()).set_parallelism(2))
        config = PytorchClusterConfig.new_builder() \
            .set_node_entry(_get_entry(os.path.join(get_resource_folder(),
                                                    "with_input_iter.py"),
                                       "main")) \
            .set_world_size(2) \
            .set_property("input_types", "INT_32") \
            .build()
        train(self.statement_set, config, source_table, 1024)
        self.statement_set.execute().wait()

    def test_inference(self):
        config = PytorchClusterConfig.new_builder() \
            .set_world_size(2) \
            .set_node_entry(_get_entry(os.path.join(get_resource_folder(),
                                                    "inference.py"),
                                       "main")) \
            .set_property("input_types",
                          "INT_32") \
            .set_property("output_types",
                          "INT_32,INT_32") \
            .build()

        schema = Schema.new_builder() \
            .column("f0", "INT") \
            .column("f1", "INT") \
            .build()
        source_table = self.t_env.from_data_stream(
            self.env.from_collection([1, 2, 3, 4], Types.INT()))
        output_table = inference(self.statement_set, source_table, config,
                                 schema)
        self.statement_set.add_insert(TableDescriptor.for_connector("print")
                                      .build(), output_table)
        self.statement_set.execute().wait()
