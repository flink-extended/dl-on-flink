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
import pytest
import unittest
from typing import List
from notification_service.base_notification import BaseEvent, EventWatcher
from notification_service.client import NotificationClient
from notification_service.mongo_event_storage import MongoEventStorage
from notification_service.master import NotificationMaster
from notification_service.service import NotificationService


@unittest.skip("To run this test you need to setup a local mongodb")
@pytest.mark.release
class MongoNotificationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        kwargs = {
            "host": "127.0.0.1",
            "port": 27017,
            "db": "test"
        }
        cls.storage = MongoEventStorage(**kwargs)
        cls.master = NotificationMaster(NotificationService(cls.storage))
        cls.master.run()
        cls.client = NotificationClient(server_uri="localhost:50051")

    @classmethod
    def tearDownClass(cls):
        cls.master.stop()
        MongoNotificationTest.storage.clean_up()  # will clean up mongodb!!!

    def setUp(self):
        MongoNotificationTest.storage.clean_up()  # will clean up mongodb!!!

    def test_send_event(self):
        event = self.client.send_event(BaseEvent(key="key", value="value1"))
        latest_version = self.storage.get_latest_version(key="key")
        self.assertEqual(event.version, latest_version)

    def test_list_events(self):
        event = self.client.send_event(BaseEvent(key="key", value="value1"))
        first_version = event.version
        print("######first version: {}".format(first_version))
        event = self.client.send_event(BaseEvent(key="key", value="value2"))
        event = self.client.send_event(BaseEvent(key="key", value="value3"))
        events = self.client.list_events("key", version=first_version)
        self.assertEqual(2, len(events))
        events = self.client.list_events("key")
        self.assertEqual(3, len(events))

    def test_listen_events(self):
        event_list = []

        class TestWatch(EventWatcher):
            def __init__(self, event_list) -> None:
                super().__init__()
                self.event_list = event_list

            def process(self, events: List[BaseEvent]):
                self.event_list.extend(events)

        event = self.client.send_event(BaseEvent(key="key", value="value1"))
        first_version = event.version
        self.client.start_listen_event(key="key", watcher=TestWatch(event_list), version=event.version)
        event = self.client.send_event(BaseEvent(key="key", value="value2"))
        event = self.client.send_event(BaseEvent(key="key", value="value3"))
        self.client.stop_listen_event("key")
        events = self.client.list_events("key", version=first_version)
        self.assertEqual(2, len(events))
        self.assertEqual(2, len(event_list))

    def test_all_listen_events(self):
        event = self.client.send_event(BaseEvent(key="key", value="value1"))
        event = self.client.send_event(BaseEvent(key="key", value="value2"))
        start_time = event.create_time
        print("#####start time: {}".format(start_time))
        event = self.client.send_event(BaseEvent(key="key", value="value3"))
        events = self.client.list_all_events(start_time)
        self.assertEqual(2, len(events))

    def test_listen_all_events(self):
        event_list = []

        class TestWatch(EventWatcher):
            def __init__(self, event_list) -> None:
                super().__init__()
                self.event_list = event_list

            def process(self, events: List[BaseEvent]):
                self.event_list.extend(events)
        try:
            self.client.start_listen_events(watcher=TestWatch(event_list))
            self.client.send_event(BaseEvent(key="key1", value="value1"))
            self.client.send_event(BaseEvent(key="key2", value="value2"))
            self.client.send_event(BaseEvent(key="key3", value="value3"))
        finally:
            self.client.stop_listen_events()
        self.assertEqual(3, len(event_list))

    def test_get_latest_version(self):
        self.client.send_event(BaseEvent(key="key", value="value1"))
        self.client.send_event(BaseEvent(key="key", value="value2"))
        latest_version = self.client.get_latest_version(key="key")
        print("#####latest version of key: {}".format(latest_version))

    def test_register_client(self):
        self.assertIsNotNone(self.client.id)
        tmp_client = NotificationClient(server_uri="localhost:50051")
        self.assertEqual(1, tmp_client.id - self.client.id)