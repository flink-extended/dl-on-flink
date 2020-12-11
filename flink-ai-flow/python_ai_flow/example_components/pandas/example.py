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
import pandas as pd
from python_ai_flow.python_job_common import BaseExampleComponent, Executor
from typing import List, Text
from ai_flow.udf.function_context import FunctionContext
from ai_flow.common.args import ExecuteArgs


class PandasIOExample(BaseExampleComponent):
    class SourceExecutor(Executor):

        def __init__(self,
                     file_format: Text,
                     file_or_buffer: Text,
                     args: ExecuteArgs) -> None:
            super().__init__()
            self.file_format = file_format
            self.file_or_buffer = file_or_buffer
            self.kwargs = args

        def execute(self, context: FunctionContext, args: List = None) -> List:
            if self.kwargs is not None:
                tmp_args = self.kwargs
            else:
                tmp_args = {}
            if self.file_format.strip().lower() == "csv":
                return [pd.read_csv(filepath_or_buffer=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "json":
                return [pd.read_json(path_or_buf=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "html":
                return [pd.read_html(io=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "clipboard":
                return [pd.read_clipboard(**tmp_args)]
            elif self.file_format.strip().lower() == "excel":
                return [pd.read_excel(io=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "hdf":
                return [pd.read_hdf(path_or_buf=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "feather":
                return [pd.read_feather(path=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "parquet":
                return [pd.read_parquet(path=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "msgpack":
                return [pd.read_msgpack(path_or_buf=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "stata":
                return [pd.read_stata(filepath_or_buffer=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "sas":
                return [pd.read_sas(filepath_or_buffer=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "pickle":
                return [pd.read_pickle(path=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "sql":
                return [pd.read_sql(**tmp_args)]
            elif self.file_format.strip().lower() == "sql_query":
                return [pd.read_sql_query(**tmp_args)]
            elif self.file_format.strip().lower() == "sql_table":
                return [pd.read_sql_table(**tmp_args)]
            elif self.file_format.strip().lower() == "gbq":
                return [pd.read_gbq(**tmp_args)]
            else:
                raise Exception("pandas do not support " + self.file_format)

    class SinkExecutor(Executor):

        def __init__(self,
                     file_format: Text,
                     file_or_buffer: Text,
                     args: ExecuteArgs) -> None:
            super().__init__()
            self.file_format = file_format
            self.file_or_buffer = file_or_buffer
            self.kwargs = args

        def execute(self, context: FunctionContext, args: List = None):
            if self.kwargs is not None:
                tmp_args = self.kwargs
            else:
                tmp_args = {}
            df: pd.DataFrame = args[0]
            if self.file_format.strip().lower() == "csv":
                return [df.to_csv(path_or_buf=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "json":
                return [df.to_json(path_or_buf=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "html":
                return [df.to_html(buf=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "clipboard":
                return [df.to_clipboard(**tmp_args)]
            elif self.file_format.strip().lower() == "excel":
                return [df.to_excel(self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "hdf":
                return [df.to_hdf(path_or_buf=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "feather":
                return [df.to_feather(fname=self.file_or_buffer)]
            elif self.file_format.strip().lower() == "parquet":
                return [df.to_parquet(fname=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "msgpack":
                return [df.to_msgpack(path_or_buf=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "stata":
                return [df.to_stata(fname=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "pickle":
                return [df.to_pickle(path=self.file_or_buffer, **tmp_args)]
            elif self.file_format.strip().lower() == "sql":
                return [df.to_sql(**tmp_args)]
            elif self.file_format.strip().lower() == "gbq":
                return [df.to_gbq(**tmp_args)]
            else:
                raise Exception("pandas do not support " + self.file_format)

    def batch_executor(self) -> Executor:
        if self.is_source:
            return PandasIOExample.SourceExecutor(
                file_format=self.example_meta.data_format,
                file_or_buffer=self.example_meta.batch_uri,
                args=self.example_node.execute_properties.batch_properties)
        else:
            return PandasIOExample.SinkExecutor(
                file_format=self.example_meta.data_format,
                file_or_buffer=self.example_meta.batch_uri,
                args=self.example_node.execute_properties.batch_properties)

    def stream_executor(self):
        if self.is_source:
            return PandasIOExample.SourceExecutor(
                file_format=self.example_meta.data_format,
                file_or_buffer=self.example_meta.stream_uri,
                args=self.example_node.execute_properties.stream_properties)
        else:
            return PandasIOExample.SinkExecutor(
                file_format=self.example_meta.data_format,
                file_or_buffer=self.example_meta.stream_uri,
                args=self.example_node.execute_properties.stream_properties)
