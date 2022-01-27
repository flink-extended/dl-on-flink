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

import os.path

from pyflink.ml.core.api import Estimator, Model
from pyflink.ml.core.param import Param
from pyflink.ml.util import read_write_utils

from flink_ml_tensorflow.tensorflow_TFConfig import TFConfig
from flink_ml_tensorflow.tensorflow_on_flink_table import train
from pyflink.common import Row
from pyflink.datastream.stream_execution_environment import \
    StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, StatementSet, FunctionContext, \
    TableFunction
from pyflink.table.table import Table
from pyflink.table.types import DataType
from pyflink.table.udf import udtf
from typing import List, Dict, Any


class TensorflowEstimator(Estimator):

    def __init__(self,
                 tf_config: TFConfig,
                 predict_col_names: List[str],
                 predict_data_types: List[DataType],
                 table_env: StreamTableEnvironment = None,
                 statement_set: StatementSet = None):
        self.tf_config = tf_config
        self.predict_data_types = predict_data_types
        self.predict_col_names = predict_col_names
        self.table_env = table_env
        self.statement_set = statement_set

    def fit(self, *inputs: Table) -> 'TensorflowModel':
        if len(inputs) == 0:
            if self.table_env is None:
                raise RuntimeError(
                    "table_env should not be None if inputs is not given")
            input_table = None
            t_env = self.table_env
        else:
            input_table = inputs[0]
            t_env = input_table._t_env

        statement_set = self.statement_set if self.statement_set \
            else t_env.create_statement_set()
        env = StreamExecutionEnvironment(t_env._j_tenv.execEnv())
        train(env, t_env, statement_set, input_table, self.tf_config)
        return TensorflowModel(self.tf_config, statement_set,
                               self.predict_col_names, self.predict_data_types)

    def save(self, path: str) -> None:
        read_write_utils.save_metadata(self, path, {
            "tf_config": self.tf_config,
            "predict_data_types": self.predict_data_types,
            "predict_col_names": self.predict_col_names
        })

    @classmethod
    def load(cls, env: StreamExecutionEnvironment, path: str) -> 'TensorflowEstimator':
        meta = read_write_utils.load_metadata(path)
        return TensorflowEstimator(meta["tf_config"], meta["predict_col_names"],
                                   meta["predict_data_types"])

    def get_param_map(self) -> Dict['Param[Any]', Any]:
        return {}

    def __eq__(self, other):
        return type(self) is type(other) \
               and self.__dict__ == other.__dict__


class Predict(TableFunction):

    def __init__(self, model_path, predict_col_names: List[str]):
        super().__init__()
        self._predictor = None
        self._model_path = model_path
        self._predict_col_names = predict_col_names

    def open(self, function_context: FunctionContext):
        import tensorflow as tf
        self._predictor = tf.contrib.predictor.from_saved_model(
            self._model_path)

    def eval(self, row: Row):
        row_dict = row.as_dict()
        feed_dict = {}
        for feed_tensor_key in self._predictor.feed_tensors.keys():
            if feed_tensor_key not in row_dict:
                raise RuntimeError(
                    "input tensor with key {} is not in the row {}".format(
                        feed_tensor_key, row))
            feed_dict[feed_tensor_key] = row_dict[feed_tensor_key]
        predict_dict = self._predictor(feed_dict)
        output_list = []
        for predict_col_name in self._predict_col_names:
            if predict_col_name not in predict_dict:
                raise RuntimeError(
                    "predict column name {} is not in the prediction dict {}"
                        .format(predict_col_name, predict_dict))
            output_list.append(predict_dict[predict_col_name])
        return Row(*row, *output_list)


class TensorflowModel(Model):

    def __init__(self,
                 tf_config: TFConfig = None,
                 statement_set=None,
                 predict_col_names: List[str] = None,
                 predict_data_types: List[DataType] = None) -> None:
        super().__init__()
        self.statement_set: StatementSet = statement_set
        self.tf_config = tf_config
        self.path = None
        self.predict_col_names = predict_col_names if predict_col_names else []
        self.predict_data_types = predict_data_types if predict_data_types else []

    def save(self, path: str) -> None:
        self.path = path
        self.tf_config.java_config().addProperty("model_save_path",
                                                 os.path.join(self.path,
                                                              "model_data"))
        read_write_utils.save_metadata(self, path, {
            "predict_data_types": self.predict_data_types,
            "predict_col_names": self.predict_col_names
        })

    @classmethod
    def load(cls, env: StreamExecutionEnvironment,
             path: str) -> 'TensorflowModel':
        meta = read_write_utils.load_metadata(path)
        model = TensorflowModel()
        model.path = path
        model.predict_data_types = meta["predict_data_types"]
        model.predict_col_names = meta["predict_col_names"]
        return model

    def get_param_map(self) -> Dict['Param[Any]', Any]:
        return {}

    def transform(self, *inputs: Table) -> List[Table]:
        table = inputs[0]
        row_data_type = table.get_schema().to_row_data_type()
        field_types = row_data_type.field_types()
        field_names = row_data_type.field_names()

        table = table.flat_map(
            udtf(f=Predict(os.path.join(self.path, "model_data"),
                           self.predict_col_names),
                 result_types=field_types + self.predict_data_types))
        table = table.alias(*field_names, *self.predict_col_names)
        return [table]
