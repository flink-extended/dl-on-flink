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

import tensorflow as tf
from dl_on_flink_tensorflow.flink_ml.tf_estimator import TFEstimator
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, TableDescriptor, Schema, \
    DataTypes, expressions as expr

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
        default=100,
        help='The number of epochs to train the model'
    )
    parser.add_argument(
        '--sample-count',
        dest='sample_count',
        required=False,
        type=int,
        default=5120,
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
        .column('x1', DataTypes.FLOAT()) \
        .column('x2', DataTypes.FLOAT()) \
        .column_by_expression('y', expr.call_sql("2 * x1 + 3 * x2 + 1")) \
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

    label_col = "y"
    feature_cols = [col for col in table.get_schema().get_field_names() if
                    col != label_col]

    x1 = tf.keras.Input(shape=(1,), dtype=tf.float32, name="x1")
    x2 = tf.keras.Input(shape=(1,), dtype=tf.float32, name="x2")

    x = tf.keras.layers.concatenate([x1, x2])
    output = tf.keras.layers.Dense(units=1)(x)
    model = tf.keras.Model(inputs=[x1, x2], outputs=output)
    loss = tf.keras.losses.MeanSquaredError()
    adam = tf.keras.optimizers.Adam()

    config_properties = {'storage_type': 'local_file'}
    estimator = TFEstimator(statement_set, model, loss, adam, worker_num=2,
                            feature_cols=feature_cols,
                            label_col=label_col, max_epochs=epoch,
                            batch_size=128,
                            cluster_config_properties=config_properties)

    model = estimator.fit(table)
    model.save(model_save_path)

    # Submit the job. Note that you should call execute method on the
    # statement_set.
    statement_set.execute().wait()


if __name__ == '__main__':
    main()
