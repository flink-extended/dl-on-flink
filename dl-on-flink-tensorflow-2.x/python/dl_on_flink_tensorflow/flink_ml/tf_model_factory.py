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
import abc
import cloudpickle as pickle
from typing import List, Optional, Union

import tensorflow as tf

from dl_on_flink_tensorflow.tensorflow_context import TFContext


class TFModelFactory(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def create_model(self, tf_context: TFContext) -> tf.keras.Model:
        pass

    @abc.abstractmethod
    def create_loss(self, tf_context: TFContext) -> tf.keras.losses.Loss:
        pass

    @abc.abstractmethod
    def create_optimizer(self,
                         tf_context: TFContext) -> tf.keras.optimizers.Optimizer:
        pass

    @abc.abstractmethod
    def create_metrics(self, tf_context: TFContext) \
            -> List[tf.keras.metrics.Metric]:
        pass


class SimpleTFModelFactory(TFModelFactory):

    def __init__(self, model: tf.keras.Model,
                 loss: Union[tf.keras.losses.Loss, str],
                 optimizer: Union[tf.keras.optimizers.Optimizer, str],
                 metrics: Optional[List[tf.keras.metrics.Metric]] = None):
        super().__init__()
        self.model_json = model.to_json()
        self.pickled_loss = pickle.dumps(loss)
        self.pickled_optimizer = pickle.dumps(optimizer)
        self.pickled_metrics = pickle.dumps(metrics)

    def create_model(self, tf_context: TFContext) -> tf.keras.Model:
        return tf.keras.models.model_from_json(self.model_json)

    def create_loss(self, tf_context: TFContext) -> tf.keras.losses.Loss:
        return pickle.loads(self.pickled_loss)

    def create_optimizer(self,
                         tf_context: TFContext) -> tf.keras.optimizers.Optimizer:
        return pickle.loads(self.pickled_optimizer)

    def create_metrics(self, tf_context: TFContext) -> List[
        tf.keras.metrics.Metric]:
        return pickle.loads(self.pickled_metrics)
