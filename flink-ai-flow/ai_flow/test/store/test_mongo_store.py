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
import unittest
from unittest import mock

import pytest
import sqlalchemy

from ai_flow.store.db.base_model import base
from ai_flow.store.mongo_store import MongoStore, MongoStoreConnManager
from ai_flow.store.db.db_util import parse_mongo_uri
from ai_flow.endpoint.server.exception import AIFlowException
from ai_flow.test.test_util import get_mongodb_server_url
from ai_flow.test.store.common import AbstractTestStore


def _get_store(db_uri=''):
    try:
        username, password, host, port, db = parse_mongo_uri(db_uri)
        return MongoStore(host=host,
                          port=int(port),
                          username=username,
                          password=password,
                          db=db)
    except Exception as e:
        raise AIFlowException(str(e))


@unittest.skip("To run this test you need to configure the mongodb info in 'ai_flow/test/test_util.py'")
@pytest.mark.release
class TestMongoDB(AbstractTestStore, unittest.TestCase):
    """
    Run tests against a MongoDB database. Run the test command with the environment variables set,
    e.g: MONGODB_TEST_USERNAME=your_username MONGODB_TEST_PASSWORD=your_password <your-test-command>.
    You may optionally specify MONGODB host via MONGODB_TEST_HOST and specify MONGODB port via 
    MONGODB_TEST_PORT.
    """

    @classmethod
    def setUpClass(cls) -> None:
        db_server_url = get_mongodb_server_url()
        cls.db_name = 'test_aiflow_store'
        cls.store_uri = '%s/%s' % (db_server_url, cls.db_name)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Run once for the whole class when all set
        """
        MongoStoreConnManager().disconnect(cls.store_uri)

    def setUp(self) -> None:
        """
        Each time will try to set up connection, just ingore if already have one
        """
        self.store = _get_store(self.store_uri)

    def tearDown(self) -> None:
        """
        Each time will clear the db before test takes off
        """
        MongoStoreConnManager().drop(self.store_uri)


if __name__ == '__main__':
    unittest.main()
