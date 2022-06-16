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
import logging
import os
import pickle
from typing import Dict, Any, List, Optional, Type, Mapping, Union

import numpy as np
import tensorflow as tf
from pyflink.common import Row
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.ml.core.api import Estimator, Model, M, T
from pyflink.ml.core.param import Param
from pyflink.ml.util import read_write_utils
from pyflink.table import Table, StatementSet, TableSchema, TableFunction, \
    FunctionContext
from pyflink.table.types import CharType, VarCharType, IntType, \
    BigIntType, FloatType, DoubleType, DataType
from pyflink.table.udf import udtf

from dl_on_flink_tensorflow.tf_cluster_config import TFClusterConfig
from dl_on_flink_tensorflow.flink_ml.tf_estimator_constants import \
    INPUT_TYPES, INPUT_COL_NAMES, FEATURE_COLS, \
    LABEL_COL, MODEL_SAVE_PATH, BATCH_SIZE, MODEL_FACTORY_BASE64, MAX_EPOCHS
from dl_on_flink_tensorflow.flink_ml.tf_model_factory import \
    SimpleTFModelFactory, TFModelFactory
from dl_on_flink_tensorflow.flink_ml.tf_multi_worker_entry import \
    tf_multi_worker_entry
from dl_on_flink_tensorflow.tf_utils import train

logger = logging.getLogger(__file__)

FLINK_TYPE_TO_DL_ON_FLINK_TYPE: Mapping[Type, str] = {
    CharType: "STRING",
    VarCharType: "STRING",
    IntType: "INT_32",
    BigIntType: "INT_64",
    FloatType: "FLOAT_32",
    DoubleType: "FLOAT_64"
}


class TFEstimator(Estimator):

    def __init__(self, statement_set: StatementSet,
                 model: tf.keras.Model,
                 loss: Union[tf.keras.losses.Loss, str],
                 optimizer: Union[tf.keras.optimizers.Optimizer, str],
                 worker_num: int,
                 feature_cols: List[str],
                 label_col: str,
                 max_epochs: int = 1,
                 batch_size: Optional[int] = 32,
                 cluster_config_properties: Optional[Mapping[str, str]] = None):
        """
        A FlinkML Estimator implementation to distributed train a Tensorflow
        Keras Model with MultiWorkerMirroredStrategy.

        :param statement_set: The statement set created by the
        StreamTableEnvironment.
        :param model: The Keras model to train. We only support models with one
        output.
        :param loss: The loss function. It should be keras.losses.Loss instance
        or str.
        :param optimizer: The optimizer. It should be keras.optimizers.Optimizer
        instance or str.
        :param worker_num: The number of workers to run distributed model
        training.
        :param feature_cols: The name of the feature columns.
        :param label_col: The name of the label_col.
        :param max_epochs: Maximum number of epoch to train the model.
        :param batch_size: The batch size default to 32.
        :param cluster_config_properties: Extra cluster config properties.
        """
        self.max_epochs = max_epochs
        self.optimizer = optimizer
        self.loss = loss
        self.model = model
        self.batch_size = batch_size
        self.label_col = label_col
        self.feature_cols = feature_cols
        self.worker_num = worker_num
        self._statement_set = statement_set
        self.cluster_config_properties = \
            cluster_config_properties if cluster_config_properties is not None else {}

    def fit(self, *inputs: Table) -> 'TFModel':
        if len(inputs) != 1:
            raise ValueError("Only one input table is allowed.")

        self._verify_input_table(inputs[0])

        input_table = inputs[0]

        tf_cluster_config_builder = TFClusterConfig.new_builder()

        predict_col_data_type = input_table.get_schema().get_field_data_type(
            self.label_col)
        tf_cluster_config_builder.set_worker_count(self.worker_num) \
            .set_node_entry(tf_multi_worker_entry) \
            .set_property(INPUT_COL_NAMES,
                          self._get_column_names(input_table.get_schema())) \
            .set_property(FEATURE_COLS, ",".join(self.feature_cols)) \
            .set_property(LABEL_COL, self.label_col) \
            .set_property(BATCH_SIZE, str(self.batch_size)) \
            .set_property(INPUT_TYPES,
                          self._get_input_type(input_table.get_schema())) \
            .set_property(MAX_EPOCHS, str(self.max_epochs))

        for k, v in self.cluster_config_properties.items():
            tf_cluster_config_builder.set_property(k, v)

        tf_model_factory = SimpleTFModelFactory(model=self.model,
                                                loss=self.loss,
                                                optimizer=self.optimizer)

        tf_cluster_config_builder.set_property(MODEL_FACTORY_BASE64,
                                               self._pickle_model_factory(
                                                   tf_model_factory))

        return TFModel(tf_cluster_config_builder=tf_cluster_config_builder,
                       predict_col_data_type=predict_col_data_type,
                       statement_set=self._statement_set, input_table=inputs[0])

    def save(self, path: str) -> None:
        raise Exception("TFEstimator does not support save and load")

    @classmethod
    def load(cls, env: StreamExecutionEnvironment, path: str) -> 'TFEstimator':
        raise Exception("TFEstimator does not support save and load")

    def get_param_map(self) -> Dict['Param[Any]', Any]:
        return {}

    @staticmethod
    def _pickle_model_factory(model_factory: TFModelFactory) -> str:
        return base64.encodebytes(pickle.dumps(model_factory)) \
            .decode('utf-8')

    @staticmethod
    def _get_input_type(schema: TableSchema) -> str:
        data_types = schema.get_field_data_types()
        dl_on_flink_types = []
        for data_type in data_types:
            data_type = type(data_type)
            if data_type not in FLINK_TYPE_TO_DL_ON_FLINK_TYPE:
                raise TypeError(f"Unsupported type of column {data_type}")
            dl_on_flink_types.append(
                FLINK_TYPE_TO_DL_ON_FLINK_TYPE[data_type])
        return ",".join(dl_on_flink_types)

    @staticmethod
    def _get_column_names(schema: TableSchema):
        return ",".join(schema.get_field_names())

    def _verify_input_table(self, table: Table):
        for feature_col in self.feature_cols:
            assert feature_col in table.get_schema().get_field_names()

        assert self.label_col in table.get_schema().get_field_names()


