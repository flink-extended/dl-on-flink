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
import argparse
import logging
import sys

import torch
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, \
    FunctionContext, DataTypes, TableDescriptor, Schema
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
        self._model = torch.load(self._model_path)

    def eval(self, x):
        result = self._model(torch.tensor([x], dtype=torch.float64))
        return result.item()


def main():
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

    # Register the udf for prediction
    predict = udf(f=Predict(model_path), result_type=DataTypes.DOUBLE())

    # Create the table of input for prediction
    schema = Schema.new_builder().column("x", DataTypes.FLOAT()).build()
    table = t_env.from_descriptor(TableDescriptor.for_connector("datagen")
                                  .schema(schema)
                                  .option("fields.x.min", "0")
                                  .option("fields.x.max", "1")
                                  .option("number-of-rows", str(sample_count))
                                  .build())

    table = table.add_columns(predict(table.x).alias("predict"))
    table.execute().print()


if __name__ == '__main__':
    main()
