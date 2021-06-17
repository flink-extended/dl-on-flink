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
from typing import List

from streamz import Stream

from ai_flow import ModelMeta, ExampleSupportType, PythonObjectExecutor, ModelType, ExecutionMode
from ai_flow.endpoint.server.server_runner import AIFlowServerRunner
from ai_flow.util.path_util import get_file_dir
from ai_flow.model_center.entity.model_version_stage import ModelVersionStage
from ai_flow.udf.function_context import FunctionContext
from python_ai_flow import ExampleExecutor, Executor
from python_ai_flow.test import test_util
import tensorflow as tf
import ai_flow as af


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


class BatchModelValidate(Executor):
    def __init__(self):
        super().__init__()
        self.path = None
        self.model_version = None

    def setup(self, function_context: FunctionContext):
        model_name = function_context.node_spec.model.name
        notifications = af.list_events(key=model_name)
        self.path = json.loads(notifications[0].value).get('_model_path')
        self.model_version = json.loads(notifications[0].value).get('_model_version')

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        save_path = self.path
        new_model_version = self.model_version
        model_meta: ModelMeta = function_context.node_spec.model
        serving_model_version = af.get_deployed_model_version(model_name=model_meta.name)
        if serving_model_version is None:
            af.update_model_version(model_name=model_meta.name, model_version=new_model_version,
                                    current_stage=ModelVersionStage.VALIDATED)
            print('the first serving model version is ', new_model_version)
        else:
            x_test, y_test = input_list[0][0], input_list[0][1]
            model = tf.keras.models.load_model(save_path)
            result = model.evaluate(x_test, y_test, verbose=2)
            base_model = tf.keras.models.load_model(serving_model_version.model_path)
            result_base = base_model.evaluate(x_test, y_test, verbose=2)
            model_validate_result = af.register_artifact(name='model_validate',
                                                         batch_uri=get_file_dir(__file__) + '/model_batch_validate')
            if function_context.job_context.execution_mode == ExecutionMode.BATCH:
                file_uri = model_validate_result.batch_uri
            else:
                file_uri = model_validate_result.stream_uri
            with open(file_uri, 'a') as f:
                f.write(str(result_base) + ' -------> ' + 'previous model version: ' + serving_model_version.version)
                f.write('\n')
                f.write(str(result) + ' -------> ' + 'base model version: ' + new_model_version)
                f.write('\n')
            if result[1] > result_base[1]:
                af.update_model_version(model_name=model_meta.name,
                                        model_version=serving_model_version.version,
                                        current_stage=ModelVersionStage.DEPRECATED)
                af.update_model_version(model_name=model_meta.name, model_version=new_model_version,
                                        current_stage=ModelVersionStage.VALIDATED)
                print('the serving model version is ', new_model_version)
            else:
                print('the serving model version is ', serving_model_version.version)
        return []


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
        event_type = 'model_listener'
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
                save_path = 'saved_models/{}'.format((round(time.time() * 1000)))
                model.save(save_path, save_format='tf')
                af.register_model_version(
                    model_id=model_meta.uuid,
                    model_path=save_path)

                return df

        while self.path is None:
            pass

        load_path = self.path
        sess = tf.Session()
        graph = tf.get_default_graph()
        tf.compat.v1.keras.backend.set_session(sess)
        model = tf.keras.models.load_model(load_path)
        print('model update!')
        data: Stream = input_list[0]
        data.map(train, model, sess, graph).sink(sink)
        return []


class TestModelValidateComponent(unittest.TestCase):
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
        TestModelValidateComponent.server_runner._clear_db()

    def test_batch_model_validate(self):
        input_example_meta = af.register_example(name='batch_train_example',
                                                 support_type=ExampleSupportType.EXAMPLE_BOTH)
        model_meta = af.register_model(model_name='mnist_model',
                                       model_type=ModelType.SAVED_MODEL)
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='evaluate')):
            input_example = af.read_example(example_info=input_example_meta,
                                            executor=PythonObjectExecutor(python_object=ReadBatchExample()))

            batch_train = af.train(input_data_list=[input_example],
                                   executor=PythonObjectExecutor(python_object=TrainBatchMnistModel()),
                                   model_info=model_meta)

            model_validate = af.model_validate(input_data_list=[input_example],
                                               model_info=model_meta,
                                               executor=PythonObjectExecutor(python_object=BatchModelValidate()),
                                               output_num=0)
        af.stop_before_control_dependency(model_validate, batch_train)
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)
