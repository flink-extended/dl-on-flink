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

from dl_on_flink_pytorch.flink_ml.pytorch_estimator import PyTorchModel
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, Schema, DataTypes, \
    expressions as expr, TableDescriptor

logger = logging.getLogger(__file__)


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

    # Create the table of samples for model training
    schema = Schema.new_builder() \
        .column('x1', DataTypes.FLOAT()) \
        .column('x2', DataTypes.FLOAT()) \
        .column_by_expression('expected_y',
                              expr.call_sql("2 * x1 + 3 * x2 + 1")) \
        .build()
    table = t_env.from_descriptor(TableDescriptor.for_connector("datagen")
                                  .schema(schema)
                                  .option('number-of-rows',
                                          str(sample_count))
                                  .option('fields.x1.min', '0')
                                  .option('fields.x1.max', '1')
                                  .option('fields.x2.min', '0')
                                  .option('fields.x2.max', '1')
                                  .build())

    model = PyTorchModel.load(env, model_path)
    res_table = model.transform(table)[0]
    res_table.execute().print()


if __name__ == '__main__':
    main()
