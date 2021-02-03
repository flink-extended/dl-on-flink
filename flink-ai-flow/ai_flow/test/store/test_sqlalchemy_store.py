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
from ai_flow.store.sqlalchemy_store import SqlAlchemyStore
from ai_flow.test.test_util import get_mysql_server_url
from ai_flow.test.store.common import AbstractTestStore

_SQLITE_DB_FILE = 'ai_flow.db'
_SQLITE_DB_URI = '%s%s' % ('sqlite:///', _SQLITE_DB_FILE)


def _get_store(db_uri=''):
    return SqlAlchemyStore(db_uri)


class TestSqlAlchemyStoreSqlite(AbstractTestStore, unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        if os.path.exists(_SQLITE_DB_FILE):
            os.remove(_SQLITE_DB_FILE)

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(_SQLITE_DB_FILE)

    def setUp(self):
        self.store = _get_store(_SQLITE_DB_URI)

    def tearDown(self):
        base.metadata.drop_all(self.store.db_engine)


@unittest.skip("To run this test you need to configure the mysql info in 'ai_flow/test/test_util.py'")
@pytest.mark.release
class TestSqlAlchemyStoreMySQL(AbstractTestStore, unittest.TestCase):
    """
    Run tests against a MySQL database. Run the test command with the environment variables set,
    e.g: MYSQL_TEST_USERNAME=your_username MYSQL_TEST_PASSWORD=your_password <your-test-command>.
    You may optionally specify MySQL host via MYSQL_TEST_HOST (default is 100.69.96.145)
    and specify MySQL port via MYSQL_TEST_PORT (default is 3306).
    """

    @classmethod
    def setUpClass(cls) -> None:
        db_server_url = get_mysql_server_url()
        cls.db_name = 'test_aiflow_store'
        cls.engine = sqlalchemy.create_engine(db_server_url)
        cls.engine.execute('CREATE DATABASE IF NOT EXISTS %s' % cls.db_name)
        cls.store_uri = '%s/%s' % (db_server_url, cls.db_name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.engine.execute('DROP DATABASE IF EXISTS %s' % cls.db_name)

    def setUp(self) -> None:
        self.store = _get_store(self.store_uri)

    def tearDown(self) -> None:
        store = _get_store(self.store_uri)
        base.metadata.drop_all(store.db_engine)


if __name__ == '__main__':
    unittest.main()
