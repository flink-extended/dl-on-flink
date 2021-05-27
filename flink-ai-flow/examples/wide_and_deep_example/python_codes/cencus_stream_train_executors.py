#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from pyflink.datastream import StreamExecutionEnvironment
import ai_flow as af
from typing import List
from python_ai_flow import FunctionContext
import python_ai_flow as paf
import time
from flink_ai_flow.pyflink import TableEnvCreator, SourceExecutor, SinkExecutor, FlinkFunctionContext
import flink_ai_flow.pyflink as faf
from flink_ml_tensorflow.tensorflow_TFConfig import TFConfig
from flink_ml_tensorflow.tensorflow_on_flink_mlconf import MLCONSTANTS
from flink_ml_tensorflow.tensorflow_on_flink_table import train
from pyflink.table import StreamTableEnvironment, EnvironmentSettings, Table, TableEnvironment
from ai_flow.model_center.entity.model_version_stage import ModelVersionStage
from census_common import get_accuracy_score
from kafka_util import census_kafka_data


class StreamTableEnvCreator(TableEnvCreator):

    def create_table_env(self):
        stream_env = StreamExecutionEnvironment.get_execution_environment()
        stream_env.set_parallelism(1)
        t_env = StreamTableEnvironment.create(
            stream_env,
            environment_settings=EnvironmentSettings.new_instance().in_streaming_mode().use_blink_planner().build())
        statement_set = t_env.create_statement_set()
        t_env.get_config().set_python_executable('python')
        t_env.get_config().get_configuration().set_boolean('python.fn-execution.memory.managed', True)
        return stream_env, t_env, statement_set


class StreamPreprocessSource(SourceExecutor):

    def execute(self, function_context: FlinkFunctionContext) -> Table:
        table_env: TableEnvironment = function_context.get_table_env()
        table_env.execute_sql('''
            create table stream_train_preprocess_source (
                age varchar,
                workclass varchar,
                fnlwgt varchar,
                education varchar,
                education_num varchar,
                marital_status varchar,
                occupation varchar,
                relationship varchar,
                race varchar,
                gender varchar,
                capital_gain varchar,
                capital_loss varchar,
                hours_per_week varchar,
                native_country varchar,
                income_bracket varchar
            ) with (
                'connector' = 'kafka',
                'topic' = 'census_input_preprocess_topic',
                'properties.bootstrap.servers' = 'localhost:9092',
                'properties.group.id' = 'stream_train_preprocess_source',
                'format' = 'csv',
                'scan.startup.mode' = 'earliest-offset'
            )
        ''')
        table = table_env.from_path('stream_train_preprocess_source')
        return table


class StreamPreprocessExecutor(SinkExecutor):
    def execute(self, function_context: FlinkFunctionContext, input_table: Table) -> None:
        table_env: TableEnvironment = function_context.get_table_env()
        statement_set = function_context.get_statement_set()
        table_env.execute_sql('''
            create table stream_train_preprocess_sink (
                age varchar,
                workclass varchar,
                fnlwgt varchar,
                education varchar,
                education_num varchar,
                marital_status varchar,
                occupation varchar,
                relationship varchar,
                race varchar,
                gender varchar,
                capital_gain varchar,
                capital_loss varchar,
                hours_per_week varchar,
                native_country varchar,
                income_bracket varchar
            ) with (
                'connector' = 'kafka',
                'topic' = 'census_train_input_topic',
                'properties.bootstrap.servers' = 'localhost:9092',
                'properties.group.id' = 'stream_train_preprocess_sink',
                'format' = 'csv',
                'scan.startup.mode' = 'earliest-offset'
            )
        ''')
        statement_set.add_insert('stream_train_preprocess_sink', input_table)


class StreamTrainSource(SourceExecutor):

    def execute(self, function_context: FlinkFunctionContext) -> Table:
        table_env: TableEnvironment = function_context.get_table_env()
        table_env.execute_sql('''
            create table stream_train_source (
                age varchar,
                workclass varchar,
                fnlwgt varchar,
                education varchar,
                education_num varchar,
                marital_status varchar,
                occupation varchar,
                relationship varchar,
                race varchar,
                gender varchar,
                capital_gain varchar,
                capital_loss varchar,
                hours_per_week varchar,
                native_country varchar,
                income_bracket varchar
            ) with (
                'connector' = 'kafka',
                'topic' = 'census_train_input_topic',
                'properties.bootstrap.servers' = 'localhost:9092',
                'properties.group.id' = 'stream_train_source',
                'format' = 'csv',
                'scan.startup.mode' = 'earliest-offset'
            )
        ''')
        table = table_env.from_path('stream_train_source')
        return table


