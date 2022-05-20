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
from typing import Optional

from pyflink.java_gateway import get_gateway
from pyflink.table import StatementSet, Table, Schema

from dl_on_flink_pytorch.pytorch_cluster_config import PyTorchClusterConfig


def train(statement_set: StatementSet, pytorch_config: PyTorchClusterConfig,
          input_table: Optional[Table] = None, max_epoch: int = 1):
    """
    Train a PyTorch deep learning model. If the input_table is None, the
    max_epoch is ignored. Users should read the input data in their entry
    function written with PyTorch.

    If input_table is provided, the deep learning model is trained iteratively
    with the input data from Flink up to the given maximum number epoch. User
    can terminate the training earlier by exiting the entry. The input_table
    should be bounded, if the max_epoch is greater than 1. Otherwise, the model
    is trained indefinitely with the unbounded data at the first epoch. User can
    use the FlinkStreamDataset to read data from Flink. The pytorch_config includes
    all the information to run the training cluster.

    This method adds a number of nodes with different node types
    in the deep learning cluster to the given statement_set. Therefore, user
    should invoke execute on statement_set to run the deep learning cluster
    at the end.

    :param statement_set: The statement set to add the deep learning tables.
    :param pytorch_config: The configuration of the PyTorch cluster.
    :param input_table: The input data to the training process.
    :param max_epoch: Maximum number of epoch to train the model.
    """
    if statement_set is None:
        raise ValueError("statement_set cannot be None.")

    if pytorch_config is None:
        raise ValueError("pytorch_config cannot be None.")

    if input_table is None:
        # noinspection PyProtectedMember
        get_gateway().jvm.org.flinkextended \
            .flink.ml.pytorch.PyTorchUtils.train(
            statement_set._j_statement_set,
            pytorch_config._to_j_pytorch_cluster_config())
    else:
        if max_epoch == 1:
            # noinspection PyProtectedMember
            get_gateway().jvm.org.flinkextended \
                .flink.ml.pytorch.PyTorchUtils.train(
                statement_set._j_statement_set,
                input_table._j_table,
                pytorch_config._to_j_pytorch_cluster_config())
        elif max_epoch > 1:
            # noinspection PyProtectedMember
            get_gateway().jvm.org.flinkextended \
                .flink.ml.pytorch.PyTorchUtils.train(
                statement_set._j_statement_set,
                input_table._j_table,
                pytorch_config._to_j_pytorch_cluster_config(),
                max_epoch)
        else:
            raise ValueError(f"Invalid max_epoch {max_epoch}.")


def inference(statement_set: StatementSet, input_table: Table,
              pytorch_cluster_config: PyTorchClusterConfig,
              schema: Schema) -> Table:
    """
    Stream inference with PyTorch model for the input table.
    pytorch_cluster_config includes all the information to run the training
    cluster.

    This method add a number of nodes with different node types
    in the deep learning cluster to the given statement_set. Therefore, user
    should invoke execute on statement_set to run the deep learning cluster
    at the end.

    User is responsible to insert the returned table into the statement_set so
    that the PyTorch cluster runs in the same Flink job.

    :param statement_set: The statement set to add the deep learning tables.
    :param input_table: The input data to inference.
    :param pytorch_cluster_config: The configuration of the PyTorch cluster.
    :param schema: The schema of the output Table.
    :return: The output Table produced by PyTorch model inference process.
    """
    if statement_set is None:
        raise ValueError("statement_set cannot be None.")

    if input_table is None:
        raise ValueError("input_table cannot be None.")

    if pytorch_cluster_config is None:
        raise ValueError("pytorch_cluster_config cannot be None.")

    if schema is None:
        raise ValueError("schema cannot be None")

    # noinspection PyProtectedMember
    j_table = get_gateway().jvm.org.flinkextended \
        .flink.ml.pytorch.PyTorchUtils.inference(
        statement_set._j_statement_set,
        input_table._j_table,
        pytorch_cluster_config._to_j_pytorch_cluster_config(),
        schema._j_schema)

    # noinspection PyProtectedMember
    return Table(j_table, statement_set._t_env)
