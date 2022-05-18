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
import logging
import sys
from typing import Callable

import tensorflow as tf

from dl_on_flink_tensorflow.tensorflow_context import TFContext
from dl_on_flink_tensorflow.tensorflow_on_flink_ops import FlinkStreamDataSet

logger = logging.getLogger(__file__)


class PrintLayer(tf.keras.layers.Layer):

    def __init__(self, log_id, *xargs, **kwargs):
        super().__init__(*xargs, **kwargs)
        self.log_id = log_id

    def call(self, inputs, **kwargs):
        tf.keras.backend.print_tensor(inputs, message=f'{self.log_id}: ')
        return inputs


def train(node_id, dataset_provider: Callable[[], tf.data.Dataset],
          epochs=sys.maxsize):
    model = tf.keras.Sequential([PrintLayer(node_id)])
    loss = tf.keras.losses.MeanSquaredError()
    model.compile(loss=loss)
    try:
        model.fit(dataset_provider(), epochs=epochs, verbose=2)
    except Exception as e:
        # ignore
        pass


def map_func(context):
    tf.compat.v1.enable_eager_execution()
    context: TFContext = TFContext(context)
    dataset: FlinkStreamDataSet = context.get_tfdataset_from_flink() \
        .map(
        lambda t: [tf.io.decode_csv(t, [[.0]]),
                   tf.io.decode_csv(t, [[.0]])])
    train(f"{context.get_node_type()}:{context.get_index()}", lambda: dataset,
          epochs=20)
