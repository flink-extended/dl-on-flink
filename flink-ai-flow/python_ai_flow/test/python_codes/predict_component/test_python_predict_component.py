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
import json
import os
import threading
import time
import unittest
from typing import List

from ai_flow.util.path_util import get_file_dir
from streamz import Stream
from ai_flow.meta.model_meta import ModelType, ModelMeta
from ai_flow.executor.executor import PythonObjectExecutor
from ai_flow.meta.example_meta import ExampleSupportType, ExampleMeta
from ai_flow.endpoint.server.server_runner import AIFlowServerRunner
from ai_flow.udf.function_context import FunctionContext
from python_ai_flow import ExampleExecutor, Executor
from python_ai_flow.test import test_util
import ai_flow as af
import tensorflow as tf


class ReadBatchExample(ExampleExecutor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data(path='mnist.npz')
        return [[x_train, y_train, x_test, y_test]]


def get_compiled_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    return model


class TrainBatchMnistModel(Executor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        model = get_compiled_model()
        model.compile(optimizer='adam',
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy', 'mse'])
        x_train, y_train = input_list[0][0] / 255.0, input_list[0][1]
        model.fit(x_train, y_train, epochs=1)
        model_meta: ModelMeta = function_context.node_spec.output_model
        save_path = 'saved_models/{}'.format(round(time.time() * 1000))
        model.save(save_path, save_format='tf')
        af.register_model_version(model=model_meta,
                                  model_path=save_path)


class PredictBatchMnistModel(Executor):
    def __init__(self):
        super().__init__()
        self.path = None

    def setup(self, function_context: FunctionContext):
        model_name = function_context.node_spec.model.name
        notifications = af.list_events(key=model_name)
        self.path = json.loads(notifications[0].value).get('_model_path')

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        save_path = self.path
        x_predict = input_list[0][2] / 255.0
        model = tf.keras.models.load_model(save_path)
        result = model.predict_classes(x_predict)
        return [result]


class SourceThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.stream = Stream()

    def run(self) -> None:
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data(path='mnist.npz')
        for _ in range(0, 4):
            print('The example has been read {} times'.format(_ + 1))
            self.stream.emit(x_test)
            time.sleep(2)


class ReadStreamExample(ExampleExecutor):
    def setup(self, function_context: FunctionContext):
        self.thread = SourceThread()

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        self.thread.start()
        return [self.thread.stream]


class PredictStreamMnistModel(Executor):
    def __init__(self):
        super().__init__()
        self.path = None

    def setup(self, function_context: FunctionContext):
        model_name = function_context.node_spec.model.name
        notifications = af.list_events(key=model_name)
        self.path = json.loads(notifications[0].value).get('_model_path')

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        def predict(df, model, sess, graph):
            x_predict = df / 255.0
            with graph.as_default():
                tf.compat.v1.keras.backend.set_session(sess)
                result = model.predict_classes(x_predict)
                return result

        save_path = self.path
        sess = tf.Session()
        graph = tf.get_default_graph()
        tf.compat.v1.keras.backend.set_session(sess)
        model = tf.keras.models.load_model(save_path)

        data: Stream = input_list[0]
        return [data.map(predict, model, sess, graph)]


class WriteStreamExample(ExampleExecutor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        example_meta: ExampleMeta = function_context.node_spec.example_meta

        def sink(df):
            pass

        def write_example(df):
            path = example_meta.stream_uri
            with open(path, 'a') as f:
                df = df.tolist()
                for d in df:
                    f.write(str(d))
                    f.write('    ')
                f.write('\n')
            return df

        data: Stream = input_list[0]
        data.map(write_example).sink(sink)
        return []


class TestPredictComponent(unittest.TestCase):
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
        TestPredictComponent.server_runner._clear_db()

    def test_batch_predict_component(self):
        input_example_meta = af.register_example(name='input_train_example',
                                                 support_type=ExampleSupportType.EXAMPLE_BOTH)
        model_meta = af.register_model(model_name='mnist_model')
        batch_output_file = get_file_dir(__file__) + '/batch_predict'
        evaluate_output = af.register_artifact(name='batch_evaluate',
                                               batch_uri=batch_output_file)
        output_example_meta = af.register_example(name='output_result_example',
                                                  support_type=ExampleSupportType.EXAMPLE_BATCH,
                                                  data_type='numpy',
                                                  data_format='txt',
                                                  batch_uri=batch_output_file)
        if os.path.exists(batch_output_file):
            os.remove(batch_output_file)
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='batch_predict')):
            batch_example = af.read_example(example_info=input_example_meta,
                                            executor=PythonObjectExecutor(python_object=ReadBatchExample()))
            batch_train = af.train(input_data_list=[batch_example],
                                   executor=PythonObjectExecutor(python_object=TrainBatchMnistModel()),
                                   model_info=model_meta)
            batch_predict = af.predict(input_data_list=[batch_example], model_info=model_meta,
                                       executor=PythonObjectExecutor(python_object=PredictBatchMnistModel()),
                                       output_num=1)
            af.write_example(input_data=batch_predict, example_info=output_example_meta)
        af.stop_before_control_dependency(batch_predict, batch_train)
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)

    def test_stream_predict_component(self):
        batch_example_meta = af.register_example(name='batch_train_example',
                                                 support_type=ExampleSupportType.EXAMPLE_BOTH)
        model_meta = af.register_model(model_name='mnist_model')
        stream_predict_example_meta = af.register_example(name='stream_predict_example',
                                                          support_type=ExampleSupportType.EXAMPLE_STREAM)
        stream_output_file = get_file_dir(__file__) + '/stream_predict'
        evaluate_output = af.register_artifact(name='stream_evaluate',
                                               batch_uri=stream_output_file)
        stream_predict_result_example_meta = af.register_example(name='stream_result_example',
                                                                 support_type=ExampleSupportType.EXAMPLE_STREAM,
                                                                 stream_uri=stream_output_file)
        if os.path.exists(stream_output_file):
            os.remove(stream_output_file)
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='stream_predict')):
            batch_example = af.read_example(example_info=batch_example_meta,
                                            executor=PythonObjectExecutor(python_object=ReadBatchExample()))
            stream_predict_example = af.read_example(example_info=stream_predict_example_meta,
                                                     executor=PythonObjectExecutor(
                                                         python_object=ReadStreamExample()))
            batch_train = af.train(input_data_list=[batch_example],
                                   executor=PythonObjectExecutor(python_object=TrainBatchMnistModel()),
                                   model_info=model_meta)
            stream_predict = af.predict(input_data_list=[stream_predict_example], model_info=model_meta,
                                        executor=PythonObjectExecutor(python_object=PredictStreamMnistModel()),
                                        output_num=1)
            af.write_example(input_data=stream_predict, example_info=stream_predict_result_example_meta,
                             executor=PythonObjectExecutor(python_object=WriteStreamExample()))
        af.stop_before_control_dependency(stream_predict, batch_train)
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)
