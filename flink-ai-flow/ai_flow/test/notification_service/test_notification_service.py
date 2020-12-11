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
import asyncio
import os
import unittest
from abc import ABCMeta

import sqlalchemy

from ai_flow.notification.service.service import NotificationService
from notification_service.proto.notification_service_pb2 import EventProto, ListEventsRequest, SendEventRequest
from ai_flow.store.db.base_model import base
from ai_flow.test.store.test_sqlalchemy_store import _get_store
from ai_flow.test.test_util import get_mysql_server_url

_SQLITE_DB_FILE = 'aiflow.db'
_SQLITE_DB_URI = '%s%s' % ('sqlite:///', _SQLITE_DB_FILE)


class TestNotificationServiceSqlite(unittest.TestCase):
    __metaclass__ = ABCMeta

    @classmethod
    def setUpClass(cls) -> None:
        if os.path.exists(_SQLITE_DB_FILE):
            os.remove(_SQLITE_DB_FILE)
        cls.notification_service = NotificationService(backend_store_uri=_SQLITE_DB_URI)

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(_SQLITE_DB_FILE)

    def setUp(self):
        self.store = _get_store(_SQLITE_DB_URI)

    def tearDown(self):
        base.metadata.drop_all(self.store.db_engine)

    async def _send_event(self, k, v, s):
        await asyncio.sleep(s)
        send_event_req = SendEventRequest(
            event=EventProto(key=k, value=v))
        await self.notification_service.sendEvent(send_event_req, None)

    async def _list_events(self, k, v, timeout):
        list_events_req = ListEventsRequest(
            event=EventProto(key=k, version=v),
            timeout_seconds=timeout)
        return await self.notification_service.listEvents(list_events_req, None)

    async def _gather_coroutine(self, k, v, version, timeout, sleep):
        return await asyncio.gather(self._list_events(k, version, timeout),
                                    self._send_event(k, v, sleep),
                                    self._send_event(k, v, sleep + 1),
                                    self._send_event(k, v, sleep + 2))

    def testnotification_service(self):
        result = asyncio.get_event_loop().run_until_complete(
            self._gather_coroutine('test_ns_key', 'test_ns_value', 2, 5, 1))
        events = result[0].events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].version, 3)

    def testnotification_service_with_timeout_waiting(self):
        result = asyncio.get_event_loop().run_until_complete(
            self._gather_coroutine('test_ns_wait_key', 'test_ns_wait_value', 0, 3, 3))
        events = result[0].events
        self.assertEqual(len(events), 0)


@unittest.skip("To run this test you need to configure the mysql info in 'ai_flow/test/test_util.py'")
class TestNotificationServiceMySQL(TestNotificationServiceSqlite):

    @classmethod
    def setUpClass(cls) -> None:
        db_server_url = get_mysql_server_url()
        cls.db_name = 'test_aiflow_store'
        cls.engine = sqlalchemy.create_engine(db_server_url)
        cls.engine.execute('CREATE DATABASE IF NOT EXISTS %s' % cls.db_name)
        cls.store_uri = '%s/%s' % (db_server_url, cls.db_name)
        cls.notification_service = NotificationService(backend_store_uri=cls.store_uri)

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
