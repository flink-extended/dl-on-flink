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
import os
import shutil
import time
import unittest
from distutils.dir_util import copy_tree
from typing import List
from ai_flow import ExecutionMode
from ai_flow.meta.example_meta import ExampleSupportType
from ai_flow.executor.executor import PythonObjectExecutor
from ai_flow.meta.model_meta import ModelMeta, ModelType
from ai_flow.meta.artifact_meta import ArtifactMeta
from ai_flow.application_master.master import AIFlowMaster
from ai_flow.model_center.entity.model_version_stage import ModelVersionStage
from ai_flow.udf.function_context import FunctionContext
from python_ai_flow import Executor, ExampleExecutor
from python_ai_flow.test import test_util
import ai_flow as af
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
        save_path = 'saved_models/{}'.format(round(time.time() * 1000))
        model.save(save_path, save_format='tf')
        af.register_model_version(model=model_meta,
                                  model_path=save_path,
                                  current_stage=ModelVersionStage.VALIDATED)
        return []


class PushModel(Executor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        push_model_artifact = af.register_artifact(name='model_push', batch_uri='serving_model_path')
        serving_model_path = push_model_artifact.batch_uri
        if not os.path.exists(serving_model_path):
            os.makedirs(serving_model_path)
        serving_model_version = function_context.node_spec.model_version
        model_meta: ModelMeta = function_context.node_spec.model
        if serving_model_version is None:
            serving_model_version = af.get_latest_validated_model_version(model_name=model_meta.name)
        model_path = serving_model_version.model_path
        # delete the previous serving model verison
        dirs = os.listdir(serving_model_path)
        for f in dirs:
            file_path = os.path.join(serving_model_path, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path, True)
        # the new serving model version is on
        copy_tree(model_path, serving_model_path)
        print('serving model version={} is on serving!!!'.format(serving_model_version.version))
        return []


class TestPushComponent(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config_file = test_util.get_master_config_file()
        cls.master = AIFlowMaster(config_file=config_file)
        cls.master.start()
        test_util.set_project_config(__file__)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.master.stop()
        af.unset_project_config()

    def tearDown(self):
        TestPushComponent.master._clear_db()

    def test_push_component(self):
        input_example_meta = af.register_example(name='batch_train_example',
                                                 support_type=ExampleSupportType.EXAMPLE_BOTH)
        model_meta = af.register_model(model_name='mnist_model',
                                       model_type=ModelType.SAVED_MODEL)
        with af.config(af.BaseJobConfig(platform='local', engine='python', job_name='push')):
            input_example = af.read_example(example_info=input_example_meta,
                                            executor=PythonObjectExecutor(python_object=ReadBatchExample()))
            batch_train = af.train(input_data_list=[input_example],
                                   executor=PythonObjectExecutor(python_object=TrainBatchMnistModel()),
                                   model_info=model_meta)
            push_channel = af.push_model(model_info=model_meta,
                                         executor=PythonObjectExecutor(python_object=PushModel()))
        af.stop_before_control_dependency(push_channel, batch_train)
        workflow_id = af.run(test_util.get_project_path())
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)
