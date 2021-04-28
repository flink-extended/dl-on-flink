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
from typing import List
import numpy as np
from joblib import dump, load
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.utils import check_random_state
import ai_flow as af
from ai_flow.model_center.entity.model_version_stage import ModelVersionStage
from python_ai_flow import FunctionContext, Executor, ExampleExecutor
from ai_flow.common.path_util import get_file_dir


def preprocess_data(x_data, y_data=None):
    random_state = check_random_state(0)
    permutation = random_state.permutation(x_data.shape[0])
    if y_data is None:
        return x_data[permutation]
    else:
        return x_data[permutation], y_data[permutation]


class ExampleReader(ExampleExecutor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        with np.load(function_context.node_spec.example_meta.batch_uri) as f:
            x_train, y_train = f['x_train'], f['y_train']
        return [[x_train, y_train]]


class ExampleTransformer(Executor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        x_train, y_train = preprocess_data(input_list[0][0], input_list[0][1])
        x_train = x_train.reshape((x_train.shape[0], -1))
        return [[StandardScaler().fit_transform(x_train), y_train]]


class ModelTrainer(Executor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        # https://scikit-learn.org/stable/auto_examples/linear_model/plot_sparse_logistic_regression_mnist.html
        clf = LogisticRegression(C=50. / 5000, penalty='l1', solver='saga', tol=0.1)
        x_train, y_train = input_list[0][0], input_list[0][1]
        clf.fit(x_train, y_train)
        model_path = get_file_dir(__file__) + '/saved_model'
        if not os.path.exists(model_path):
            os.makedirs(model_path)
        model_timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        model_path = model_path + '/' + model_timestamp
        dump(clf, model_path)
        af.register_model_version(model=function_context.node_spec.output_model, model_path=model_path)

        return []


class EvaluateExampleReader(ExampleExecutor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        with np.load(function_context.node_spec.example_meta.batch_uri) as f:
            x_test, y_test = f['x_test'], f['y_test']
        return [[x_test, y_test]]


class EvaluateTransformer(Executor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        x_test, y_test = preprocess_data(input_list[0][0], input_list[0][1])
        x_test = x_test.reshape((x_test.shape[0], -1))
        return [[StandardScaler().fit_transform(x_test), y_test]]


class ModelEvaluator(Executor):

    def __init__(self, artifact):
        super().__init__()
        self.model_path = None
        self.model_version = None
        self.artifact = artifact

    def setup(self, function_context: FunctionContext):
        print(function_context.node_spec.model.name)
        model = af.get_latest_generated_model_version(function_context.node_spec.model.name)
        self.model_path = model.model_path
        self.model_version = model.version

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        x_evaluate, y_evaluate = input_list[0][0], input_list[0][1]
        clf = load(self.model_path)
        scores = cross_val_score(clf, x_evaluate, y_evaluate, cv=5)
        evaluate_artifact = af.get_artifact_by_name(self.artifact).batch_uri
        with open(evaluate_artifact, 'a') as f:
            f.write('model version[{}] scores: {}\n'.format(self.model_version, scores))

        return []


class ValidateExampleReader(ExampleExecutor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        with np.load(function_context.node_spec.example_meta.batch_uri) as f:
            x_test, y_test = f['x_test'], f['y_test']
        return [[x_test, y_test]]


class ValidateTransformer(Executor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        x_test, y_test = preprocess_data(input_list[0][0], input_list[0][1])
        x_test = x_test.reshape((x_test.shape[0], -1))
        return [[StandardScaler().fit_transform(x_test), y_test]]


class ModelValidator(Executor):

    def __init__(self, artifact):
        super().__init__()
        self.model_name = None
        self.model_path = None
        self.model_version = None
        self.artifact = artifact

    def setup(self, function_context: FunctionContext):
        self.model_name = function_context.node_spec.model.name
        model = af.get_latest_generated_model_version(self.model_name)
        self.model_path = model.model_path
        self.model_version = model.version

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        deployed_model_version = af.get_deployed_model_version(model_name=self.model_name)

        if deployed_model_version is None:
            af.update_model_version(model_name=self.model_name,
                                    model_version=self.model_version,
                                    current_stage=ModelVersionStage.VALIDATED)

        else:
            x_validate, y_validate = input_list[0][0], input_list[0][1]
            clf = load(self.model_path)
            scores = cross_val_score(clf, x_validate, y_validate, scoring='precision_macro', cv=5)
            deployed_clf = load(deployed_model_version.model_path)
            deployed_scores = cross_val_score(deployed_clf, x_validate, y_validate, scoring='precision_macro')

            batch_uri = af.get_artifact_by_name(self.artifact).batch_uri
            if np.mean(scores) > np.mean(deployed_scores):
                af.update_model_version(model_name=self.model_name,
                                        model_version=self.model_version,
                                        current_stage=ModelVersionStage.VALIDATED)
                with open(batch_uri, 'a') as f:
                    f.write('deployed model version[{}] scores: {}\n'.format(deployed_model_version.version,
                                                                             deployed_scores))
                    f.write('generated model version[{}] scores: {}\n'.format(self.model_version, scores))
        return []


class ModelPusher(Executor):
    def __init__(self, artifact):
        super().__init__()
        self.artifact = artifact

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        model_name = function_context.node_spec.model.name
        validated_model = af.get_latest_validated_model_version(model_name)

        cur_deployed_model = af.get_deployed_model_version(model_name=model_name)
        if cur_deployed_model is not None:
            af.update_model_version(model_name=model_name,
                                    model_version=cur_deployed_model.version,
                                    current_stage=ModelVersionStage.DEPRECATED)
        af.update_model_version(model_name=model_name,
                                model_version=validated_model.version,
                                current_stage=ModelVersionStage.DEPLOYED)

        # Copy deployed model to deploy_model_dir
        deployed_model_dir = af.get_artifact_by_name(self.artifact).batch_uri
        if not os.path.exists(deployed_model_dir):
            os.makedirs(deployed_model_dir)
        for file in os.listdir(deployed_model_dir):
            file_path = os.path.join(deployed_model_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path, True)
        shutil.copy(validated_model.model_path, deployed_model_dir)
        return []


class PredictExampleReader(ExampleExecutor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        with np.load(function_context.node_spec.example_meta.batch_uri) as f:
            x_test = f['x_test']
        return [[x_test]]


class PredictTransformer(Executor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        x_test = preprocess_data(input_list[0][0], None)
        x_test = x_test.reshape((x_test.shape[0], -1))
        return [[StandardScaler().fit_transform(x_test)]]


class ModelPredictor(Executor):
    def __init__(self):
        super().__init__()

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        model_name = function_context.node_spec.model.name
        model_meta = af.get_deployed_model_version(model_name)
        clf = load(model_meta.model_path)
        return [clf.predict(input_list[0][0])]


class ExampleWriter(ExampleExecutor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        np.savetxt(function_context.node_spec.example_meta.batch_uri, input_list[0])
        return []