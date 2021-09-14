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
import glob
import os
import time

import numpy as np
from datetime import date, timedelta
from typing import List

from ai_flow.client.ai_flow_client import AIFlowClient
from joblib import dump, load
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LogisticRegression

from ai_flow.workflow.control_edge import MeetAllEventCondition

import ai_flow as af
from ai_flow.api.context_extractor import ContextExtractor, EventContext, ContextList, Broadcast
from ai_flow_plugins.job_plugins.python.python_processor import PythonProcessor, ExecutionContext
from notification_service.base_notification import BaseEvent, ANY_CONDITION


def _get_ai_flow_client_with_retry(max_retry: int, interval: float = 1.0) -> AIFlowClient:
    for retry in range(max_retry):
        try:
            client = af.get_ai_flow_client()
            return client
        except Exception as e:
            print(e)
            print("Error while getting AIFlowClient, retry: {}/{}".format(retry, max_retry))
            time.sleep(interval)
    raise Exception("Failed to get AIFlowClient")


class DailyWorkflowContextExtractor(ContextExtractor):

    def extract_context(self, event: BaseEvent) -> EventContext:
        context_list = ContextList()
        if event.event_type == 'DATA_EVENT' and 'daily_data' == event.key:
            context_list.add_context(event.context)
            return context_list

        return Broadcast()


