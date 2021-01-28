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
import time
import unittest
import sqlalchemy
from typing import List
from sqlalchemy.ext.declarative import declarative_base

from notification_service.base_notification import BaseEvent, EventWatcher
from notification_service.client import NotificationClient
from notification_service.event_storage import DbEventStorage
from notification_service.high_availability import SimpleNotificationServerHaManager, DbHighAvailabilityStorage
from notification_service.master import NotificationMaster
from notification_service.service import HighAvailableNotificationService


_SQLITE_DB_FILE = 'notification_service.db'
_SQLITE_DB_URI = '%s%s' % ('sqlite:///', _SQLITE_DB_FILE)


class HaServerTest(unittest.TestCase):

    @classmethod
    def start_master(cls, host, port):
        port = str(port)
        server_uri = host + ":" + port
        storage = DbEventStorage()
        ha_manager = SimpleNotificationServerHaManager()
        ha_storage = DbHighAvailabilityStorage(db_conn=_SQLITE_DB_URI)
        service = HighAvailableNotificationService(
            storage,
            ha_manager,
            server_uri,
            ha_storage,
            5000)
        master = NotificationMaster(service, port=int(port))
        master.run()
        return master

    @classmethod
    def wait_for_master_started(cls, server_uri="localhost:50051"):
        last_exception = None
        for i in range(100):
            try:
                return NotificationClient(server_uri="localhost:50051", enable_ha=True)
            except Exception as e:
                time.sleep(10)
                last_exception = e
        raise Exception("The server %s is unavailable." % server_uri) from last_exception

    @classmethod
    def setUpClass(cls):
        cls.storage = DbEventStorage()
        cls.master1 = None
        cls.master2 = None
        cls.master3 = None

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(_SQLITE_DB_FILE)

    def setUp(self):
        self.storage.clean_up()
        self.master1 = self.start_master("localhost", "50051")
        self.client = self.wait_for_master_started("localhost:50051")

    def tearDown(self):
        self.client.stop_listen_events()
        self.client.stop_listen_event()
        self.client.disable_high_availability()
        if self.master1 is not None:
            self.master1.stop()
        if self.master2 is not None:
            self.master2.stop()
        if self.master3 is not None:
            self.master3.stop()
        db_engine = sqlalchemy.create_engine(_SQLITE_DB_URI, pool_pre_ping=True)
        declarative_base().metadata.drop_all(db_engine)

    def wait_for_new_members_detected(self, new_member_uri):
        for i in range(100):
            living_member = self.client.living_members
            if new_member_uri in living_member:
                break
            else:
                time.sleep(10)

    def test_server_change(self):
        self.client.send_event(BaseEvent(key="key", value="value1"))
        self.client.send_event(BaseEvent(key="key", value="value2"))
        self.client.send_event(BaseEvent(key="key", value="value3"))
        results = self.client.list_all_events()
        self.assertEqual(self.client.current_uri, "localhost:50051")
        self.master2 = self.start_master("localhost", "50052")
        self.wait_for_new_members_detected("localhost:50052")
        self.master1.stop()
        results2 = self.client.list_all_events()
        self.assertEqual(results, results2)
        self.assertEqual(self.client.current_uri, "localhost:50052")
        self.master3 = self.start_master("localhost", "50053")
        self.wait_for_new_members_detected("localhost:50053")
        self.master2.stop()
        results3 = self.client.list_all_events()
        self.assertEqual(results2, results3)
        self.assertEqual(self.client.current_uri, "localhost:50053")

    def test_send_listening_on_different_server(self):
        event_list = []

        class TestWatch(EventWatcher):
            def __init__(self, event_list) -> None:
                super().__init__()
                self.event_list = event_list

            def process(self, events: List[BaseEvent]):
                self.event_list.extend(events)

        self.master2 = self.start_master("localhost", "50052")
        self.wait_for_new_members_detected("localhost:50052")
        another_client = NotificationClient(server_uri="localhost:50052")
        try:
            event1 = another_client.send_event(BaseEvent(key="key1", value="value1"))
            self.client.start_listen_events(watcher=TestWatch(event_list), version=event1.version)
            another_client.send_event(BaseEvent(key="key2", value="value2"))
            another_client.send_event(BaseEvent(key="key3", value="value3"))
        finally:
            self.client.stop_listen_events()
        self.assertEqual(2, len(event_list))

    def test_start_with_multiple_servers(self):
        self.client.disable_high_availability()
        self.client = NotificationClient(server_uri="localhost:55001,localhost:50051", enable_ha=True)
        self.assertTrue(self.client.current_uri, "localhost:50051")
