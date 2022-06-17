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
from typing import Dict, Any, List, Optional, Mapping, Type

import torch
from pyflink.common import Row
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.ml.core.api import Estimator, Model
from pyflink.ml.core.param import Param
from pyflink.ml.util import read_write_utils
from pyflink.table import Table, StatementSet, TableSchema, TableFunction, \
    FunctionContext
from pyflink.table.types import IntType, \
    BigIntType, FloatType, DoubleType, DataType
from pyflink.table.udf import udtf
from torch.nn.modules.loss import _Loss as Loss

from dl_on_flink_pytorch.flink_ml.pytorch_estimator_constants import \
    INPUT_COL_NAMES, FEATURE_COLS, LABEL_COL, BATCH_SIZE, INPUT_TYPES, \
    MAX_EPOCHS, MODEL_FACTORY_BASE64, MODEL_SAVE_PATH
from dl_on_flink_pytorch.flink_ml.pytorch_model_factory import \
    LR_SCHEDULER_CREATOR_T, SimplePyTorchModelFactory, PyTorchModelFactory, \
    OPTIMIZER_CREATOR_T
from dl_on_flink_pytorch.flink_ml.pytorch_train_entry import pytorch_train_entry
from dl_on_flink_pytorch.flink_stream_dataset import \
    DL_ON_FLINK_TYPE_TO_PYTORCH_TYPE
from dl_on_flink_pytorch.pytorch_cluster_config import PyTorchClusterConfig
from dl_on_flink_pytorch.pytorch_utils import train

logger = logging.getLogger(__file__)

FLINK_TYPE_TO_DL_ON_FLINK_TYPE: Mapping[Type, str] = {
    IntType: "INT_32",
    BigIntType: "INT_64",
    FloatType: "FLOAT_32",
    DoubleType: "FLOAT_64"
}


class PyTorchEstimator(Estimator):

    def __init__(self, statement_set: StatementSet,
                 model: torch.nn.Module,
                 loss: Loss,
                 optimizer: OPTIMIZER_CREATOR_T,
                 worker_num: int,
                 feature_cols: List[str],
                 label_col: str,
                 max_epochs: int = 1,
                 lr_scheduler_creator: Optional[LR_SCHEDULER_CREATOR_T] = None,
                 batch_size: Optional[int] = 32,
                 cluster_config_properties: Optional[Mapping[str, str]] = None
                 ):
        """
        A FlinkML Estimator implementation to distributed train a PyTorch model.

        :param statement_set: The statement set created by the
        StreamTableEnvironment.
        :param model: The PyTorch model instance.
        :param loss: The Loss instance
        :param optimizer: A function to create a PyTorch optimizer.
        :param worker_num: The number of workers to do the distributed training.
        :param feature_cols: The name of the feature columns.
        :param label_col: The name of the label_col.
        :param max_epochs: Maximum number of epoch to train the model.
        :param lr_scheduler_creator: A function to create the PyTorch LRScheduler
        :param batch_size: The batch size default to 32.
        :param cluster_config_properties: Extra cluster config properties.
        """
        self.batch_size = batch_size
        self.lr_scheduler_creator = lr_scheduler_creator
        self.max_epochs = max_epochs
        self.label_col = label_col
        self.feature_cols = feature_cols
        self.worker_num = worker_num
        self.optimizer_creator = optimizer
        self.loss = loss
        self.model = model
        self.statement_set = statement_set
        self.cluster_config_properties = \
            cluster_config_properties if cluster_config_properties is not None else {}

    def fit(self, *inputs: Table) -> 'PyTorchModel':
        if len(inputs) != 1:
            raise ValueError("Only one input table is allowed.")
        self._verify_input_table(inputs[0])

        input_table = inputs[0]
        pytorch_cluster_config_builder = PyTorchClusterConfig.new_builder()
        predict_col_data_type = input_table.get_schema().get_field_data_type(
            self.label_col)
        pytorch_cluster_config_builder.set_world_size(self.worker_num) \
            .set_node_entry(pytorch_train_entry) \
            .set_property(INPUT_COL_NAMES,
                          self._get_column_names(input_table.get_schema())) \
            .set_property(FEATURE_COLS, ",".join(self.feature_cols)) \
            .set_property(LABEL_COL, self.label_col) \
            .set_property(BATCH_SIZE, str(self.batch_size)) \
            .set_property(INPUT_TYPES,
                          self._get_input_type(input_table.get_schema())) \
            .set_property(MAX_EPOCHS, str(self.max_epochs))

        for k, v in self.cluster_config_properties.items():
            pytorch_cluster_config_builder.set_property(k, v)

        tf_model_factory = SimplePyTorchModelFactory(model=self.model,
                                                     loss=self.loss,
                                                     optimizer_creator=self.optimizer_creator,
                                                     lr_scheduler_creator=self.lr_scheduler_creator)

        pytorch_cluster_config_builder.set_property(MODEL_FACTORY_BASE64,
                                                    self._pickle_model_factory(
                                                        tf_model_factory))

        return PyTorchModel(
            pytorch_cluster_config_builder=pytorch_cluster_config_builder,
            predict_col_data_type=predict_col_data_type,
            statement_set=self.statement_set, input_table=inputs[0])

    def save(self, path: str) -> None:
        raise Exception("PyTorch does not support save and load")

    @classmethod
    def load(cls, env: StreamExecutionEnvironment, path: str) \
            -> 'PyTorchEstimator':
        raise Exception("PyTorch does not support save and load")

    def get_param_map(self) -> Dict['Param[Any]', Any]:
        return {}

    def _verify_input_table(self, table: Table):
        for feature_col in self.feature_cols:
            assert feature_col in table.get_schema().get_field_names(), \
                f"{feature_col} not in the given input table: \n " \
                f"{table.get_schema()}"

        assert self.label_col in table.get_schema().get_field_names(), \
            f"{self.label_col} not in the given input table: \n " \
            f"{table.get_schema()}"

    @staticmethod
    def _pickle_model_factory(model_factory: PyTorchModelFactory) -> str:
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