class DailyTrainingReader(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        training_date = date.fromisoformat(execution_context.job_execution_info.workflow_execution.context)
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        daily_dir = os.path.join(dataset_meta.uri, training_date.isoformat())

        x_trains = []
        y_trains = []
        for np_name in glob.glob(os.path.join(daily_dir, '*.npz')):
            with np.load(np_name) as f:
                x_trains.append(f['x_train'])
                y_trains.append(f['y_train'])

        return [[np.concatenate(x_trains), np.concatenate(y_trains)]]


class DailyTrainingTrain(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        # https://scikit-learn.org/stable/auto_examples/linear_model/plot_sparse_logistic_regression_mnist.html
        training_date = execution_context.job_execution_info.workflow_execution.context
        af_client = _get_ai_flow_client_with_retry(5)

        x_train, y_train = input_list[0][0], input_list[0][1]
        clf = self._init_model(af_client, training_date)
        clf.fit(x_train, y_train)

        model_path = self._dump_model(clf, training_date)
        self._register_model_and_model_version(af_client, execution_context, model_path, training_date)

        return [[None]]

    @staticmethod
    def _register_model_and_model_version(af_client, execution_context, model_path, training_date):
        project_meta = \
            af_client.get_project_by_name(
                execution_context.job_execution_info.workflow_execution.workflow_info.namespace)
        print("project id of {} is {}".format(project_meta.name, project_meta.uuid))
        model_name = 'mnist_daily_model_{}'.format(training_date)
        model_meta = af_client.get_model_by_name(model_name)
        if not model_meta:
            model_meta = af_client.register_model(model_name, project_meta.uuid)
        af.register_model_version(model=model_meta, model_path=model_path)

    @staticmethod
    def _dump_model(model, training_date):
        model_path = '/tmp/daily_mnist_model'
        if not os.path.exists(model_path):
            os.makedirs(model_path)
        model_path = model_path + '/' + training_date
        dump(model, model_path)
        return model_path

    def _init_model(self, af_client, training_date):
        today_model_name = 'mnist_daily_model_{}'.format(training_date)
        base_model_version = self._get_model_version_meta(af_client, today_model_name)

        if not base_model_version:
            print("training first model of date:{}, using yesterday model version as base".format(training_date))
            yesterday = date.fromisoformat(training_date) - timedelta(days=1)
            yesterday_model_name = 'mnist_daily_model_{}'.format(yesterday.isoformat())
            base_model_version = self._get_model_version_meta(af_client, yesterday_model_name)

        if base_model_version:
            try:
                clf = load(base_model_version.model_path)
            except Exception as _:
                clf = LogisticRegression(C=50. / 5000, penalty='l1', solver='saga', tol=0.1)
        else:
            print("yesterday's model not exist, init a new model")
            clf = LogisticRegression(C=50. / 5000, penalty='l1', solver='saga', tol=0.1)
        return clf

    @staticmethod
    def _get_model_version_meta(af_client, model_name) -> af.ModelVersionMeta:
        print("Getting deployed model version of {}".format(model_name))
        model_version = af_client.get_deployed_model_version(model_name)
        if not model_version:
            print("Getting validated model version of {}".format(model_name))
            model_version = af_client.get_latest_validated_model_version(model_name)
        if not model_version:
            print("Getting generated model version of {}".format(model_name))
            model_version = af_client.get_latest_generated_model_version(model_name)
        return model_version


class DailyValidateReader(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        dataset_meta: af.DatasetMeta = execution_context.config.get('dataset')
        with np.load(dataset_meta.uri) as f:
            x_test, y_test = f['x_test'], f['y_test']
        return [[x_test, y_test]]


class DailyValidateTransformer(PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        x_test, y_test = input_list[0][0], input_list[0][1]
        x_test = x_test.reshape((x_test.shape[0], -1))
        return [[StandardScaler().fit_transform(x_test), y_test]]


class DailyValidate(PythonProcessor):
    def __init__(self):
        super().__init__()
        self.model_name = None
        self.model_path = None
        self.model_version = None

    def open(self, execution_context: ExecutionContext):
        training_date = execution_context.job_execution_info.workflow_execution.context
        model_name = 'mnist_daily_model_{}'.format(training_date)
        af_client = _get_ai_flow_client_with_retry(5)
        self.model_name = model_name
        model = af_client.get_latest_generated_model_version(self.model_name)
        self.model_path = model.model_path
        self.model_version = model.version

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        x_validate, y_validate = input_list[0][0], input_list[0][1]
        clf = load(self.model_path)

        af_client = _get_ai_flow_client_with_retry(5)
        latest_version = self._get_latest_validated_model_version(af_client, self.model_name)
        latest_version_score = 0.0
        if latest_version:
            latest_version_model = load(latest_version.model_path)
            latest_version_score = np.mean(cross_val_score(latest_version_model, x_validate, y_validate,
                                                           scoring='precision_macro', cv=5))
            print('latest model version[{}] scores: {}'.format(latest_version.version, latest_version_score))
        score = np.mean(cross_val_score(clf, x_validate, y_validate, scoring='precision_macro', cv=5))
        af.update_model_version(model_name=self.model_name,
                                model_version=self.model_version,
                                version_desc="score: {}".format(score))
        print('generated model version[{}] scores: {}'.format(self.model_version, score))
        if score > latest_version_score:
            af.update_model_version(model_name=self.model_name,
                                    model_version=self.model_version,
                                    current_stage=af.ModelVersionStage.VALIDATED)

        return [[None]]

    @staticmethod
    def _get_latest_validated_model_version(af_client, model_name) -> af.ModelVersionMeta:
        print("Getting deployed model version of {}".format(model_name))
        model_version = af_client.get_deployed_model_version(model_name)
        if not model_version:
            print("Getting validated model version of {}".format(model_name))
            model_version = af_client.get_latest_validated_model_version(model_name)
        return model_version


def main():
    af.init_ai_flow_context()
    with af.job_config('daily_training'):
        daily_data_meta = af.get_dataset_by_name('daily_data')
        assert daily_data_meta is not None
        conn = af.read_dataset(daily_data_meta, DailyTrainingReader())
        af.train(conn, training_processor=DailyTrainingTrain(), model_info=None)
    with af.job_config('daily_validate'):
        mnist_evaluate_data_meta = af.get_dataset_by_name('mnist_evaluate')
        assert mnist_evaluate_data_meta is not None
        conn = af.read_dataset(mnist_evaluate_data_meta, read_dataset_processor=DailyValidateReader())
        conn = af.transform(conn, transform_processor=DailyValidateTransformer())
        af.user_define_operation(conn, processor=DailyValidate())

    af.action_on_job_status('daily_validate', 'daily_training')

    af.set_context_extractor(DailyWorkflowContextExtractor())

    project_name = af.current_project_config().get_project_name()
    workflow_name = af.current_workflow_config().workflow_name
    af.workflow_operation.submit_workflow(workflow_name)

    condition = MeetAllEventCondition()
    condition.add_event(namespace=project_name, event_type='DATA_EVENT',
                        event_key='daily_data', event_value='ready', sender=ANY_CONDITION)
    af.workflow_operation.start_new_workflow_execution_on_events(workflow_name, event_conditions=[condition])


if __name__ == '__main__':
    main()
