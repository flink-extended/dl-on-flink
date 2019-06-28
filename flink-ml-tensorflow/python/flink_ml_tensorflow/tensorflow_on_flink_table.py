# Copyright 2019 The flink-ai-extended Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

from pyflink.java_gateway import get_gateway
from tensorflow_on_flink.pyflink_tensorflow import TFConfig
from pyflink.environment import StreamExecutionEnvironment
from pyflink.table.table_environment import TableEnvironment
from pyflink.table.table_environment import Table


def inference(num_worker, num_ps=0, func=None, properties=None, env_path=None, zk_conn=None, zk_base_path=None,
              stream_env=None, table_env=None, input_table=None, output_schema=None):
    """
    Tensorflow inference for Table
    :param zk_conn: The Zookeeper connection string
    :param zk_base_path: The Zookeeper base path
    :param num_worker: Number of workers
    :param num_ps: Number of PS
    :param func: The user-defined function that runs TF inference. If it's None, inference is run via Java API.
    :param properties: User-defined properties
    :param env_path: Path to the virtual env
    :param stream_env: The StreamExecutionEnvironment. If it's None, this method will create one and execute the job
                       at the end. Otherwise, caller is responsible to trigger the job execution
    :param table_env: The TableEnvironment
    :param input_table: The input Table
    :param output_schema: The TableSchema of the output Table. If it's None, a dummy sink will be added to the output
                          Table. Otherwise, caller is responsible to add sink before executing the job.
    :return: The output Table
    """
    tf_config = TFConfig(num_worker, num_ps, func, properties, env_path, zk_conn, zk_base_path)
    execute = stream_env is None
    if stream_env is None:
        stream_env = StreamExecutionEnvironment.get_execution_environment()
    if table_env is None:
        table_env = TableEnvironment.get_table_environment(stream_env)
    if input_table is not None:
        input_table = input_table._java_table
    if output_schema is not None:
        output_schema = output_schema._j_table_schema
    output_table = get_gateway().jvm.com.alibaba.flink.tensorflow.client.TFUtils.inference(stream_env._j_env,
                                                                                           table_env._j_tenv,
                                                                                           input_table,
                                                                                           tf_config.java_config(),
                                                                                           output_schema)
    if execute:
        table_env.execute()
    return Table(java_table=output_table)


def train(num_worker, num_ps, func, properties=None, env_path=None, zk_conn=None, zk_base_path=None,
          stream_env=None, table_env=None, input_table=None, output_schema=None):
    """
    Tensorflow training for Table
    :param zk_conn: The Zookeeper connection string
    :param zk_base_path: The Zookeeper base path
    :param num_worker: Number of workers
    :param num_ps: Number of PS
    :param func: The user-defined function that runs TF training
    :param properties: User-defined properties
    :param env_path: Path to the virtual env
    :param stream_env: The StreamExecutionEnvironment. If it's None, this method will create one and execute the job
                       at the end. Otherwise, caller is responsible to trigger the job execution
    :param table_env: The TableEnvironment
    :param input_table: The input Table
    :param output_schema: The TableSchema of the output Table. If it's None, a dummy sink will be added to the output
                          Table. Otherwise, caller is responsible to add sink before executing the job.
    :return: The output Table
    """
    tf_config = TFConfig(num_worker, num_ps, func, properties, env_path, zk_conn, zk_base_path)
    execute = stream_env is None
    if stream_env is None:
        stream_env = StreamExecutionEnvironment.get_execution_environment()
    if table_env is None:
        table_env = TableEnvironment.get_table_environment(stream_env)
    if input_table is not None:
        input_table = input_table._java_table
    if output_schema is not None:
        output_schema = output_schema._j_table_schema
    output_table = get_gateway().jvm.com.alibaba.flink.tensorflow.client.TFUtils.train(stream_env._j_env,
                                                                                       table_env._j_tenv, input_table,
                                                                                       tf_config.java_config(),
                                                                                       output_schema)
    if execute:
        table_env.execute()
    return Table(java_table=output_table)
