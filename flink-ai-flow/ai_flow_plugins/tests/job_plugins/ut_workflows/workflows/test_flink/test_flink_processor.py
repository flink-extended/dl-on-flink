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
import os
import shutil
import time
from typing import List

from ai_flow_plugins.job_plugins.flink.flink_processor import UDFWrapper
from pyflink.table import Table, DataTypes, ScalarFunction
from pyflink.table.descriptors import Schema, OldCsv, FileSystem
from pyflink.table.udf import udf

from ai_flow_plugins.job_plugins import flink


class PassUDF(ScalarFunction):

    def eval(self, s):
        return s


class Transformer(flink.FlinkPythonProcessor):
    def process(self, execution_context: flink.ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        execution_context.table_env.register_function("pass_func", udf(PassUDF(),
                                                                       input_types=[DataTypes.STRING()],
                                                                       result_type=DataTypes.STRING()))
        return [input_list[0].group_by('word').select('pass_func(word), count(1)')]


class SleepUDF(ScalarFunction):

    def eval(self, s):
        time.sleep(100)
        return s


class Transformer2(flink.FlinkPythonProcessor):
    def process(self, execution_context: flink.ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        execution_context.table_env.register_function("sleep_func", udf(SleepUDF(),
                                                                        input_types=[DataTypes.STRING()],
                                                                        result_type=DataTypes.STRING()))
        return [input_list[0].group_by('word').select('sleep_func(word), count(1)')]


class Source(flink.FlinkPythonProcessor):
    def process(self, execution_context: flink.ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        input_file = os.path.join(os.getcwd(), 'resources', 'word_count.txt')
        t_env = execution_context.table_env
        t_env.connect(FileSystem().path(input_file)) \
            .with_format(OldCsv()
                         .field('word', DataTypes.STRING())) \
            .with_schema(Schema()
                         .field('word', DataTypes.STRING())) \
            .create_temporary_table('mySource')
        return [t_env.from_path('mySource')]


class Sink(flink.FlinkPythonProcessor):
    def process(self, execution_context: flink.ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        output_file = os.path.join(os.getcwd(), 'output')
        if os.path.exists(output_file):
            os.remove(output_file)

        t_env = execution_context.table_env
        statement_set = execution_context.statement_set
        t_env.connect(FileSystem().path(output_file)) \
            .with_format(OldCsv()
                         .field_delimiter('\t')
                         .field('word', DataTypes.STRING())
                         .field('count', DataTypes.BIGINT())) \
            .with_schema(Schema()
                         .field('word', DataTypes.STRING())
                         .field('count', DataTypes.BIGINT())) \
            .create_temporary_table('mySink')
        statement_set.add_insert('mySink', input_list[0])
        return []


class SinkWithExecuteSql(flink.FlinkPythonProcessor):
    def process(self,
                execution_context: flink.ExecutionContext,
                input_list: List[Table] = None) -> List[Table]:
        output_file = os.path.join(os.getcwd(), 'output')
        if os.path.exists(output_file):
            os.remove(output_file)

        t_env = execution_context.table_env
        t_env.connect(FileSystem().path(output_file)) \
            .with_format(OldCsv()
                         .field_delimiter('\t')
                         .field('word', DataTypes.STRING())
                         .field('count', DataTypes.BIGINT())) \
            .with_schema(Schema()
                         .field('word', DataTypes.STRING())
                         .field('count', DataTypes.BIGINT())) \
            .create_temporary_table('mySink')
        t_env.execute_sql(f"""
        INSERT INTO mySink
        SELECT *
        FROM {input_list[0]}
        """)
        return []


class SinkWithAddInsertSql(flink.FlinkPythonProcessor):
    def process(self,
                execution_context: flink.ExecutionContext,
                input_list: List[Table] = None) -> List[Table]:
        output_file = os.path.join(os.getcwd(), 'output')
        if os.path.exists(output_file):
            os.remove(output_file)

        t_env = execution_context.table_env
        s_set = execution_context.statement_set
        t_env.connect(FileSystem().path(output_file)) \
            .with_format(OldCsv()
                         .field_delimiter('\t')
                         .field('word', DataTypes.STRING())
                         .field('count', DataTypes.BIGINT())) \
            .with_schema(Schema()
                         .field('word', DataTypes.STRING())
                         .field('count', DataTypes.BIGINT())) \
            .create_temporary_table('mySink')
        s_set.add_insert_sql(f"""
        INSERT INTO mySink
        SELECT *
        FROM {input_list[0]}
        """)
        return []


class SourceSql(flink.FlinkSqlProcessor):
    def __init__(self):
        super().__init__()
        self.input_file = None

    def open(self, execution_context: flink.ExecutionContext):
        self.input_file = os.path.join(os.getcwd(), 'resources', 'word_count.txt')

    def sql_statements(self, execution_context: flink.ExecutionContext) -> List[str]:
        table_source_stmt = '''
                           CREATE TABLE mySource (
                               word STRING 
                           ) WITH (
                               'connector' = 'filesystem',
                               'path' = '{uri}',
                               'format' = 'csv',
                               'csv.ignore-parse-errors' = 'true'
                           )
                            '''.format(uri=self.input_file)
        return [table_source_stmt]


class SinkSql(flink.FlinkSqlProcessor):
    def __init__(self):
        super().__init__()
        self.output_file = None

    def open(self, execution_context: flink.ExecutionContext):
        self.output_file = os.path.join(os.getcwd(), 'output')

        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        if os.path.isdir(self.output_file):
            shutil.rmtree(self.output_file)

    def udf_list(self, execution_context: flink.ExecutionContext) -> List[UDFWrapper]:
        return [UDFWrapper(name='pass_func', func=udf(PassUDF(),
                                                      input_types=[DataTypes.STRING()],
                                                      result_type=DataTypes.STRING()))]

    def sql_statements(self, execution_context: flink.ExecutionContext) -> List[str]:
        table_sink_stmt = '''
                           CREATE TABLE mySink (
                               newword STRING
                           ) WITH (
                               'connector' = 'filesystem',
                               'path' = '{uri}',
                               'format' = 'csv',
                               'csv.ignore-parse-errors' = 'true'
                           )
        '''.format(uri=self.output_file)
        insert_stmt = 'INSERT INTO mySink SELECT pass_func(word) FROM mySource'
        return [table_sink_stmt, insert_stmt]
