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
import unittest
import os
import ai_flow as af
from ai_flow import AIFlowServerRunner, ExampleSupportType, ExecuteArgs, PythonObjectExecutor, FunctionContext, List
import numpy as np
from python_ai_flow.test import test_util
from python_ai_flow import Executor


class TransformTrainData(Executor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        return [input_list[0]['arr_0'], input_list[0]['arr_1']]


class TestBaseExampleComponent(unittest.TestCase):
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
        TestBaseExampleComponent.server_runner._clear_db()

    def test_read_example_with_pandas(self):
        input_example_meta = af.register_example(name='input_pandas_example',
                                                 data_type='pandas',
                                                 data_format='csv',
                                                 support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                 batch_uri=os.path.abspath(os.path.dirname(__file__)
                                                                           + '/test1.csv'))
        output_example_meta = af.register_example(name='ouput_pandas_example',
                                                  data_type='pandas',
                                                  data_format='csv',
                                                  support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                  batch_uri=os.path.abspath(os.path.dirname(__file__)
                                                                            + '/pandas_output.csv'))
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='test_csv')):
            example_channel = af.read_example(example_info=input_example_meta)
            af.write_example(input_data=example_channel, example_info=output_example_meta)
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)

    def test_read_example_with_numpy_npy(self):
        npy_name = 'test.npy'
        np.save(file=npy_name, arr=np.arange(10))
        input_example_meta = af.register_example(name='input_numpy_example',
                                                 data_type='numpy',
                                                 data_format='npy',
                                                 support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                 batch_uri=os.path.abspath(os.path.dirname(__file__)
                                                                           + "/" + npy_name))
        output_example_meta = af.register_example(name='ouput_numpy_example',
                                                  data_type='numpy',
                                                  data_format='npy',
                                                  support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                  batch_uri=os.path.abspath(os.path.dirname(__file__)
                                                                            + '/numpy_output.npy'))
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='test_npy')):
            example_channel = af.read_example(example_info=input_example_meta)
            af.write_example(input_data=example_channel, example_info=output_example_meta)
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)

    def test_read_example_with_numpy_txt(self):
        npy_name = 'test.txt'
        np.savetxt(fname=npy_name, X=np.arange(10))
        input_example_meta = af.register_example(name='input_numpy_example',
                                                 data_type='numpy',
                                                 data_format='txt',
                                                 support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                 batch_uri=os.path.abspath(os.path.dirname(__file__)
                                                                           + "/" + npy_name))
        output_example_meta = af.register_example(name='ouput_numpy_example',
                                                  data_type='numpy',
                                                  data_format='txt',
                                                  support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                  batch_uri=os.path.abspath(os.path.dirname(__file__)
                                                                            + '/numpy_output.txt'))
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='test_txt')):
            example_channel = af.read_example(example_info=input_example_meta)
            af.write_example(input_data=example_channel, example_info=output_example_meta)
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)

    def test_read_example_with_numpy_npz(self):
        npy_name = 'test.npz'
        np.savez(npy_name, np.arange(10), np.sin(np.arange(10)))
        input_example_meta = af.register_example(name='input_numpy_example',
                                                 data_type='numpy',
                                                 data_format='npz',
                                                 support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                 batch_uri=os.path.abspath(os.path.dirname(__file__)
                                                                           + "/" + npy_name))
        output_example_meta_first = af.register_example(name='ouput_numpy_example_1',
                                                        data_type='numpy',
                                                        data_format='npz',
                                                        support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                        batch_uri=os.path.abspath(os.path.dirname(__file__)
                                                                                  + '/numpy_output_1.npz'))
        output_example_meta_second = af.register_example(name='ouput_numpy_example_2',
                                                         data_type='numpy',
                                                         data_format='npz',
                                                         support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                         batch_uri=os.path.abspath(os.path.dirname(__file__)
                                                                                   + '/numpy_output_2.npz'))
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='test_npz')):
            example_channel = af.read_example(example_info=input_example_meta)
            transform_channel = af.transform(input_data_list=[example_channel],
                                             executor=PythonObjectExecutor(python_object=TransformTrainData()),
                                             output_num=2)
            af.write_example(input_data=transform_channel[0], example_info=output_example_meta_first)
            af.write_example(input_data=transform_channel[1], example_info=output_example_meta_second)
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)
