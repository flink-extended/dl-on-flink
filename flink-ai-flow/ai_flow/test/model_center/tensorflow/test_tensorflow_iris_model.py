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
import collections
import copy
import json
import os
import sys
import tempfile
import unittest

import numpy as np
import pandas
import pandas as pd
import tensorflow as tf
from notification_service.base_notification import EventWatcher
from tensorflow.python.saved_model import tag_constants

from ai_flow import ModelType
from ai_flow.model_center.model import tensorflow
from ai_flow.endpoint.client.aiflow_client import AIFlowClient
from ai_flow.endpoint.server.server import AIFlowServer
from ai_flow.test.model_center.tensorflow import iris_data_utils

SavedModelInfo = collections.namedtuple(
    'SavedModelInfo',
    ['path', 'meta_graph_tags', 'signature_def_map_key', 'inference_df', 'expected_results_df', 'raw_results',
     'raw_df'])

_SQLITE_DB_FILE = 'aiflow.db'
_SQLITE_DB_URI = '%s%s' % ('sqlite:///', _SQLITE_DB_FILE)
_PORT = '50051'


def fit_and_save_model():
    (train_x, train_y), (test_x, test_y) = iris_data_utils.load_data()
    # Feature columns describe how to use the input.
    my_feature_columns = []
    for key in train_x.keys():
        my_feature_columns.append(tf.feature_column.numeric_column(key=key))
    # Build 2 hidden layer DNN with 10, 10 units respectively.
    estimator = tf.estimator.DNNClassifier(
        feature_columns=my_feature_columns,
        # Two hidden layers of 10 ai_nodes each.
        hidden_units=[10, 10],
        # The model must choose between 3 classes.
        n_classes=3)
    # Train the Model.
    batch_size = 100
    train_steps = 1000
    estimator.train(
        input_fn=lambda: iris_data_utils.train_input_fn(train_x, train_y, batch_size),
        steps=train_steps)
    # Generate predictions from the model
    predict_x = {
        'SepalLength': [5.1, 5.9, 6.9],
        'SepalWidth': [3.3, 3.0, 3.1],
        'PetalLength': [1.7, 4.2, 5.4],
        'PetalWidth': [0.5, 1.5, 2.1],
    }
    estimator_preds = estimator.predict(lambda: iris_data_utils.eval_input_fn(predict_x, None,
                                                                              batch_size))
    # Building a dictionary of the predictions by the estimator.
    if sys.version_info < (3, 0):
        estimator_preds_dict = estimator_preds.next()
    else:
        estimator_preds_dict = next(estimator_preds)
    for row in estimator_preds:
        for key in row.keys():
            estimator_preds_dict[key] = np.vstack((estimator_preds_dict[key], row[key]))
    # Building a pandas DataFrame out of the prediction dictionary.
    estimator_preds_df = copy.deepcopy(estimator_preds_dict)
    for col in estimator_preds_df.keys():
        if all(len(element) == 1 for element in estimator_preds_df[col]):
            estimator_preds_df[col] = estimator_preds_df[col].ravel()
        else:
            estimator_preds_df[col] = estimator_preds_df[col].tolist()
    # Building a DataFrame that contains the names of the flowers predicted.
    estimator_preds_df = pandas.DataFrame.from_dict(data=estimator_preds_df)
    estimator_preds_results = [iris_data_utils.SPECIES[id[0]]
                               for id in estimator_preds_dict['class_ids']]
    estimator_preds_results_df = pd.DataFrame({'predictions': estimator_preds_results})
    # Define a function for estimator inference
    feature_spec = {}
    for name in my_feature_columns:
        feature_spec[name.key] = tf.Variable([], dtype=tf.float64, name=name.key)
    receiver_fn = tf.estimator.export.build_raw_serving_input_receiver_fn(feature_spec)
    # Save the estimator and its inference function
    model_path = os.path.join(tempfile.mkdtemp(), 'saved_model')
    saved_estimator_path = estimator.export_saved_model(model_path,
                                                        receiver_fn).decode('utf-8')

    return SavedModelInfo(path=saved_estimator_path,
                          meta_graph_tags=[tag_constants.SERVING],
                          signature_def_map_key='predict',
                          inference_df=pd.DataFrame(data=predict_x,
                                                    columns=[name.key for name in
                                                             my_feature_columns]),
                          expected_results_df=estimator_preds_results_df,
                          raw_results=estimator_preds_dict,
                          raw_df=estimator_preds_df)


class TestTensorFlowIrisModel(unittest.TestCase):

    def setUp(self) -> None:
        if os.path.exists(_SQLITE_DB_FILE):
            os.remove(_SQLITE_DB_FILE)
        self.server = AIFlowServer(store_uri=_SQLITE_DB_URI, port=_PORT)
        self.server.run()
        self.client = AIFlowClient(server_uri='localhost:' + _PORT)

    def tearDown(self) -> None:
        self.client.stop_listen_event()
        self.server.stop()
        os.remove(_SQLITE_DB_FILE)

    def test_save_and_load_model(self):
        iris_model = fit_and_save_model()
        tf_graph = tf.Graph()
        registered_model = self.client.create_registered_model(model_name='iris_model',
                                                               model_type=ModelType.SAVED_MODEL,
                                                               model_desc='iris model')
        self.client.create_model_version(model_name=registered_model.model_name, model_path=iris_model.path,
                                         model_metric='http://metric',
                                         model_flavor='{"meta_graph_tags":["serve"],"signature_def_map_key":"predict"}',
                                         version_desc='iris model')

        class IrisWatcher(EventWatcher):

            def process(self, notifications):
                for notification in notifications:
                    model_path = json.loads(notification.value).get('_model_path')
                    model_flavor = json.loads(notification.value).get('_model_flavor')
                    signature_def = tensorflow.load_model(model_uri=model_path,
                                                          meta_graph_tags=json.loads(model_flavor).get(
                                                              'meta_graph_tags'),
                                                          signature_def_map_key=json.loads(model_flavor).get(
                                                              'signature_def_map_key'),
                                                          tf_session=tf.Session(graph=tf_graph))
                    for _, input_signature in signature_def.inputs.items():
                        t_input = tf_graph.get_tensor_by_name(input_signature.name)
                        assert t_input is not None
                    for _, output_signature in signature_def.outputs.items():
                        t_output = tf_graph.get_tensor_by_name(output_signature.name)
                        assert t_output is not None

        self.client.start_listen_event(key=registered_model.model_name,
                                              watcher=IrisWatcher())


if __name__ == '__main__':
    unittest.main()
