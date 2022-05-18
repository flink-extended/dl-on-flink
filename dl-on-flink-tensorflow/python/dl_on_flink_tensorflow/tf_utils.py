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
from pyflink.table import StatementSet, Schema
from pyflink.table.table import Table

from dl_on_flink_tensorflow.tf_cluster_config import TFClusterConfig


def inference(statement_set: StatementSet, input_table: Table,
              tf_cluster_config: TFClusterConfig, schema: Schema) -> Table:
    """
    Stream inference with Tensorflow model for the input table.
    tf_cluster_config includes all the information to run the training cluster.

    This method add a number of nodes with different node types
    in the deep learning cluster to the given statement_set. Therefore, user
    should invoke execute on statement_set to run the deep learning cluster
    at the end.

    User is responsible to insert the returned table into the statement_set so
    that the Tensorflow cluster runs in the same Flink job.

    :param statement_set: The statement set to add the deep learning tables.
    :param input_table: The input data to inference.
    :param tf_cluster_config: The configuration of the Tensorflow cluster.
    :param schema: The schema of the output Table.
    :return: The output Table produced by Tensorflow model inference process.
    """
    if statement_set is None:
        raise ValueError("statement_set cannot be None.")

    if input_table is None:
        raise ValueError("input_table cannot be None.")

    if tf_cluster_config is None:
        raise ValueError("tf_cluster_config cannot be None.")

    if schema is None:
        raise ValueError("schema cannot be None")

    # noinspection PyProtectedMember
    j_table = get_gateway().jvm.org.flinkextended \
        .flink.ml.tensorflow.client.TFUtils.inference(
        statement_set._j_statement_set,
        input_table._j_table,
        tf_cluster_config._to_j_tf_cluster_config(),
        schema._j_schema)

    # noinspection PyProtectedMember
    return Table(j_table, statement_set._t_env)


def train(statement_set: StatementSet, tf_cluster_config: TFClusterConfig,
          input_table: Optional[Table] = None, max_epoch: int = 1):
    """
    Train a Tensorflow deep learning model. If the input_table is None, the
    max_epoch is ignored. Users should read the input data in their entry
    function written with Tensorflow.

    If input_table is provided, the deep learning model is trained iteratively
    with the input data from Flink up to the given maximum number epoch. User
    can terminate the training earlier by exiting the entry. The input_table
    should be bounded, if the max_eopch is greater than 1. Otherwise, the model
    is trained indefinitely with the unbounded data at the first epoch. User can
    use the TFDataSet to read data from Flink. The tf_cluster_config includes
    all the information to run the training cluster.

    This method adds a number of nodes with different node types
    in the deep learning cluster to the given statement_set. Therefore, user
    should invoke execute on statement_set to run the deep learning cluster
    at the end.

    :param statement_set: The statement set to add the deep learning tables.
    :param tf_cluster_config: The configuration of the Tensorflow cluster.
    :param input_table: The input data to the training process.
    :param max_epoch: Maximum number of epoch to train the model.
    """
    if statement_set is None:
        raise ValueError("statement_set cannot be None.")

    if tf_cluster_config is None:
        raise ValueError("tf_cluster_config cannot be None.")

    if input_table is None:
        # noinspection PyProtectedMember
        get_gateway().jvm.org.flinkextended \
            .flink.ml.tensorflow.client.TFUtils.train(
            statement_set._j_statement_set,
            tf_cluster_config._to_j_tf_cluster_config())
    else:
        if max_epoch == 1:
            # noinspection PyProtectedMember
            get_gateway().jvm.org.flinkextended \
                .flink.ml.tensorflow.client.TFUtils.train(
                statement_set._j_statement_set,
                input_table._j_table,
                tf_cluster_config._to_j_tf_cluster_config())
        elif max_epoch > 1:
            # noinspection PyProtectedMember
            get_gateway().jvm.org.flinkextended \
                .flink.ml.tensorflow.client.TFUtils.train(
                statement_set._j_statement_set,
                input_table._j_table,
                tf_cluster_config._to_j_tf_cluster_config(),
                max_epoch)
        else:
            raise ValueError(f"Invalid max_epoch {max_epoch}.")


def tensorboard(statement_set: StatementSet,
                tf_cluster_config: TFClusterConfig):
    """
    Start a TensorBoard service in the Tensorflow cluster. This method is
    commonly used with the train method. User can look for the "TensorBoard
    *.*.* at http://****:**/" log of the TaskManager that runs the tensorboard
    operator to get the ip and port to access the Tensorboard.

    The started TensorBoard service will look for the model checkpoint at the
    path specified in tf_cluster_config. User should make sure that the training
    function write the checkpoint to the same path.

    :param statement_set: The statement set to add the deep learning tables.
    :param tf_cluster_config: The configuration of the Tensorflow cluster.
    """
    if statement_set is None:
        raise ValueError("statement_set cannot be None.")

    if tf_cluster_config is None:
        raise ValueError("tf_cluster_config cannot be None.")

    # noinspection PyProtectedMember
    get_gateway().jvm.org.flinkextended \
        .flink.ml.tensorflow.client.TFUtils.tensorBoard(
        statement_set._j_statement_set,
        tf_cluster_config._to_j_tf_cluster_config())
