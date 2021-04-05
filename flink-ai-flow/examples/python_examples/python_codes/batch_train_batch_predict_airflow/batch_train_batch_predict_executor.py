import json
import os
import shutil
import time
from typing import List
import numpy as np
from joblib import dump, load
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.utils import check_random_state
import ai_flow as af
from ai_flow import ModelMeta
from ai_flow.model_center.entity.model_version_stage import ModelVersionStage
from python_ai_flow import FunctionContext, Executor, ExampleExecutor
from ai_flow.common.path_util import get_file_dir


class ExampleReader(ExampleExecutor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        f = np.load(function_context.node_spec.example_meta.batch_uri)
        x_train, y_train = f['x_train'], f['y_train']
        f.close()
        print("## {} ## is Done".format(self.__class__.__name__))
        return [[x_train, y_train]]


class ExampleTransformer(Executor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        x_train, y_train = input_list[0][0], input_list[0][1]
        # f = np.load('/opt/flink-ai-flow/examples/python_examples/example_data/mnist_train.npz')
        # x_train, y_train = f['x_train'], f['y_train']
        # f.close()
        random_state = check_random_state(0)
        permutation = random_state.permutation(x_train.shape[0])
        x_train, y_train = x_train[permutation], y_train[permutation]
        x_train = x_train.reshape((x_train.shape[0], -1))
        res = [[StandardScaler().fit_transform(x_train), y_train]]
        print("## {} ## is Done".format(self.__class__.__name__))
        return res


class ModelTrainer(Executor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        # https://scikit-learn.org/stable/auto_examples/linear_model/plot_sparse_logistic_regression_mnist.html
        clf = LogisticRegression(C=50. / 5000, penalty='l1', solver='saga', tol=0.1)
        print("## {} ## is Start2".format(self.__class__.__name__))
        x_train, y_train = input_list[0][0], input_list[0][1]
        print("## {} ## is Start3".format(self.__class__.__name__))
        print("Fit Start")
        clf.fit(x_train, y_train)
        print("Fit Done")
        model_path = get_file_dir(__file__) + '/' + 'saved_model'
        if not os.path.exists(model_path):
            os.makedirs(model_path)
        model_version = time.strftime("%Y%m%d%H%M%S", time.localtime())
        model_path = model_path + '/' + model_version
        dump(clf, model_path)
        print("$$$$$")
        print(model_path)
        af.register_model_version(model=function_context.node_spec.output_model, model_path=model_path)

        print("## {} ## is Done".format(self.__class__.__name__))
        return []


class EvaluateExampleReader(ExampleExecutor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        f = np.load(function_context.node_spec.example_meta.batch_uri)
        x_test, y_test = f['x_test'], f['y_test']
        f.close()
        print("## {} ## is Done".format(self.__class__.__name__))
        return [[x_test, y_test]]


class EvaluateTransformer(Executor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        x_test, y_test = input_list[0][0], input_list[0][1]
        random_state = check_random_state(0)
        permutation = random_state.permutation(x_test.shape[0])
        x_test, y_test = x_test[permutation], y_test[permutation]
        x_test = x_test.reshape((x_test.shape[0], -1))
        print("## {} ## is Done".format(self.__class__.__name__))
        return [[StandardScaler().fit_transform(x_test), y_test]]


class ModelEvaluator(Executor):

    def __init__(self):
        super().__init__()
        self.model_path = None
        self.model_version = None

    def setup(self, function_context: FunctionContext):
        notifications = af.list_events(key=function_context.node_spec.model.name)
        print(notifications[0].value)
        self.model_path = json.loads(notifications[0].value).get('_model_path')
        self.model_version = json.loads(notifications[0].value).get('_model_version')

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        x_evaluate, y_evaluate = input_list[0][0], input_list[0][1]
        clf = load(self.model_path)
        scores = cross_val_score(clf, x_evaluate, y_evaluate, cv=5)
        evaluate_artifact = af.get_artifact_by_name('evaluate_artifact').batch_uri
        with open(evaluate_artifact, 'a') as f:
            f.write('model version[{}] scores: {}\n'.format(self.model_version, scores))

        print("## {} ## is Done".format(self.__class__.__name__))
        return []


class ValidateExampleReader(ExampleExecutor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        f = np.load(function_context.node_spec.example_meta.batch_uri)
        x_test, y_test = f['x_test'], f['y_test']
        f.close()
        print("## {} ## is Done".format(self.__class__.__name__))
        return [[x_test, y_test]]


class ValidateTransformer(Executor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        x_test, y_test = input_list[0][0], input_list[0][1]
        random_state = check_random_state(0)
        permutation = random_state.permutation(x_test.shape[0])
        x_test, y_test = x_test[permutation], y_test[permutation]
        x_test = x_test.reshape((x_test.shape[0], -1))
        print("## {} ## is Done".format(self.__class__.__name__))
        return [[StandardScaler().fit_transform(x_test), y_test]]


class ModelValidator(Executor):

    def __init__(self):
        super().__init__()
        self.model_path = None
        self.model_version = None

    def setup(self, function_context: FunctionContext):
        notifications = af.list_events(key=function_context.node_spec.model.name)
        self.model_path = json.loads(notifications[0].value).get('_model_path')
        self.model_version = json.loads(notifications[0].value).get('_model_version')

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        model_meta: ModelMeta = function_context.node_spec.model
        serving_model_version = af.get_deployed_model_version(model_name=model_meta.name)
        if serving_model_version is None:
            af.update_model_version(model_name=model_meta.name,
                                    model_version=self.model_version,
                                    current_stage=ModelVersionStage.DEPLOYED)

        else:
            x_validate, y_validate = input_list[0][0], input_list[0][1]
            scoring = ['precision_macro', 'recall_macro']
            serving_clf = load(serving_model_version.model_path)
            serving_scores = cross_validate(serving_clf, x_validate, y_validate, scoring=scoring)
            clf = load(self.model_path)
            scores = cross_validate(clf, x_validate, y_validate, scoring=scoring)
            batch_uri = af.get_artifact_by_name('validate_artifact').batch_uri
            with open(batch_uri, 'a') as f:
                f.write('serving model version[{}] scores: {}\n'.format(serving_model_version.version, serving_scores))
                f.write('generated model version[{}] scores: {}\n'.format(self.model_version, scores))
            if scores.mean() > serving_scores.mean():
                af.update_model_version(model_name=model_meta.name,
                                        model_version=serving_model_version.version,
                                        current_stage=ModelVersionStage.VALIDATED)
                af.update_model_version(model_name=model_meta.name,
                                        model_version=self.model_version,
                                        current_stage=ModelVersionStage.DEPLOYED)
        print("## {} ## is Done".format(self.__class__.__name__))
        return []


class ModelPusher(Executor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        node_spec = function_context.node_spec
        serving_model_path = af.get_artifact_by_name('push_model_artifact').batch_uri
        if not os.path.exists(serving_model_path):
            os.makedirs(serving_model_path)
        serving_model_version = None
        if serving_model_version is None:
            serving_model_version = af.get_deployed_model_version(model_name=node_spec.model.name)
        for file in os.listdir(serving_model_path):
            file_path = os.path.join(serving_model_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path, True)
        shutil.copy(serving_model_version.model_path, serving_model_path)
        print("## {} ## is Done".format(self.__class__.__name__))
        return []


class PredictExampleReader(ExampleExecutor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        f = np.load(function_context.node_spec.example_meta.batch_uri)
        x_test = f['x_test']
        f.close()
        print("## {} ## is Done".format(self.__class__.__name__))
        return [[x_test]]


class PredictTransformer(Executor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        x_test = input_list[0][0]
        random_state = check_random_state(0)
        permutation = random_state.permutation(x_test.shape[0])
        x_test = x_test[permutation]
        x_test = x_test.reshape((x_test.shape[0], -1))
        print("## {} ## is Done".format(self.__class__.__name__))
        return [[StandardScaler().fit_transform(x_test)]]


class ModelPredictor(Executor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        model_artifact = af.get_artifact_by_name('push_model_artifact').batch_uri
        clf = load(os.path.join(model_artifact, os.listdir(model_artifact)[0]))
        print("## {} ## is Done".format(self.__class__.__name__))
        return [clf.predict(input_list[0][0])]


class ExampleWriter(ExampleExecutor):

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("## {} ## is Start".format(self.__class__.__name__))
        np.savetxt(function_context.node_spec.example_meta.batch_uri, input_list[0])
        print("## {} ## is Done".format(self.__class__.__name__))
        return []
