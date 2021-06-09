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
import unittest

import sqlalchemy

from ai_flow.endpoint.client.aiflow_client import AIFlowClient
from ai_flow.endpoint.server.server import AIFlowServer
from ai_flow.store.db.base_model import base
from ai_flow.test.endpoint import test_client
from ai_flow.test.store.test_sqlalchemy_store import _get_store
from ai_flow.test.test_util import get_mysql_server_url

_PORT = '50051'


@unittest.skip("To run this test you need to configure the mysql info in 'ai_flow/test/test_util.py'")
class TestAIFlowClientMySQL(test_client.TestAIFlowClientSqlite):

    @classmethod
    def setUpClass(cls) -> None:
        print("TestAIFlowClientMySQL setUpClass")
        db_server_url = get_mysql_server_url()
        cls.db_name = 'test_aiflow_client'
        cls.engine = sqlalchemy.create_engine(db_server_url)
        cls.engine.execute('DROP DATABASE IF EXISTS %s' % cls.db_name)
        cls.engine.execute('CREATE DATABASE IF NOT EXISTS %s' % cls.db_name)
        cls.store_uri = '%s/%s' % (db_server_url, cls.db_name)
        cls.server = AIFlowServer(store_uri=cls.store_uri, port=_PORT)
        cls.server.run()
        test_client.client = AIFlowClient(server_uri='localhost:' + _PORT)
        test_client.client1 = AIFlowClient(server_uri='localhost:' + _PORT)
        test_client.client2 = AIFlowClient(server_uri='localhost:' + _PORT)

    @classmethod
    def tearDownClass(cls) -> None:
        test_client.client.stop_listen_event()
        test_client.client1.stop_listen_event()
        test_client.client2.stop_listen_event()
        cls.server.stop()

    def setUp(self) -> None:
        _get_store(self.store_uri)

    def tearDown(self) -> None:
        store = _get_store(self.store_uri)
        base.metadata.drop_all(store.db_engine)


if __name__ == '__main__':
    unittest.main()
