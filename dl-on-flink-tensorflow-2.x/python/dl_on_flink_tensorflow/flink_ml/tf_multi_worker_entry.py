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
import base64
import json
import logging
import os
import pickle
from typing import List

import tensorflow as tf
from dl_on_flink_framework.context import Context

from dl_on_flink_tensorflow.tensorflow_context import TFContext
from dl_on_flink_tensorflow.flink_ml.tf_estimator_constants import \
    MODEL_SAVE_PATH, INPUT_TYPES, INPUT_COL_NAMES, \
    FEATURE_COLS, LABEL_COL, BATCH_SIZE, MODEL_FACTORY_BASE64, MAX_EPOCHS
from dl_on_flink_tensorflow.flink_ml.tf_model_factory import TFModelFactory

logger = logging.getLogger(__file__)


def convert_dataset(dataset_from_flink: tf.data.TFRecordDataset,
                    input_col_names: List[str],
                    input_types: List[str],
                    feature_cols: List[str],
                    label_col: str,
                    batch_size: int) -> tf.data.Dataset:
    """
    Return a DataSet that read from Flink for model training
    """
    default_tensor_map = {
        "STRING": tf.constant([""], dtype=tf.string),
        "INT_32": tf.constant([0], dtype=tf.int32),
        "INT_64": tf.constant([0], dtype=tf.int64),
        "FLOAT_32": tf.constant([0.0], dtype=tf.float32),
        "FLOAT_64": tf.constant([0.0], dtype=tf.float64)
    }
    default_tensors = [default_tensor_map[data_type] for data_type in
                       input_types]

    def parse_csv(value):
        tensors = tf.io.decode_csv(value, record_defaults=default_tensors)
        features = {}
        for feature_col in feature_cols:
            idx = input_col_names.index(feature_col)
            features[feature_col] = tensors[idx]
        label_idx = input_col_names.index(label_col)
        return features, tensors[label_idx]

    dataset = dataset_from_flink \
        .batch(batch_size) \
        .map(parse_csv)

    option = tf.data.Options()
    option.experimental_distribute.auto_shard_policy = \
        tf.data.experimental.AutoShardPolicy.OFF
    dataset = dataset.with_options(option)

    return dataset


def tf_multi_worker_entry(context: Context):
    tf_context = TFContext(context)
    cluster = tf_context.get_tf_cluster_config()
    config = {
        'cluster': cluster,
        'task': {'type': tf_context.get_node_type(),
                 'index': tf_context.get_index()}
    }
    os.environ['TF_CONFIG'] = json.dumps(config)
    logger.info(os.environ['TF_CONFIG'])

    model_save_path = tf_context.get_property(MODEL_SAVE_PATH)

    input_col_names: List[str] = context.get_property(INPUT_COL_NAMES) \
        .split(",")
    input_types: List[str] = context.get_property(INPUT_TYPES).split(",")
    feature_cols: List[str] = context.get_property(FEATURE_COLS).split(",")
    predict_col: str = context.get_property(LABEL_COL)
    batch_size: int = int(context.get_property(BATCH_SIZE))
    max_epochs: int = int(context.get_property(MAX_EPOCHS))

    strategy = tf.distribute.MultiWorkerMirroredStrategy()
    logger.info('Number of devices: {}'.format(strategy.num_replicas_in_sync))

    with strategy.scope():
        model_factory: TFModelFactory = pickle.loads(
            base64.decodebytes(context.get_property(MODEL_FACTORY_BASE64)
                               .encode('utf-8')))
        model = model_factory.create_model(tf_context)
        loss = model_factory.create_loss(tf_context)
        optimizer = model_factory.create_optimizer(tf_context)
        metrics = model_factory.create_metrics(tf_context)
        model.compile(loss=loss, optimizer=optimizer, metrics=metrics)

    task_type = config['task']['type']
    task_index = config['task']['index']
    is_chief = task_type == 'worker' and task_index == 0

    dataset = convert_dataset(tf_context.get_tfdataset_from_flink(),
                              input_col_names, input_types, feature_cols,
                              predict_col, batch_size)

    model.fit(dataset, verbose=2, epochs=max_epochs)

    if is_chief:
        model_dir = os.path.dirname(model_save_path)
        if not tf.io.gfile.exists(model_dir):
            tf.io.gfile.makedirs(model_dir)
        model.save(model_save_path, save_format='h5')
    else:
        model_dir = os.path.dirname(model_save_path)
        tmp_model_dir = os.path.join(model_dir, f"task_{task_index}")
        tmp_model_path = os.path.join(tmp_model_dir, "tmp_model")
        if not tf.io.gfile.exists(tmp_model_dir):
            tf.io.gfile.makedirs(tmp_model_dir)
        model.save(tmp_model_path, save_format='h5')
        tf.io.gfile.rmtree(tmp_model_dir)