class Predict(TableFunction):

    def __init__(self, tf_cluster_config: TFClusterConfig):
        super().__init__()
        self._model: Optional[tf.keras.Model] = None
        self._tf_cluster_config = tf_cluster_config
        self._model_path = tf_cluster_config.get_property(MODEL_SAVE_PATH)
        self._feature_cols = tf_cluster_config.get_property(FEATURE_COLS) \
            .split(",")
        self._label_col = tf_cluster_config.get_property(LABEL_COL)

    def open(self, function_context: FunctionContext):
        import tensorflow as tf
        if not tf.io.gfile.exists(self._model_path):
            raise FileNotFoundError(
                f"Model is not found at {self._model_path}.")
        self._model = tf.keras.models.load_model(self._model_path)

    def eval(self, row: Row):
        row_dict = row.as_dict()
        features = {}
        for feature_col in self._feature_cols:
            if feature_col not in row_dict:
                raise KeyError(f"{feature_col} not in the given row")
            features[feature_col] = np.array([row_dict[feature_col]])
        res = self._model.predict(features)[0]
        return Row(*row, res)


class TFModel(Model):

    def __init__(self,
                 predict_col_data_type: DataType,
                 tf_cluster_config_builder: TFClusterConfig.Builder = None,
                 tf_cluster_config: TFClusterConfig = None,
                 statement_set: StatementSet = None,
                 input_table=None):
        self.predict_col_data_type = predict_col_data_type
        self.input_table = input_table
        self.statement_set = statement_set
        self.tf_cluster_config_builder = tf_cluster_config_builder
        self.tf_cluster_config = tf_cluster_config

    def transform(self, *inputs: Table) -> List[Table]:
        if self.tf_cluster_config is None \
                or self.tf_cluster_config.get_property(MODEL_SAVE_PATH) is None:
            raise Exception("TFClusterConfig is missing or model path does "
                            "not exist. Please invoke save and "
                            "StatementSet#exeucte before transform.")
        table = inputs[0]
        row_data_type = table.get_schema().to_row_data_type()
        field_types = row_data_type.field_types()
        field_names = row_data_type.field_names()

        label_col = self.tf_cluster_config.get_property(LABEL_COL)
        table = table.flat_map(
            udtf(f=Predict(self.tf_cluster_config),
                 result_types=field_types + [self.predict_col_data_type]))
        table = table.alias(*field_names, label_col)
        return [table]

    def save(self, path: str) -> None:
        self.tf_cluster_config_builder \
            .set_property(MODEL_SAVE_PATH, os.path.join(path, "model.h5"))
        self.tf_cluster_config = self.tf_cluster_config_builder.build()
        max_epoch = int(self.tf_cluster_config.get_property(MAX_EPOCHS))

        read_write_utils.save_metadata(self, path, {
            "tf_cluster_config": self.tf_cluster_config,
            "predict_col_data_type": self.predict_col_data_type
        })
        train(self.statement_set, self.tf_cluster_config, self.input_table,
              max_epoch=max_epoch)

    @classmethod
    def load(cls, env: StreamExecutionEnvironment, path: str) -> 'TFModel':
        meta = read_write_utils.load_metadata(path)
        model = TFModel(tf_cluster_config=meta["tf_cluster_config"],
                        predict_col_data_type=meta["predict_col_data_type"])
        return model

    def get_param_map(self) -> Dict['Param[Any]', Any]:
        return {}
