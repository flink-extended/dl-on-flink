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
import os
import time
import unittest

import tensorflow as tf
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, Schema, DataTypes, \
    expressions as expr, TableDescriptor

from dl_on_flink_tensorflow.flink_ml.tf_estimator import TFEstimator, TFModel
from tests.flink_ml_tensorflow.utils import add_dl_on_flink_jar, find_jar_path


class TestTFEstimator(unittest.TestCase):

    def setUp(self) -> None:
        add_dl_on_flink_jar()
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.env.add_jars("file://{}".format(find_jar_path()))
        self.t_env = StreamTableEnvironment.create(self.env)
        self.statement_set = self.t_env.create_statement_set()

    def test_fit_with_all_types(self):
        schema = Schema.new_builder() \
            .column("x1", DataTypes.STRING()) \
            .column("x2", DataTypes.INT()) \
            .column("x3", DataTypes.BIGINT()) \
            .column("x4", DataTypes.FLOAT()) \
            .column("x5", DataTypes.DOUBLE()) \
            .column_by_expression("y", expr.call_sql("2 * x2")) \
            .build()
        input_table = self.t_env.from_descriptor(TableDescriptor
                                                 .for_connector("datagen")
                                                 .schema(schema)
                                                 .option('number-of-rows',
                                                         '100')
                                                 .option('fields.x2.min', '0')
                                                 .option('fields.x2.max', '100')
                                                 .build())

        def select_inputs(inputs):
            import tensorflow as tf
            inputs = tf.keras.backend.print_tensor(inputs)
            return tf.cast(inputs[1], tf.float32)

        input1 = tf.keras.Input(shape=(1,), dtype=tf.string, name="x1")
        input2 = tf.keras.Input(shape=(1,), dtype=tf.int32, name="x2")
        input3 = tf.keras.Input(shape=(1,), dtype=tf.int64, name="x3")
        input4 = tf.keras.Input(shape=(1,), dtype=tf.float32, name="x4")
        input5 = tf.keras.Input(shape=(1,), dtype=tf.float64, name="x5")
        output = tf.keras.layers.Lambda(select_inputs)(
            [input1, input2, input3, input4, input5])
        output = tf.keras.layers.Dense(units=1)(output)

        model = tf.keras.Model(inputs=[input1, input2, input3, input4, input5],
                               outputs=output)
        loss = tf.keras.losses.MeanSquaredError()

        estimator = TFEstimator(self.statement_set, model, loss, 'adam', 1,
                                ["x1", "x2", "x3", "x4", "x5"],
                                "y", batch_size=1)
        model = estimator.fit(input_table)
        model_path = self._get_model_path()
        model.save(model_path)
        self.statement_set.execute().wait()

        table = model.transform(input_table.drop_columns("y").fetch(10))[0]
        table.execute().print()

    def test_fit_save_load_transform(self):
        self.env.set_parallelism(3)
        schema = Schema.new_builder() \
            .column('x', DataTypes.DOUBLE()) \
            .column_by_expression('y', expr.call_sql("2 * x + 1")) \
            .build()
        input_tb = self.t_env.from_descriptor(
            TableDescriptor.for_connector("datagen")
                .schema(schema)
                .option('number-of-rows', '5120')
                .option('fields.x.min', '0')
                .option('fields.x.max', '1').build())

        input_x = tf.keras.Input(shape=(1,), dtype=tf.float32, name="x")
        output = tf.keras.layers.Dense(units=1)(input_x)
        model = tf.keras.Model(inputs=[input_x], outputs=output)
        loss = tf.keras.losses.MeanSquaredError()

        estimator = TFEstimator(self.statement_set, model, loss, 'adam', 3,
                                ["x"], "y", max_epochs=10)
        model = estimator.fit(input_tb)
        model_path = self._get_model_path()
        model.save(model_path)
        self.statement_set.execute().wait()

        model = TFModel.load(self.env, model_path)
        input_tb = input_tb.drop_columns("y").fetch(10)
        table = model.transform(input_tb)[0]
        table.execute().print()

    def _get_model_path(self):
        return os.path.join(os.path.dirname(__file__), "model",
                            self.id(), f"{time.time()}")
