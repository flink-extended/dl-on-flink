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
from __future__ import print_function

import json
import os
import pickle
import tempfile
import unittest
from collections import namedtuple

import numpy
import sklearn.datasets as datasets
import sklearn.neighbors as knn
from notification_service.base_notification import EventWatcher

from ai_flow.model_center.model import sklearn
from ai_flow.client.ai_flow_client import AIFlowClient
from ai_flow.endpoint.server.server import AIFlowServer

ModelWithData = namedtuple('ModelWithData', ['model', 'inference_data'])

SERIALIZATION_FORMAT_PICKLE = 'pickle'

_SQLITE_DB_FILE = 'aiflow.db'
_SQLITE_DB_URI = '%s%s' % ('sqlite:///', _SQLITE_DB_FILE)
_PORT = '50051'


def fit_model():
    iris = datasets.load_iris()
    X = iris.data[:, :2]
    y = iris.target
    knn_model = knn.KNeighborsClassifier()
    knn_model.fit(X, y)
    return ModelWithData(model=knn_model, inference_data=X)


def save_model(sk_model, output_path, serialization_format):
    with open(output_path, 'wb') as out:
        if serialization_format == SERIALIZATION_FORMAT_PICKLE:
            pickle.dump(sk_model, out)


class TestSklearnModel(unittest.TestCase):

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
        knn_model = fit_model()
        model_path = tempfile.mkdtemp()
        if not os.path.exists(model_path):
            os.makedirs(model_path)
        model_path = os.path.join(model_path, 'model.pkl')
        save_model(sk_model=knn_model.model, output_path=model_path, serialization_format=SERIALIZATION_FORMAT_PICKLE)
        registered_model = self.client.create_registered_model(model_name='knn_model',
                                                               model_desc='knn model')
        self.client.create_model_version(model_name=registered_model.model_name, model_path=model_path,
                                         model_type='sklearn', version_desc='knn model')

        class KnnWatcher(EventWatcher):

            def process(self, notifications):
                for notification in notifications:
                    load_path = json.loads(notification.value).get('_model_path')
                    reloaded_knn_model = sklearn.load_model(model_uri=load_path)
                    numpy.testing.assert_array_equal(
                        knn_model.model.predict(knn_model.inference_data),
                        reloaded_knn_model.predict(knn_model.inference_data))
                    os.remove(load_path)

        self.client.start_listen_event(key=registered_model.model_name, watcher=KnnWatcher())