class StreamTrainExecutor(faf.Executor):

    def execute(self, function_context: FlinkFunctionContext, input_list: List[Table]) -> List[Table]:
        time.sleep(10)
        work_num = 2
        ps_num = 1
        python_file = 'census_distribute.py'
        func = 'stream_map_func'
        prop = {MLCONSTANTS.PYTHON_VERSION: '',
                MLCONSTANTS.ENCODING_CLASS: 'com.alibaba.flink.ml.operator.coding.RowCSVCoding',
                MLCONSTANTS.DECODING_CLASS: 'com.alibaba.flink.ml.operator.coding.RowCSVCoding',
                'sys:csv_encode_types': 'STRING,STRING,STRING,STRING,STRING,STRING,STRING,STRING,STRING,STRING,STRING,STRING,STRING,STRING,STRING',
                MLCONSTANTS.CONFIG_STORAGE_TYPE: MLCONSTANTS.STORAGE_ZOOKEEPER,
                MLCONSTANTS.CONFIG_ZOOKEEPER_CONNECT_STR: 'localhost:2181',
                MLCONSTANTS.CONFIG_ZOOKEEPER_BASE_PATH: '/demo',
                MLCONSTANTS.REMOTE_CODE_ZIP_FILE: "hdfs://localhost:9000/demo/code.zip"}
        env_path = None

        input_tb = function_context.t_env.from_path('stream_train_source')
        output_schema = None

        tf_config = TFConfig(work_num, ps_num, prop, python_file, func, env_path)

        train(function_context.get_exec_env(), function_context.get_table_env(), function_context.get_statement_set(),
              input_tb, tf_config, output_schema)


class StreamValidateExecutor(paf.Executor):
    def __init__(self):
        super().__init__()
        self.path = None
        self.model_version = None
        self.model_name = None

    def setup(self, function_context: FunctionContext):
        self.model_name = function_context.node_spec.model.name
        # wide_and_deep model
        self.model_version = af.get_latest_generated_model_version(self.model_name)
        print("#### name {}".format(self.model_name))
        print("#### path {}".format(self.model_version.model_path))
        self.path = self.model_version.model_path.split('|')[1]

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        deployed_version = af.get_deployed_model_version(self.model_name)
        if deployed_version is not None:
            test_data = '/tmp/census_data/adult.stream.validate'
            kafka_util = census_kafka_data.CensusKafkaUtil()
            count = 400
            kafka_util.read_data_into_file(kafka_util.census_train_input_topic, test_data, count)

            score = get_accuracy_score(self.path, test_data, count)
            deployed_version_score = get_accuracy_score(deployed_version.model_path.split('|')[1], test_data)
            if score > deployed_version_score:
                af.update_model_version(model_name=self.model_name,
                                        model_version=self.model_version.version,
                                        current_stage=ModelVersionStage.VALIDATED)
        else:
            af.update_model_version(model_name=self.model_name,
                                    model_version=self.model_version.version,
                                    current_stage=ModelVersionStage.VALIDATED)
        print("### {}".format("stream validation done"))
        return []


class StreamPushExecutor(paf.Executor):
    def __init__(self):
        super().__init__()
        self.model_name = None
        self.model_version = None

    def setup(self, function_context: FunctionContext):
        self.model_name = function_context.node_spec.model.name
        self.model_version = af.get_latest_validated_model_version(self.model_name)

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        deployed_version = af.get_deployed_model_version(self.model_name)

        if deployed_version is not None:
            af.update_model_version(model_name=self.model_name,
                                    model_version=deployed_version.version,
                                    current_stage=ModelVersionStage.DEPRECATED)

        af.update_model_version(model_name=self.model_name,
                                model_version=self.model_version.version,
                                current_stage=ModelVersionStage.DEPLOYED)

        return []
