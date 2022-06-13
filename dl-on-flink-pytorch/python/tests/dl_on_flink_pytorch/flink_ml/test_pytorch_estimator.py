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
import os
import time
import unittest

import torch
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, Schema, DataTypes, \
    expressions as expr, TableDescriptor
from torch import nn
from torch.optim import SGD
from torch.optim.lr_scheduler import ExponentialLR

from dl_on_flink_pytorch.flink_ml.pytorch_estimator import PyTorchEstimator, \
    PyTorchModel
from tests.dl_on_flink_pytorch.utils import add_dl_on_flink_jar, find_jar_path


class Linear(nn.Module):

    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1, 1, dtype=torch.float64)

    def forward(self, x):
        return self.linear(x)


class PrintModel(nn.Module):

    def __init__(self):
        super(PrintModel, self).__init__()
        self.linear = nn.Linear(1, 1, dtype=torch.float64)

    def forward(self, x1, x2, x3, x4):
        print(x1, x2, x3, x4)
        return self.linear(x4)


def sgd_optimizer_creator(_model: torch.nn.Module):
    return SGD(_model.parameters(), lr=0.1)


class TestPyTorchEstimator(unittest.TestCase):

    def setUp(self) -> None:
        add_dl_on_flink_jar()
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.env.add_jars("file://{}".format(find_jar_path()))
        self.t_env = StreamTableEnvironment.create(self.env)
        self.statement_set = self.t_env.create_statement_set()

    def test_fit_with_all_types(self):
        schema = Schema.new_builder() \
            .column("x1", DataTypes.INT()) \
            .column("x2", DataTypes.BIGINT()) \
            .column("x3", DataTypes.FLOAT()) \
            .column("x4", DataTypes.DOUBLE()) \
            .column_by_expression("y", expr.call_sql("x4")) \
            .build()
        input_table = self.t_env.from_descriptor(TableDescriptor
                                                 .for_connector("datagen")
                                                 .schema(schema)
                                                 .option('number-of-rows',
                                                         '100')
                                                 .option('fields.x4.min', '0')
                                                 .option('fields.x4.max', '100')
                                                 .build())

        model = PrintModel()
        loss_fn = nn.MSELoss()
        estimator = PyTorchEstimator(self.statement_set, model, loss_fn,
                                     sgd_optimizer_creator, 1,
                                     ["x1", "x2", "x3", "x4"],
                                     "y", batch_size=1)

        model = estimator.fit(input_table)
        model_path = self._get_model_path()
        model.save(model_path)
        self.statement_set.execute().wait()

        table = model.transform(input_table.drop_columns("y").fetch(10))[0]
        table.execute().print()

    def test_fit_save_load_transform(self):
        self.env.set_parallelism(3)
        schema = Schema.new_builder() \
            .column('x', DataTypes.DOUBLE()) \
            .column_by_expression('y', expr.call_sql("2 * x + 1")) \
            .build()
        input_tb = self.t_env.from_descriptor(
            TableDescriptor.for_connector("datagen")
                .schema(schema)
                .option('number-of-rows', '1280')
                .option('fields.x.min', '0')
                .option('fields.x.max', '1').build())

        model = Linear()
        loss_fn = nn.MSELoss()

        def lr_scheduler_creator(_optimizer):
            return ExponentialLR(_optimizer, 0.9)

        estimator = PyTorchEstimator(self.statement_set, model, loss_fn,
                                     sgd_optimizer_creator, 3,
                                     ["x"], "y", max_epochs=10,
                                     lr_scheduler_creator=lr_scheduler_creator,
                                     batch_size=32)
        model = estimator.fit(input_tb)
        model_path = self._get_model_path()
        model.save(model_path)
        self.statement_set.execute().wait()

        model = PyTorchModel.load(self.env, model_path)
        input_tb = input_tb.drop_columns("y").fetch(10)
        table = model.transform(input_tb)[0]
        table.execute().print()

    def _get_model_path(self):
        return os.path.join(os.path.dirname(__file__), "model",
                            self.id(), f"{time.time()}")
