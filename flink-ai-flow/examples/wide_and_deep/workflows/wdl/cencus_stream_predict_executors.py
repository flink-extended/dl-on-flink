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

from typing import List

import numpy as np
import tensorflow as tf
from pyflink.table import ScalarFunction, DataTypes
from pyflink.table import Table, TableEnvironment
from pyflink.table.udf import udf, FunctionContext

import ai_flow as af
from ai_flow_plugins.job_plugins.flink import FlinkPythonProcessor, ExecutionContext
from census_common import preprocess
from code import census_dataset


class StreamPredictPreprocessSource(FlinkPythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        table_env: TableEnvironment = execution_context.table_env
        table_env.execute_sql('''
            create table stream_predict_preprocess_source (
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
                'properties.group.id' = 'stream_predict_preprocess_source',
                'format' = 'csv',
                'scan.startup.mode' = 'earliest-offset'
            )
        ''')
        table = table_env.from_path('stream_predict_preprocess_source')
        return [table]


class StreamPredictPreprocessExecutor(FlinkPythonProcessor):
    def process(self, execution_context: ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        return input_list


class StreamPredictPreprocessSink(FlinkPythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        table_env: TableEnvironment = execution_context.table_env
        table_env.execute_sql('''
                    create table stream_predict_preprocess_sink (
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
                        native_country varchar
                    ) with (
                        'connector' = 'kafka',
                        'topic' = 'census_predict_input_topic',
                        'properties.bootstrap.servers' = 'localhost:9092',
                        'properties.group.id' = 'stream_predict_preprocess_sink',
                        'format' = 'csv',
                        'scan.startup.mode' = 'earliest-offset'
                    )
                ''')
        statement_set = execution_context.statement_set
        statement_set.add_insert('stream_predict_preprocess_sink', input_list[0].drop_columns('income_bracket'))
        return []


class StreamPredictSource(FlinkPythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        table_env: TableEnvironment = execution_context.table_env
        table_env.execute_sql('''
            create table stream_predict_source (
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
                native_country varchar
            ) with (
                'connector' = 'kafka',
                'topic' = 'census_predict_input_topic',
                'properties.bootstrap.servers' = 'localhost:9092',
                'properties.group.id' = 'stream_predict_source',
                'format' = 'csv',
                'scan.startup.mode' = 'earliest-offset'
            )
        ''')
        table = table_env.from_path('stream_predict_source')
        print("##### StreamPredictSource")
        return [table]


class Predict(ScalarFunction):

    def __init__(self, model_path):
        super().__init__()
        self._predictor = None
        self._exported_model = None
        self._model_path = model_path

    def open(self, function_context: FunctionContext):
        self._exported_model = self._model_path.split('|')[1]
        with tf.Session() as session:
            tf.saved_model.loader.load(session, [tf.saved_model.tag_constants.SERVING], self._exported_model)
            self._predictor = tf.contrib.predictor.from_saved_model(self._exported_model)

    def eval(self, age, workclass, fnlwgt, education, education_num, marital_status, occupation, relationship,
             race, gender, capital_gain, capital_loss, hours_per_week, native_country):
        try:
            arg_list = [age, workclass, fnlwgt, education, education_num, marital_status, occupation, relationship,
                        race, gender, capital_gain, capital_loss, hours_per_week, native_country]
            tmp = dict(zip(census_dataset.CSV_COLUMNS[:-1], arg_list))
            model_input = preprocess(tmp)
            output_dict = self._predictor({'inputs': [model_input]})
            print(str(np.argmax(output_dict['scores'])))
            return str(np.argmax(output_dict['scores']))
        except Exception:
            return 'tf fail'


class StreamPredictExecutor(FlinkPythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        model_version = af.get_deployed_model_version('wide_and_deep')
        print("##### StreamPredictExecutor {}".format(model_version.version))
        execution_context.table_env.register_function('predict',
                                                      udf(f=Predict(model_version.model_path),
                                                          input_types=[DataTypes.STRING(), DataTypes.STRING(),
                                                                       DataTypes.STRING(), DataTypes.STRING(),
                                                                       DataTypes.STRING(), DataTypes.STRING(),
                                                                       DataTypes.STRING(), DataTypes.STRING(),
                                                                       DataTypes.STRING(), DataTypes.STRING(),
                                                                       DataTypes.STRING(), DataTypes.STRING(),
                                                                       DataTypes.STRING(), DataTypes.STRING()],
                                                          result_type=DataTypes.STRING()))
        print("#### {}".format(self.__class__.__name__))
        return [input_list[0].add_columns(
            'predict(age, workclass, fnlwgt, education, education_num, marital_status, occupation, '
            'relationship, race, gender, capital_gain, capital_loss, hours_per_week, native_country) as income_bracket')]


class StreamPredictSink(FlinkPythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        table_env: TableEnvironment = execution_context.table_env
        statement_set = execution_context.statement_set
        table_env.execute_sql('''
            create table stream_predict_sink (
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
                'topic' = 'census_predict_output_topic',
                'properties.bootstrap.servers' = 'localhost:9092',
                'properties.group.id' = 'stream_predict_sink',
                'format' = 'csv',
                'scan.startup.mode' = 'earliest-offset'
            )
        ''')
        statement_set.add_insert('stream_predict_sink', input_list[0])
        print("#### {}".format(self.__class__.__name__))
        return []
