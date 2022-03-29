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

import json
import logging
import os
import shutil
from datetime import datetime
from sys import argv
from typing import Callable, List

import numpy as np
import tensorflow as tf

logger = logging.getLogger(__file__)

logger.info("TensorFlow version:", tf.__version__)
is_tf2 = int(tf.__version__.split('.')[0]) == 2


class StepLogCallback(tf.keras.callbacks.Callback):
    """
    A Keras call back that log the loss every N steps
    """

    def __init__(self, steps):
        """
        Initialize StepLogCallBack
        :param steps: log every N steps
        """
        super().__init__()
        self.steps = steps
        self._chief_worker_only = True

    def on_train_batch_end(self, batch, logs=None):
        if batch % self.steps == 0:
            loss = logs['loss']
            if abs(loss) > 1e-3:
                logger.info("Step: {} Loss: {:.4f}".format(batch, loss))
            else:
                logger.info("Step: {} Loss: {:.4e}".format(batch, loss))


class ModelSaveCallback(tf.keras.callbacks.Callback):
    """
    A Keras call back that save the model per given number of steps
    """

    def __init__(self, steps, model, model_save_path, is_chief):
        """
        Initialize ModelSaveCallback
        :param steps: save the model every N steps
        """
        super().__init__()
        self.steps = steps
        self.model = model
        if is_chief:
            self.model_save_path = model_save_path
        else:
            # non chief worker save model to a temp path
            self.model_save_path = os.path.join(model_save_path, "non-chief")
        self.is_chief = is_chief
        self._chief_worker_only = True

    def on_train_batch_end(self, batch, logs=None):
        if batch % self.steps == 0:
            logger.info("saving model at step {}".format(batch))
            self._save_model()

    def on_train_end(self, logs=None):
        if not self.is_chief:
            return
        if is_tf2:
            weight = self.model.weights
        else:
            sess = tf.keras.backend.get_session()
            weight = {w.name: sess.run(w) for w in self.model.weights}
        logger.info(weight)

    def _save_model(self):
        self.model.save(self.model_save_path, save_format="tf")
        if not self.is_chief:
            # Removing the temp directory
            shutil.rmtree(self.model_save_path, ignore_errors=True)
            return
        logger.info("model saved at: {}".format(self.model_save_path))


def build_and_compile_model():
    """
    Build linear regression model.
    :return:
    """
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(units=1, input_shape=(1,))
    ])
    loss = tf.keras.losses.MeanSquaredError()
    model.compile(optimizer='adam',
                  loss=loss)
    return model


def train(dataset_provider: Callable[[], tf.data.Dataset],
          model_save_path: str = None):
    """
    Distributed model training on multiple workers.
    """
    if model_save_path is None:
        datetime_str = datetime.now().strftime("%Y%m%d%H%M")
        model_save_path = f"/tmp/linear/{datetime_str}"

    strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
    logger.info('Number of devices: {}'.format(strategy.num_replicas_in_sync))
    with strategy.scope():
        model = build_and_compile_model()

    config = json.loads(os.environ['TF_CONFIG'])
    is_chief = config['task']['type'] == 'worker' and \
        config['task']['index'] == 0
    callbacks: List[tf.keras.callbacks.Callback] = \
        [ModelSaveCallback(1000, model, model_save_path, is_chief)]
    if is_chief:
        callbacks = callbacks + [StepLogCallback(100)]

    model.fit(dataset_provider(), verbose=2, callbacks=callbacks)


def stream_train(context):
    """
    The entry method called by the Deep Learning on Flink framework
    :param context: The context passe by the framework, which could be used to
    construct the TFContext
    """
    from dl_on_flink_tensorflow.tensorflow_context import TFContext

    # Set the TF_CONFIG for distributed training
    tf_context = TFContext(context)
    cluster = tf_context.to_tf_cluster(tf_context.properties["cluster"])
    os.environ['TF_CONFIG'] = json.dumps({
        'cluster': cluster,
        'task': {'type': tf_context.get_node_type(),
                 'index': tf_context.get_index()}
    })
    logger.info(os.environ['TF_CONFIG'])

    model_save_path = tf_context.get_property("model_save_path")

    def stream_dataset() -> tf.data.Dataset:
        """
        Return a DataSet that read from Flink for model training
        """
        def parse_csv(value):
            x, y = tf.io.decode_csv(value, record_defaults=[[0.], [0.]])
            return x, y

        dataset = tf_context.flink_stream_dataset() \
            .map(parse_csv).repeat(1) \
            .batch(32)
        if is_tf2:
            option = tf.data.Options()
            option.experimental_distribute.auto_shard_policy = \
                tf.data.experimental.AutoShardPolicy.OFF
            dataset = dataset.with_options(option)
        return dataset

    train(stream_dataset, model_save_path)


if __name__ == '__main__':
    """
    Distribute train a model with two workers. You should start the two workers
    independently in the same machine with the following two commands:
    ```
    python linear.py 0
    python linear.py 1
    ```
    """

    # Set the TF_CONFIG for distributed training
    tf_config = {
        'cluster': {
            'worker': ['localhost:2000', 'localhost:2001']
        },
        'task': {'type': 'worker', 'index': int(argv[1])}
    }

    os.environ['TF_CONFIG'] = json.dumps(tf_config)


    def get_dataset():
        """
        Generate a DataSet for training
        """
        x_train = np.array([x / 1000. for x in range(1000)]) \
            .reshape((1000, 1))

        y_train = np.array([2.0 * (x / 1000.) + 1.0 for x in range(1000)]) \
            .reshape((1000, 1))

        dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train)).repeat(
            1).batch(32)
        if is_tf2:
            option = tf.data.Options()
            option.experimental_distribute.auto_shard_policy = \
                tf.data.experimental.AutoShardPolicy.OFF
            dataset = dataset.with_options(option)
        return dataset

    train(get_dataset)
