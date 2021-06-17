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
import threading
import time
import unittest
import os
from typing import List

from streamz import Stream

import ai_flow as af
from ai_flow.meta.model_meta import ModelMeta, ModelType
from ai_flow.executor.executor import PythonObjectExecutor
from ai_flow.meta.example_meta import ExampleSupportType

from ai_flow.endpoint.server.server_runner import AIFlowServerRunner
from ai_flow.udf.function_context import FunctionContext
from python_ai_flow import ExampleExecutor, Executor
from python_ai_flow.test import test_util
import tensorflow as tf


class ReadBatchExample(ExampleExecutor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data(path='mnist.npz')
        return [[x_train, y_train]]


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
        save_path = 'saved_models/{}'.format(round(time.time()))
        model.save(save_path, save_format='tf')
        af.register_model_version(model=model_meta.uuid,
                                  model_path=save_path)
        return []


class TrainBatchMnistModelWithOutput(Executor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        model = get_compiled_model()
        model.compile(optimizer='adam',
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy', 'mse'])
        x_train, y_train = input_list[0][0] / 255.0, input_list[0][1]
        model.fit(x_train, y_train, epochs=1)
        model_meta: ModelMeta = function_context.node_spec.output_model
        save_path = 'saved_models/{}'.format(round(time.time()))
        model.save(save_path, save_format='tf')
        af.register_model_version(model=model_meta.uuid,
                                  model_path=save_path)
        return [x_train, y_train]


class SourceThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.stream = Stream()

    def run(self) -> None:
        (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data(path='mnist.npz')
        for _ in range(0, 4):
            print('The example has been read {} times'.format(_ + 1))
            self.stream.emit((x_train, y_train))
            time.sleep(1)


class ReadStreamExample(ExampleExecutor):
    def setup(self, function_context: FunctionContext):
        self.thread = SourceThread()

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        self.thread.start()
        return [self.thread.stream]


class TrainStreamMnistModel(Executor):
    def __init__(self):
        super().__init__()
        self.path = None

    def setup(self, function_context: FunctionContext):
        model_name = function_context.node_spec.output_model.name
        notifications = af.list_events(key=model_name)
        self.path = json.loads(notifications[0].value).get('_model_path')

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        def sink(df):
            pass

        def train(df, model, sess, graph):
            x_train, y_train = df[0] / 255.0, df[1]
            with graph.as_default():
                tf.compat.v1.keras.backend.set_session(sess)
                model.fit(x_train, y_train, epochs=1)
                model_meta: ModelMeta = function_context.node_spec.output_model
                save_path = 'saved_models/{}'.format((round(time.time())))
                model.save(save_path, save_format='tf')
                af.register_model_version(
                    model=model_meta.uuid,
                    model_path=save_path)

                return df

        while self.path is None:
            pass

        data: Stream = input_list[0]
        load_path = self.path

        sess = tf.Session()
        graph = tf.get_default_graph()
        tf.compat.v1.keras.backend.set_session(sess)
        model = tf.keras.models.load_model(load_path)

        print('model update!')
        data.map(train, model, sess, graph).sink(sink)
        return []


class TestTrainComponent(unittest.TestCase):
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
        TestTrainComponent.server_runner._clear_db()

    def test_batch_train_component(self):
        input_example_meta = af.register_example(name='batch_train_example',
                                                 support_type=ExampleSupportType.EXAMPLE_BATCH)
        model_meta = af.register_model(model_name='mnist_model',
                                       model_type=ModelType.SAVED_MODEL)
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='batch_train')):
            input_example = af.read_example(example_info=input_example_meta,
                                            executor=PythonObjectExecutor(python_object=ReadBatchExample()))
            af.train(input_data_list=[input_example],
                     executor=PythonObjectExecutor(python_object=TrainBatchMnistModel()),
                     model_info=model_meta)
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)

    def test_batch_train_component_with_an_output(self):
        input_example_meta = af.register_example(name='batch_train_example',
                                                 support_type=ExampleSupportType.EXAMPLE_BATCH)
        model_meta = af.register_model(model_name='mnist_model',
                                       model_type=ModelType.SAVED_MODEL)

        example_meta = af.register_example(name='output_example', support_type=ExampleSupportType.EXAMPLE_BATCH,
                                           data_type='numpy', data_format='npz',
                                           batch_uri=os.path.abspath(os.path.dirname(__file__)
                                                                     + '/numpy_output.npz')
                                           )
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='batch_train')):
            input_example = af.read_example(example_info=input_example_meta,
                                            executor=PythonObjectExecutor(python_object=ReadBatchExample()))
            train_channel = af.train(input_data_list=[input_example],
                                     executor=PythonObjectExecutor(python_object=TrainBatchMnistModelWithOutput()),
                                     model_info=model_meta,
                                     output_num=1
                                     )
            af.write_example(input_data=train_channel, example_info=example_meta)
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)

    def test_stream_train_component(self):
        batch_input_example_meta = af.register_example(name='stream_train_example',
                                                       support_type=ExampleSupportType.EXAMPLE_BOTH)
        model_meta = af.register_model(model_name='mnist_model',
                                       model_type=ModelType.SAVED_MODEL)
        stream_input_example_meta = af.register_example(name='stream_train_example',
                                                        support_type=ExampleSupportType.EXAMPLE_BOTH)
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='stream_train')):
            batch_input_example = af.read_example(example_info=batch_input_example_meta,
                                                  executor=PythonObjectExecutor(python_object=ReadBatchExample()))
            batch_train = af.train(input_data_list=[batch_input_example],
                                   executor=PythonObjectExecutor(python_object=TrainBatchMnistModel()),
                                   model_info=model_meta)
            stream_input_example = af.read_example(example_info=stream_input_example_meta,
                                                   executor=PythonObjectExecutor(python_object=ReadStreamExample()))
            stream_train = af.train(input_data_list=[stream_input_example],
                                    executor=PythonObjectExecutor(python_object=TrainStreamMnistModel()),
                                    model_info=model_meta)
        af.stop_before_control_dependency(stream_train, batch_train)
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)
