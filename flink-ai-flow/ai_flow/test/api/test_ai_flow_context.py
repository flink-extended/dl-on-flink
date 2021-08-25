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
from ai_flow.store.db.base_model import base
from ai_flow.test.store.test_sqlalchemy_store import _get_store
from ai_flow.endpoint.server.server import AIFlowServer
import ai_flow as af

_SQLITE_DB_FILE = 'aiflow.db'
_SQLITE_DB_URI = '%s%s' % ('sqlite:///', _SQLITE_DB_FILE)
_PORT = '50051'


class TestAIFlowContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print("TestAIFlowContext setUpClass")
        if os.path.exists(_SQLITE_DB_FILE):
            os.remove(_SQLITE_DB_FILE)
        cls.server = AIFlowServer(store_uri=_SQLITE_DB_URI, port=_PORT, start_scheduler_service=False)
        cls.server.run()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.stop()
        os.remove(_SQLITE_DB_FILE)

    def setUp(self) -> None:
        _get_store(_SQLITE_DB_URI)

    def tearDown(self) -> None:
        store = _get_store(_SQLITE_DB_URI)
        base.metadata.drop_all(store.db_engine)

    def test_init_ai_client(self):
        af.init_ai_flow_client(server_uri='localhost:50051', project_name='test')
        project_meta = af.get_project_by_name('test')
        self.assertEqual('test', project_meta.name)

    def test_init_ai_client_no_project_name(self):
        af.init_ai_flow_client(server_uri='localhost:50051', project_name=None)
        project_meta = af.get_project_by_name('Unknown')
        self.assertEqual('Unknown', project_meta.name)

    def test_init_ai_client_register_dataset(self):
        af.init_ai_flow_client(server_uri='localhost:50051', project_name=None)
        af.register_dataset(name='test_dataset', uri='/test')
        dataset_meta = af.get_dataset_by_name('test_dataset')
        self.assertEqual('/test', dataset_meta.uri)


if __name__ == '__main__':
    unittest.main()
