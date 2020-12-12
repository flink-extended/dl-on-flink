# -*- coding: utf-8 -*-
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

from typing import List

from notification_service.service import NotificationService

from airflow.notification.event_model_storage import EventModelStorage
from tests.test_utils.db import clear_db_event_model
import unittest
from airflow.models.event import Event
from notification_service.master import NotificationMaster
from notification_service.client import NotificationClient, EventWatcher


class NotificationTest(unittest.TestCase):
    def setUp(self):
        clear_db_event_model()

    @classmethod
    def setUpClass(cls):
        cls.master = NotificationMaster(NotificationService(EventModelStorage()))
        cls.master.run()
        cls.client = NotificationClient(server_uri="localhost:50051")

    @classmethod
    def tearDownClass(cls):
        cls.master.stop()

    def test_send_event(self):
        event = self.client.send_event(Event(key="key", value="value1"))
        self.assertEqual(1, event.version)

    def test_list_events(self):
        event = self.client.send_event(Event(key="key", value="value1"))
        event = self.client.send_event(Event(key="key", value="value2"))
        event = self.client.send_event(Event(key="key", value="value3"))
        events = self.client.list_events("key", version=1)
        self.assertEqual(2, len(events))

    def test_listen_events(self):
        event_list = []

        class TestWatch(EventWatcher):
            def __init__(self, event_list) -> None:
                super().__init__()
                self.event_list = event_list

            def process(self, events: List[Event]):
                self.event_list.extend(events)

        event = self.client.send_event(Event(key="key", value="value1"))
        self.client.start_listen_event(key="key", watcher=TestWatch(event_list), version=1)
        event = self.client.send_event(Event(key="key", value="value2"))
        event = self.client.send_event(Event(key="key", value="value3"))
        self.client.stop_listen_event("key")
        events = self.client.list_events("key", version=1)
        self.assertEqual(2, len(events))
        self.assertEqual(2, len(event_list))

    def test_all_listen_events(self):
        event = self.client.send_event(Event(key="key", value="value1"))
        event = self.client.send_event(Event(key="key", value="value2"))
        start_time = event.create_time
        event = self.client.send_event(Event(key="key", value="value3"))
        events = self.client.list_all_events(start_time)
        self.assertEqual(2, len(events))

    def test_listen_all_events(self):
        event_list = []

        class TestWatch(EventWatcher):
            def __init__(self, event_list) -> None:
                super().__init__()
                self.event_list = event_list

            def process(self, events: List[Event]):
                self.event_list.extend(events)
        try:
            self.client.start_listen_events(watcher=TestWatch(event_list))
            event = self.client.send_event(Event(key="key1", value="value1"))
            event = self.client.send_event(Event(key="key2", value="value2"))
            event = self.client.send_event(Event(key="key3", value="value3"))
        finally:
            self.client.stop_listen_events()
        self.assertEqual(3, len(event_list))


