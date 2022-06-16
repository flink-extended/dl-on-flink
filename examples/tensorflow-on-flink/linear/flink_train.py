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
from datetime import datetime

from dl_on_flink_tensorflow.tf_cluster_config import TFClusterConfig
from dl_on_flink_tensorflow.tf_utils import train
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, TableDescriptor, Schema, \
    DataTypes, expressions as expr

from linear import stream_train

logger = logging.getLogger(__file__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model-path',
        dest='model_path',
        required=False,
        default=f"/tmp/linear/{datetime.now().strftime('%Y%m%d%H%M')}",
        help='Where the trained model should be saved')
    parser.add_argument(
        '--epoch',
        dest='epoch',
        required=False,
        type=int,
        default=1,
        help='The number of epochs to train the model'
    )
    parser.add_argument(
        '--sample-count',
        dest='sample_count',
        required=False,
        type=int,
        default=512000,
        help='The number of samples for training per epoch'
    )
    argv = sys.argv[1:]
    known_args, _ = parser.parse_known_args(argv)
    return known_args


def main():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format="%(message)s")

    known_args = parse_args()
    model_save_path = known_args.model_path
    epoch = known_args.epoch
    sample_count = known_args.sample_count
    logger.info(f"Model will be trained with {sample_count} samples for "
                f"{epoch} epochs and saved at: {model_save_path}")

    # Prepare Flink environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(2)
    t_env = StreamTableEnvironment.create(env)
    statement_set = t_env.create_statement_set()

    # Create the table of samples for model training
    schema = Schema.new_builder() \
        .column('x', DataTypes.DOUBLE()) \
        .column_by_expression('y', expr.call_sql("2 * x + 1")) \
        .build()
    input_tb = t_env.from_descriptor(TableDescriptor.for_connector("datagen")
                                     .schema(schema)
                                     .option('number-of-rows',
                                             str(sample_count))
                                     .option('fields.x.min', '0')
                                     .option('fields.x.max', '1').build())

    tf_cluster_config = TFClusterConfig.new_builder() \
        .set_node_entry(stream_train) \
        .set_worker_count(2) \
        .set_property('input_types', 'FLOAT_64,FLOAT_64') \
        .set_property('model_save_path', model_save_path) \
        .set_property('storage_type', 'local_file') \
        .build()

    train(statement_set, tf_cluster_config, input_tb, epoch)

    # Submit the job. Note that you should call execute method on the
    # statement_set.
    statement_set.execute().wait()


if __name__ == '__main__':
    main()
