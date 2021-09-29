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
import time
from pyflink.table import TableConfig, ScalarFunction, FunctionContext, DataTypes, Table
from pyflink.table.table_environment import StreamTableEnvironment, TableEnvironment
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table.udf import udf
from sklearn.linear_model import LogisticRegression
from joblib import dump, load
import numpy as np
from typing import List
from ai_flow_plugins.job_plugins import flink
from ai_flow_plugins.job_plugins.flink.flink_processor import ExecutionContext


class LRModel(object):
    def __init__(self, model_path):
        self.model_path = model_path
        self.lr_model = self.lr()

    def lr(self):
        return LogisticRegression(C=50. / 5000, penalty='l1', solver='saga', tol=0.1)

    def fit(self, x_train, y_train):
        self.lr_model.fit(x_train, y_train)

    def load_model(self, model_path):
        self.lr_model = load(model_path)

    def save_model(self):
        version = str(round(time.time()))
        real_path = '{}/{}'.format(self.model_path, version)
        dump(self.lr_model, real_path)


class MNISTDataConverter(object):

    @staticmethod
    def convert_to_sample(data):
        x_train = []
        y_train = []
        for i in data:
            record = i.split(',')
            x = record[:-2]
            x_train.append(x)
            y = record[-2]
            y_train.append(y)
        x_train = np.array(x_train).astype(int)
        y_train = np.array(y_train).astype(int)
        return x_train, y_train


class MNISTTrain(ScalarFunction):

    def __init__(self, model_path, batch_size):
        super().__init__()
        self.results = []
        self.model_path = model_path
        self.lr_model = None
        self.batch_size = batch_size

    def open(self, function_context: FunctionContext):
        self.lr_model = LRModel(self.model_path)

    def eval(self, record):
        self.results.append(record)
        if len(self.results) == self.batch_size:
            x, y = MNISTDataConverter.convert_to_sample(self.results)
            self.lr_model.fit(x, y)
            self.lr_model.save_model()
            self.results.clear()
        return None


class MNISTStreamSource(flink.FlinkPythonProcessor):

    def __init__(self, topic) -> None:
        super().__init__()
        self.topic = topic

    def process(self, execution_context: ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        table_env: TableEnvironment = execution_context.table_env
        table_env.execute_sql('''
                            create table mnist_data (
                                record varchar
                            ) with (
                                'connector' = 'kafka',
                                'topic' = '{}',
                                'properties.bootstrap.servers' = 'localhost:9092',
                                'properties.group.id' = 'mnist_stream_data',
                                'format' = 'csv',
                                'csv.field-delimiter' = ' ',
                                'scan.startup.mode' = 'earliest-offset'
                            )
                        '''.format(self.topic))
        table = table_env.from_path('mnist_data')
        return [table]


class MNISTStreamTrain(flink.FlinkPythonProcessor):

    def __init__(self, model_path, batch_size) -> None:
        super().__init__()
        self.model_path = model_path
        self.batch_size = batch_size

    def process(self, execution_context: ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        table_env: TableEnvironment = execution_context.table_env
        table_env.register_function('train',
                                    udf(f=MNISTTrain(self.model_path, self.batch_size),
                                        input_types=[DataTypes.STRING(), DataTypes.STRING()],
                                        result_type=DataTypes.STRING()))
        table = input_list[0].select('train(record)')
        return [table]


class MNISTStreamSink(flink.FlinkPythonProcessor):

    def __init__(self, topic) -> None:
        super().__init__()
        self.topic = topic

    def process(self, execution_context: ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        table_env: TableEnvironment = execution_context.table_env
        table_env.execute_sql('''
                                create table print_sink (
                                    data varchar
                                ) with (
                                    'connector' = 'print'
                                )
                            ''')
        execution_context.statement_set.add_insert('print_sink', input_list[0])
        return []


def run_streaming_train(topic, batch_size, model_path):
    exec_env = StreamExecutionEnvironment.get_execution_environment()
    exec_env.set_parallelism(1)
    t_config = TableConfig()
    t_env = StreamTableEnvironment.create(exec_env, t_config)
    t_env.get_config().get_configuration().set_string("taskmanager.memory.task.off-heap.size", '80m')
    statement_set = t_env.create_statement_set()
    t_env.register_function('train',
                            udf(f=MNISTTrain(model_path, batch_size),
                                input_types=[DataTypes.STRING(), DataTypes.STRING()],
                                result_type=DataTypes.STRING()))

    t_env.execute_sql('''
                        create table mnist_data (
                            record varchar
                        ) with (
                            'connector' = 'kafka',
                            'topic' = '{}',
                            'properties.bootstrap.servers' = 'localhost:9092',
                            'properties.group.id' = 'mnist_stream_data',
                            'format' = 'csv',
                            'csv.field-delimiter' = ' ',
                            'scan.startup.mode' = 'earliest-offset'
                        )
                    '''.format(topic))

    t_env.execute_sql('''
                        create table print_sink (
                            data varchar
                        ) with (
                            'connector' = 'print'
                        )
                    ''')
    table = t_env.from_path('mnist_data').select('train(record)')
    statement_set.add_insert('print_sink', table)
    r = statement_set.execute()
    job_client = r.get_job_client()
    job_client.get_job_execution_result().result()


if __name__ == '__main__':
    topic_name = 'mnist_data'
    run_streaming_train(topic_name, 10000, '/tmp/model_dir')
