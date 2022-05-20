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

from dl_on_flink_framework.context import Context
from pyflink.common import Row
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, Schema, TableDescriptor

from dl_on_flink_tensorflow.tensorflow_context import TFContext
from dl_on_flink_tensorflow.tf_cluster_config import TFClusterConfig
from dl_on_flink_tensorflow.tf_utils import inference
from tests.flink_ml_tensorflow.utils import find_jar_path


def inference_func(context: Context):
    tf_context = TFContext(context)
    writer = tf_context.get_row_writer_to_flink()
    for i in range(10):
        r = Row(i, i, i * 1.0, i * 1.0, str(f"num:{i}"))
        writer.write(r)

    writer.close()


class TestFlinkRowWriter(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.env.add_jars("file://{}".format(find_jar_path()))
        self.env.set_parallelism(1)
        self.t_env = StreamTableEnvironment.create(self.env)
        self.statement_set = self.t_env.create_statement_set()

    def test_inference(self):
        config = TFClusterConfig.new_builder() \
            .set_worker_count(1) \
            .set_node_entry(inference_func) \
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

        input_table = self.t_env.from_data_stream(self.env.from_collection([]))
        output_table = inference(self.statement_set, input_table, config,
                                 schema)
        self.statement_set.add_insert(TableDescriptor.for_connector("print")
                                      .build(), output_table)
        self.statement_set.execute().wait()
