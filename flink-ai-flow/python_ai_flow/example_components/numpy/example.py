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
import numpy as np
from python_ai_flow.python_job_common import BaseExampleComponent, Executor
from typing import List, Text
from ai_flow.udf.function_context import FunctionContext
from ai_flow.common.args import ExecuteArgs


class NumpyIOExample(BaseExampleComponent):
    class SourceExecutor(Executor):
        def __init__(self,
                     file_format: Text,
                     file: Text,
                     args: ExecuteArgs) -> None:
            super().__init__()
            self.file_format = file_format
            self.file = file
            self.kwargs = args

        def execute(self, context: FunctionContext, args: List = None) -> List:
            if self.kwargs is not None:
                tmp_args = self.kwargs
            else:
                tmp_args = {}
            if self.file_format.strip().lower() == 'npz':
                return [np.load(file=self.file, **tmp_args)]
            elif self.file_format.strip().lower() == 'npy':
                return [np.load(file=self.file, **tmp_args)]
            elif self.file_format.strip().lower() == 'txt':
                return [np.loadtxt(fname=self.file, **tmp_args)]
            else:
                raise Exception("numpy do not support " + self.file_format)

    class SinkExecutor(Executor):
        def __init__(self,
                     file_format: Text,
                     file: Text,
                     args: ExecuteArgs) -> None:
            super().__init__()
            self.file_format = file_format
            self.file = file
            self.kwargs = args

        def execute(self, context: FunctionContext, args: List = None) -> List:
            if self.kwargs is not None:
                tmp_args = self.kwargs
            else:
                tmp_args = {}
            arr = args[0]
            if self.file_format.strip().lower() == 'npy':
                return [np.save(file=self.file, arr=arr, **tmp_args)]
            elif self.file_format.strip().lower() == 'npz':
                return [np.savez(self.file, arr, **tmp_args)]
            elif self.file_format.strip().lower() == 'txt':
                return [np.savetxt(fname=self.file, X=arr, **tmp_args)]
            else:
                raise Exception("numpy do not support " + self.file_format)

    def batch_executor(self) -> Executor:
        if self.is_source:
            return NumpyIOExample.SourceExecutor(
                file_format=self.example_meta.data_format,
                file=self.example_meta.batch_uri,
                args=self.example_node.execute_properties.batch_properties)
        else:
            return NumpyIOExample.SinkExecutor(
                file_format=self.example_meta.data_format,
                file=self.example_meta.batch_uri,
                args=self.example_node.execute_properties.batch_properties)

    def stream_executor(self):
        if self.is_source:
            return NumpyIOExample.SourceExecutor(
                file_format=self.example_meta.data_format,
                file=self.example_meta.stream_uri,
                args=self.example_node.execute_properties.stream_properties)
        else:
            return NumpyIOExample.SinkExecutor(
                file_format=self.example_meta.data_format,
                file=self.example_meta.stream_uri,
                args=self.example_node.execute_properties.stream_properties)
