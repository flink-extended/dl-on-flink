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
import threading
import time
import unittest
from typing import List

from streamz import Stream

import ai_flow as af
import pandas as pd

from ai_flow.executor.executor import PythonObjectExecutor
from ai_flow.endpoint.server.server_runner import AIFlowServerRunner
from ai_flow.util.path_util import get_file_dir
from ai_flow.meta.example_meta import ExampleSupportType, ExampleMeta
from ai_flow.udf.function_context import FunctionContext
from python_ai_flow.test import test_util
from python_ai_flow import Executor, ExampleExecutor


class ReadBatchExample(ExampleExecutor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        example: ExampleMeta = function_context.node_spec.example_meta
        batch_uri = example.batch_uri
        df = pd.read_csv(batch_uri, header=None, names=['a', 'b', 'c'])
        return [df]


class WriteBatchExample(ExampleExecutor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        example: ExampleMeta = function_context.node_spec.example_meta
        batch_uri = example.batch_uri
        df: pd.DataFrame = input_list[0]
        df.to_csv(path_or_buf=batch_uri, index=0)


class SourceThread(threading.Thread):
    def __init__(self, stream_uri):
        super().__init__()
        self.stream_uri = stream_uri
        self.stream = Stream()

    def run(self) -> None:
        for _ in range(0, 4):
            print('The example has been read {} times'.format(_ + 1))
            df = pd.read_csv(self.stream_uri, header=None, names=['a', 'b', 'c'])
            self.stream.emit(df)
            time.sleep(5)


class ReadStreamExample(ExampleExecutor):

    def setup(self, function_context: FunctionContext):
        super().setup(function_context)
        example: ExampleMeta = function_context.node_spec.example_meta
        stream_uri = example.stream_uri
        self.thread = SourceThread(stream_uri)

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        self.thread.start()
        return [self.thread.stream]


class WriteStreamExample(ExampleExecutor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        def write(df, stream_uri):
            print('write to {}'.format(stream_uri))
            df.to_csv(path_or_buf=stream_uri, index=0, mode='a')

        example: ExampleMeta = function_context.node_spec.example_meta
        stream_uri = example.stream_uri
        data: Stream = input_list[0]
        data.map(write, stream_uri).sink(print)
        return []


class TransformBatchData(Executor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        df: pd.DataFrame = input_list[0]
        return [df[['a', 'c']]]


class TransformStreamData(Executor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        def transform(df):
            return df[['a', 'b']]

        data: Stream = input_list[0]
        return [data.map(transform)]


class TestDataComponent(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config_file = test_util.get_master_config_file()
        cls.server_runner = AIFlowServerRunner(config_file=config_file)
        cls.server_runner.start()
        test_util.set_project_config(__file__)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server_runner.stop()
        af.unset_project_config()

    def tearDown(self):
        TestDataComponent.server_runner._clear_db()

    def test_batch_example_component(self):
        file = get_file_dir(__file__) + '/test1.csv'
        input_example_meta = af.register_example(name='test_example',
                                                 support_type=ExampleSupportType.EXAMPLE_BOTH,
                                                 batch_uri=file)
        output_file = get_file_dir(__file__) + "/output_batch_test1.csv"
        output_example_meta = af.register_example(name='test_example_output',
                                                  support_type=ExampleSupportType.EXAMPLE_BOTH,
                                                  batch_uri=output_file)
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='batch_example')):
            input_example = af.read_example(example_info=input_example_meta,
                                            executor=PythonObjectExecutor(python_object=ReadBatchExample()))
            af.write_example(input_data=input_example,
                             example_info=output_example_meta.name,
                             executor=PythonObjectExecutor(python_object=WriteBatchExample()))
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)

    def test_stream_example_component(self):
        file = get_file_dir(__file__) + '/test1.csv'
        input_example_meta = af.register_example(name='test_example',
                                                 support_type=ExampleSupportType.EXAMPLE_BOTH,
                                                 stream_uri=file)
        output_file = get_file_dir(__file__) + "/output_stream_test1.csv"
        output_example_meta = af.register_example(name='test_example_output',
                                                  support_type=ExampleSupportType.EXAMPLE_BOTH,
                                                  stream_uri=output_file)
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='stream_example')):
            input_example = af.read_example(example_info=input_example_meta,
                                            executor=PythonObjectExecutor(python_object=ReadStreamExample()))
            af.write_example(input_data=input_example,
                             example_info=output_example_meta.name,
                             executor=PythonObjectExecutor(python_object=WriteStreamExample()))
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)

    def test_batch_transform_component(self):
        file = get_file_dir(__file__) + '/test1.csv'
        input_example_meta = af.register_example(name='test_example',
                                                 support_type=ExampleSupportType.EXAMPLE_BOTH,
                                                 batch_uri=file)
        output_file = get_file_dir(__file__) + "/output_transform_batch_test1.csv"
        output_example_meta = af.register_example(name='test_example_output',
                                                  support_type=ExampleSupportType.EXAMPLE_BOTH,
                                                  batch_uri=output_file)
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='batch_transform')):
            input_example = af.read_example(example_info=input_example_meta,
                                            executor=PythonObjectExecutor(python_object=ReadBatchExample()))
            transform_example = af.transform(input_data_list=[input_example],
                                             executor=PythonObjectExecutor(python_object=TransformBatchData()))
            af.write_example(input_data=transform_example, example_info=output_example_meta,
                             executor=PythonObjectExecutor(python_object=WriteBatchExample()))
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)

    def test_stream_transform_component(self):
        file = get_file_dir(__file__) + '/test1.csv'
        input_example_meta = af.register_example(name='test_example',
                                                 support_type=ExampleSupportType.EXAMPLE_BOTH,
                                                 stream_uri=file)
        output_file = get_file_dir(__file__) + "/output_transform_stream_test1.csv"
        output_example_meta = af.register_example(name='test_example_output',
                                                  support_type=ExampleSupportType.EXAMPLE_BOTH,
                                                  stream_uri=output_file)
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='stream_transform')):
            input_example = af.read_example(example_info=input_example_meta,
                                            executor=PythonObjectExecutor(python_object=ReadStreamExample()))
            transform_example = af.transform(input_data_list=[input_example],
                                             executor=PythonObjectExecutor(python_object=TransformStreamData()))

            af.write_example(input_data=transform_example,
                             example_info=output_example_meta.name,
                             executor=PythonObjectExecutor(python_object=WriteStreamExample()))
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)
