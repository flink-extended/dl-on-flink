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
from pyflink.stream.datastream import DataStream, DataStreamSource
from pyflink.util.type_util import TypesUtil


def inference(num_worker, num_ps=0, func=None, properties=None, env_path=None, zk_conn=None, zk_base_path=None,
              stream_env=None, input_ds=None, output_row_type=None):
    """
    Tensorflow inference for DataStream
    :param zk_conn: The Zookeeper connection string
    :param zk_base_path: The Zookeeper base path
    :param num_worker: Number of workers
    :param num_ps: Number of PS
    :param func: The user-defined function that runs TF inference. If it's None, inference is run via Java API.
    :param properties: User-defined properties
    :param env_path: Path to the virtual env
    :param stream_env: The StreamExecutionEnvironment. If it's None, this method will create one and execute the job
                       at the end. Otherwise, caller is responsible to trigger the job execution
    :param input_ds: The input DataStream
    :param output_row_type: The RowType for the output DataStream. If it's None, a dummy sink will be added to the
                      output DataStream. Otherwise, caller is responsible to add sink before executing the job.
    :return: The output DataStream. Currently it's always of type Row.
    """
    tf_config = TFConfig(num_worker, num_ps, func, properties, env_path, zk_conn, zk_base_path)
    execute = stream_env is None
    if stream_env is None:
        stream_env = StreamExecutionEnvironment.get_execution_environment()
    if input_ds is not None:
        if isinstance(input_ds, DataStreamSource):
            input_ds = input_ds._j_datastream_source
        else:
            input_ds = input_ds._j_datastream
    output_ds = get_gateway().jvm.com.alibaba.flink.tensorflow.client.TFUtils.inference(stream_env._j_env, input_ds,
                                                                                        tf_config.java_config(),
                                                                                        to_row_type_info(
                                                                                            output_row_type))
    if execute:
        stream_env.execute()
    return DataStream(output_ds)


def train(num_worker, num_ps, func, properties=None, env_path=None, zk_conn=None, zk_base_path=None,
          stream_env=None, input_ds=None, output_row_type=None):
    """
    Tensorflow training for DataStream
    :param zk_conn: The Zookeeper connection string
    :param zk_base_path: The Zookeeper base path
    :param num_worker: Number of workers
    :param num_ps: Number of PS
    :param func: The user-defined function that runs TF training
    :param properties: User-defined properties
    :param env_path: Path to the virtual env
    :param stream_env: The StreamExecutionEnvironment. If it's None, this method will create one and execute the job
                       at the end. Otherwise, caller is responsible to trigger the job execution
    :param input_ds: The input DataStream
    :param output_row_type: The RowType for the output DataStream. If it's None, a dummy sink will be added to the
                      output DataStream. Otherwise, caller is responsible to add sink before executing the job.
    :return: The output DataStream. Currently it's always of type Row.
    """
    tf_config = TFConfig(num_worker, num_ps, func, properties, env_path, zk_conn, zk_base_path)
    execute = stream_env is None
    if stream_env is None:
        stream_env = StreamExecutionEnvironment.get_execution_environment()
    if input_ds is not None:
        if isinstance(input_ds, DataStreamSource):
            input_ds = input_ds._j_datastream_source
        else:
            input_ds = input_ds._j_datastream
    output_ds = get_gateway().jvm.com.alibaba.flink.tensorflow.client.TFUtils.train(stream_env._j_env, input_ds,
                                                                                    tf_config.java_config(),
                                                                                    to_row_type_info(output_row_type))
    if execute:
        stream_env.execute()
    return DataStream(output_ds)


def to_row_type_info(row_type):
    if row_type is None:
        return None
    return get_gateway().jvm.com.alibaba.flink.tensorflow.util.TypeUtil.rowTypeToRowTypeInfo(
        TypesUtil.to_java_sql_type(row_type))
