#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import json
import os
import time

import ai_flow as af
import tensorflow as tf
from flink_ml_tensorflow.tensorflow_context import TFContext

import census_dataset
from wide_deep_run_loop import export_model, ExportCheckpointSaverListener, BatchExportCheckpointSaverListener


class Config(object):
    def __init__(self):
        self.data_dir = 'census_data/'
        self.batch_size = 32
        self.epochs_between_evals = 1
        self.download_if_missing = True
        self.model_dir = "census_model"
        self.model_type = "wide_and_deep"
        self.inter_op_parallelism_threads = 8
        self.intra_op_parallelism_threads = 8
        self.train_epochs = 320000
        self.export_dir = "census_export"
        self.stop_threshold = 0.7
        self.task_type = ''
        self.task_index = None
        self.max_steps = None
        self.run_mode = 'batch'


def build_estimator(model_dir, model_type, model_column_fn, inter_op, intra_op):
    """Build an estimator for given model type."""
    wide_columns, deep_columns = model_column_fn()
    hidden_units = [100, 75, 50, 25]

    # Create a tf.estimator.RunConfig to ensure the model is run on CPU, which
    # trains faster than GPU for this model.
    run_config = tf.estimator.RunConfig().replace(
        keep_checkpoint_max=1,
        save_checkpoints_secs=60,
        session_config=tf.ConfigProto(device_count={'GPU': 0},
                                      inter_op_parallelism_threads=inter_op,
                                      intra_op_parallelism_threads=intra_op))

    if model_type == 'wide':
        return tf.estimator.LinearClassifier(
            model_dir=model_dir,
            feature_columns=wide_columns,
            config=run_config)
    elif model_type == 'deep':
        return tf.estimator.DNNClassifier(
            model_dir=model_dir,
            feature_columns=deep_columns,
            hidden_units=hidden_units,
            config=run_config)
    else:
        return tf.estimator.DNNLinearCombinedClassifier(
            model_dir=model_dir,
            linear_feature_columns=wide_columns,
            dnn_feature_columns=deep_columns,
            dnn_hidden_units=hidden_units,
            config=run_config)


def run_census(flags_obj, input_func):
    """Construct all necessary functions and call run_loop.

    Args:
      flags_obj: Object containing user specified flags.
      input_func: A function that provides input data for training as minibatches.
    """
    if flags_obj.download_if_missing:
        census_dataset.download(flags_obj.data_dir)

    # Create a cluster from the parameter server and worker hosts.
    config = json.loads(os.environ['TF_CONFIG'])
    cluster = tf.train.ClusterSpec(config['cluster'])
    # Create and start a server for the local task.
    server = tf.train.Server(cluster,
                             job_name=flags_obj.task_type,
                             task_index=int(flags_obj.task_index))
    if 'ps' == flags_obj.task_type:
        while True:
            time.sleep(10)

    """Define training loop."""
    # Find project config in the script dir
    af.set_project_config_file(os.path.dirname(__file__) + '/project.yaml')
    model_name = flags_obj.model_type
    print("model_name: "+model_name)
    tf.logging.info("model_name: {}".format(model_name))
    if 'batch' == flags_obj.run_mode:
        version = round(time.time())
        model_path = str(flags_obj.model_dir + '/' + str(version))
    else:
        # get latest deployed base model produced by batch pipeline
        model_path = af.get_latest_validated_model_version('wide_and_deep_base').model_path.split('|')[0]
    print("model_path: " + model_path)

    model = build_estimator(
        model_dir=model_path, model_type=flags_obj.model_type,
        model_column_fn=census_dataset.build_model_columns,
        inter_op=flags_obj.inter_op_parallelism_threads,
        intra_op=flags_obj.intra_op_parallelism_threads)
    ll = []
    if 'stream' == flags_obj.run_mode:
        # The listener will take actions once we finish training
        ll = [ExportCheckpointSaverListener(model, flags_obj.model_type, flags_obj.export_dir,
                                            census_dataset.build_model_columns)]
    train_hooks = []
    # if 'stream' == flags_obj.run_mode:
    #     time.sleep(30)

    if 'batch' == flags_obj.run_mode and flags_obj.task_type != 'chief':
        while True:
            print("sleeping")
            time.sleep(10)

    model.train(input_fn=input_func, hooks=train_hooks, max_steps=flags_obj.max_steps, saving_listeners=ll)
    print("model train finish")
    # Export the model
    if flags_obj.export_dir is not None and 'batch' == flags_obj.run_mode and flags_obj.task_type == 'chief':
        export_path = export_model(model, flags_obj.model_type, flags_obj.export_dir,
                                   census_dataset.build_model_columns)
        print(model_path)
        print(export_path)
        print("##### Generate new model")
        af.register_model_version(model=model_name, model_path=model_path + '|' + export_path)


def batch_map_func(context):
    """Init and run a batch job"""
    tf_context = TFContext(context)
    job_name = tf_context.get_role_name()
    index = tf_context.get_index()
    tf_context.export_estimator_cluster()
    print("job name:" + job_name)
    print("current index:" + str(index))
    tf_config = json.loads(os.environ['TF_CONFIG'])
    config = Config()
    config.max_steps = 500
    # For cluster environment, following configs should be set accordingly.
    config.data_dir = '/tmp/census_data'
    config.model_dir = '/tmp/census_model'
    config.export_dir = '/tmp/census_export'
    config.task_type = tf_config['task']['type']
    config.task_index = tf_config['task']['index']
    config.run_mode = 'batch'
    config.model_type = 'wide_and_deep_base'
    train_file = os.path.join(config.data_dir, census_dataset.TRAINING_FILE)

    def train_input_fn():
        return census_dataset.input_fn(
            train_file, 1, False, config.batch_size)

    run_census(config, train_input_fn)


def stream_map_func(context):
    """Init and run a stream job"""
    tf_context = TFContext(context)

    def flink_input_fn(batch_size):
        """Generate an input dataset function for the Estimator."""

        def parse_csv(value):
            columns = tf.decode_csv(value, record_defaults=census_dataset._CSV_COLUMN_DEFAULTS)
            features = dict(zip(census_dataset.CSV_COLUMNS, columns))
            labels = features.pop('income_bracket')
            classes = tf.equal(labels, '>50K')  # binary classification
            return features, classes

        dataset = tf_context.flink_stream_dataset()
        dataset = dataset.map(parse_csv, num_parallel_calls=5)
        dataset = dataset.repeat(1)
        dataset = dataset.batch(batch_size)
        return dataset

    def flink_train_input_fn():
        return flink_input_fn(config.batch_size)

    job_name = tf_context.get_role_name()
    index = tf_context.get_index()
    tf_context.export_estimator_cluster()
    print("job name:" + job_name)
    print("current index:" + str(index))
    tf_config = json.loads(os.environ['TF_CONFIG'])
    config = Config()
    config.run_mode = 'stream'
    config.max_steps = None
    # For cluster environment, following configs should be set accordingly.
    config.data_dir = '/tmp/census_data'
    config.model_dir = '/tmp/census_model'
    config.export_dir = '/tmp/census_export'
    config.task_type = tf_config['task']['type']
    config.task_index = tf_config['task']['index']
    config.model_type = 'wide_and_deep'
    run_census(config, flink_train_input_fn)
