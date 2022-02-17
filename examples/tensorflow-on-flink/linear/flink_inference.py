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
import argparse
import logging
import os
import sys

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, \
    FunctionContext, DataTypes
from pyflink.table.udf import udf, ScalarFunction

logger = logging.getLogger(__file__)


class Predict(ScalarFunction):
    """
    The scalar function that do prediction with the given model.
    """

    def __init__(self, _model_path):
        super().__init__()
        self._model = None
        self._model_path = _model_path

    def open(self, function_context: FunctionContext):
        import tensorflow as tf
        self._model = tf.keras.models.load_model(self._model_path)

    def eval(self, x):
        result = self._model.predict([x])
        return result.flatten()[0]


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format="%(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model-path',
        dest='model_path',
        required=True,
        help='Where the trained model should be saved')
    parser.add_argument(
        '--sample-count',
        dest='sample_count',
        required=False,
        default=10,
        help='Number of sample to inference. Default to 10'
    )
    argv = sys.argv[1:]
    known_args, _ = parser.parse_known_args(argv)

    model_path = known_args.model_path
    sample_count = known_args.sample_count
    logger.info("Inference with model at: {}".format(model_path))

    # Prepare Flink environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    t_env = StreamTableEnvironment.create(env)
    statement_set = t_env.create_statement_set()

    python_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               'linear.py')

    # Register the udf for prediction
    t_env.create_temporary_function("predict",
                                    udf(f=Predict(model_path),
                                        result_type=DataTypes.DOUBLE()))

    # Create the table of input for prediction
    ddl = f"""
            CREATE TABLE src (
                x FLOAT
            ) WITH (
                'connector' = 'datagen',
                'fields.x.min' = '0',
                'fields.x.max' = '1',
                'number-of-rows' = '{sample_count}',
                'rows-per-second' = '1'
            )
        """
    t_env.execute_sql(ddl)

    table = t_env.sql_query("SELECT x, 2 * x + 1, predict(x) FROM src") \
        .alias("x", "y", "predict")
    table.execute().print()