class Predict(TableFunction):

    def __init__(self, pytorch_cluster_config: PyTorchClusterConfig):
        super().__init__()
        self._model: Optional[torch.nn.Module] = None
        self._tf_cluster_config = pytorch_cluster_config
        self._model_path = pytorch_cluster_config.get_property(MODEL_SAVE_PATH)
        self._feature_cols = pytorch_cluster_config.get_property(FEATURE_COLS) \
            .split(",")
        self._label_col = pytorch_cluster_config.get_property(LABEL_COL)
        self._input_types: List[str] = pytorch_cluster_config.get_property(
            INPUT_TYPES).split(",")
        self._input_cols: List[str] = pytorch_cluster_config.get_property(
            INPUT_COL_NAMES).split(",")

    def open(self, function_context: FunctionContext):
        import torch
        self._model = torch.load(self._model_path)
        self._model.eval()

    def eval(self, row: Row):
        import torch
        row_dict = row.as_dict()
        features = []
        for feature_col in self._feature_cols:
            if feature_col not in row_dict:
                raise KeyError(f"{feature_col} not in the given row")
            col_idx = self._input_cols.index(feature_col)
            col_type = self._input_types[col_idx]
            features.append(
                torch.tensor([[row_dict[feature_col]]],
                             dtype=DL_ON_FLINK_TYPE_TO_PYTORCH_TYPE[col_type]))
        res = self._model(*features)
        return Row(*row, res)


class PyTorchModel(Model):

    def __init__(self,
                 predict_col_data_type: DataType,
                 pytorch_cluster_config_builder: PyTorchClusterConfig.Builder = None,
                 pytorch_cluster_config: PyTorchClusterConfig = None,
                 statement_set: StatementSet = None,
                 input_table=None):
        self.input_table = input_table
        self.statement_set = statement_set
        self.pytorch_cluster_config = pytorch_cluster_config
        self.pytorch_cluster_config_builder = pytorch_cluster_config_builder
        self.predict_col_data_type = predict_col_data_type

    def transform(self, *inputs: Table) -> List[Table]:
        if self.pytorch_cluster_config is None \
                or self.pytorch_cluster_config.get_property(MODEL_SAVE_PATH) \
                is None:
            raise Exception("TFClusterConfig is missing or model path does "
                            "not exist. Please invoke save and "
                            "StatementSet#exeucte before transform.")
        table = inputs[0]
        row_data_type = table.get_schema().to_row_data_type()
        field_types = row_data_type.field_types()
        field_names = row_data_type.field_names()

        label_col = self.pytorch_cluster_config.get_property(LABEL_COL)
        table = table.flat_map(
            udtf(f=Predict(self.pytorch_cluster_config),
                 result_types=field_types + [self.predict_col_data_type]))
        table = table.alias(*field_names, label_col)
        return [table]

    def save(self, path: str) -> None:
        self.pytorch_cluster_config_builder \
            .set_property(MODEL_SAVE_PATH, os.path.join(path, "model.pt"))
        self.pytorch_cluster_config = \
            self.pytorch_cluster_config_builder.build()
        max_epoch = int(self.pytorch_cluster_config.get_property(MAX_EPOCHS))

        read_write_utils.save_metadata(self, path, {
            "pytorch_cluster_config": self.pytorch_cluster_config,
            "predict_col_data_type": self.predict_col_data_type
        })
        train(self.statement_set, self.pytorch_cluster_config, self.input_table,
              max_epoch=max_epoch)

    @classmethod
    def load(cls, env: StreamExecutionEnvironment, path: str) -> 'PyTorchModel':
        meta = read_write_utils.load_metadata(path)
        model = PyTorchModel(
            pytorch_cluster_config=meta["pytorch_cluster_config"],
            predict_col_data_type=meta["predict_col_data_type"])
        return model

    def get_param_map(self) -> Dict['Param[Any]', Any]:
        return {}
