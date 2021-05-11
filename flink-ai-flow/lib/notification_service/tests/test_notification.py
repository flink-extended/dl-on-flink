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
import time
from typing import List
import unittest
from notification_service.base_notification import BaseEvent, EventWatcher
from notification_service.client import NotificationClient
from notification_service.event_storage import MemoryEventStorage, DbEventStorage
from notification_service.high_availability import SimpleNotificationServerHaManager, DbHighAvailabilityStorage
from notification_service.master import NotificationMaster
from notification_service.service import NotificationService, HighAvailableNotificationService


def start_ha_master(host, port):
    server_uri = host + ":" + str(port)
    storage = DbEventStorage()
    ha_manager = SimpleNotificationServerHaManager()
    ha_storage = DbHighAvailabilityStorage()
    service = HighAvailableNotificationService(
        storage,
        ha_manager,
        server_uri,
        ha_storage)
    master = NotificationMaster(service, port=port)
    master.run()
    return master


class NotificationTest(object):

    def test_send_event(self):
        event = self.client.send_event(BaseEvent(key="key", value="value1"))
        self.assertTrue(event.version >= 1)

    def test_list_events(self):
        self.client._default_namespace = "a"
        self.client._sender = 's'
        event1 = self.client.send_event(BaseEvent(key="key", value="value1"))

        self.client._default_namespace = "b"
        self.client.send_event(BaseEvent(key="key", value="value2", event_type="a"))
        self.client.send_event(BaseEvent(key="key", value="value3"))
        self.client.send_event(BaseEvent(key="key2", value="value3"))

        events = self.client.list_events(["key", "key2"], version=event1.version)
        self.assertEqual(3, len(events))
        self.assertEqual('s', events[0].sender)

        self.client._default_namespace = "a"
        events = self.client.list_events("key")
        self.assertEqual(1, len(events))

        self.client._default_namespace = "b"
        events = self.client.list_events("key")
        self.assertEqual(2, len(events))

        events = self.client.list_events("key", event_type="a")
        self.assertEqual(1, len(events))

        events = self.client.list_events("key", sender='s')
        self.assertEqual(2, len(events))

        events = self.client.list_events("key", sender='p')
        self.assertEqual(0, len(events))

    def test_listen_events(self):
        event_list = []

        class TestWatch(EventWatcher):
            def __init__(self, event_list) -> None:
                super().__init__()
                self.event_list = event_list

            def process(self, events: List[BaseEvent]):
                self.event_list.extend(events)

        self.client._default_namespace = "a"
        self.client._sender = "s"
        event1 = self.client.send_event(BaseEvent(key="key", value="value1"))
        h = self.client.start_listen_event(key="key",
                                           watcher=TestWatch(event_list),
                                           version=event1.version)
        self.client.send_event(BaseEvent(key="key", value="value2"))
        self.client.send_event(BaseEvent(key="key", value="value3"))

        self.client._default_namespace = None
        self.client.send_event(BaseEvent(key="key", value="value4"))

        self.client._default_namespace = "a"
        h.stop()
        events = self.client.list_events("key", version=event1.version)
        self.assertEqual(2, len(events))
        self.assertEqual(2, len(event_list))

        # listen by event_type
        print('listen by event_type')
        event_list.clear()
        h = self.client.start_listen_event(key="key",
                                           watcher=TestWatch(event_list),
                                           start_time=int(time.time() * 1000),
                                           event_type='e')
        self.client.send_event(BaseEvent(key="key", value="value2", event_type='e'))
        self.client.send_event(BaseEvent(key="key", value="value2", event_type='f'))
        h.stop()
        self.assertEqual(1, len(event_list))

        event_list.clear()
        h = self.client.start_listen_event(key="key",
                                           start_time=int(time.time() * 1000),
                                           watcher=TestWatch(event_list))
        self.client.send_event(BaseEvent(key="key", value="value2", event_type='e'))
        self.client.send_event(BaseEvent(key="key", value="value2", event_type='f'))
        h.stop()
        self.assertEqual(2, len(event_list))

        # listen by namespace
        print("listen by namespace")
        self.client._default_namespace = "a"
        event_list.clear()
        h = self.client.start_listen_event(key="key",
                                           start_time=int(time.time() * 1000),
                                           watcher=TestWatch(event_list),
                                           namespace='a')
        self.client.send_event(BaseEvent(key="key", value="value2"))
        self.client._default_namespace = "b"
        self.client.send_event(BaseEvent(key="key", value="value2"))
        h.stop()
        self.assertEqual(1, len(event_list))

        event_list.clear()
        h = self.client.start_listen_event(key="key",
                                           start_time=int(time.time() * 1000),
                                           watcher=TestWatch(event_list),
                                           namespace='*')
        self.client._default_namespace = "a"
        self.client.send_event(BaseEvent(key="key", value="value2"))
        self.client._default_namespace = "b"
        self.client.send_event(BaseEvent(key="key", value="value2"))
        h.stop()
        self.assertEqual(2, len(event_list))

        # listen by sender
        print("listen by sender")
        event_list.clear()
        h = self.client.start_listen_event(key="key",
                                           watcher=TestWatch(event_list),
                                           start_time=int(time.time() * 1000),
                                           namespace='*',
                                           sender='s')
        self.client._sender = "s"
        self.client.send_event(BaseEvent(key="key", value="value2"))
        self.client._sender = "p"
        self.client.send_event(BaseEvent(key="key", value="value2"))
        h.stop()
        self.assertEqual(1, len(event_list))

        event_list.clear()
        h = self.client.start_listen_event(key="key",
                                           watcher=TestWatch(event_list),
                                           start_time=int(time.time() * 1000),
                                           namespace='*')
        self.client._sender = "s"
        self.client.send_event(BaseEvent(key="key", value="value2"))
        self.client._sender = "p"
        self.client.send_event(BaseEvent(key="key", value="value2"))
        h.stop()
        self.assertEqual(2, len(event_list))

    def test_all_listen_events(self):
        self.client.send_event(BaseEvent(key="key", value="value1"))
        event2 = self.client.send_event(BaseEvent(key="key", value="value2"))
        start_time = event2.create_time
        self.client.send_event(BaseEvent(key="key", value="value3"))
        events = self.client.list_all_events(start_time)
        self.assertEqual(2, len(events))

    def test_list_all_events_with_id_range(self):
        event1 = self.client.send_event(BaseEvent(key="key", value="value1"))
        self.client.send_event(BaseEvent(key="key", value="value2"))
        event3 = self.client.send_event(BaseEvent(key="key", value="value3"))
        events = self.client.list_all_events(start_version=event1.version, end_version=event3.version)
        self.assertEqual(2, len(events))

    def test_listen_all_events(self):
        event_list = []

        class TestWatch(EventWatcher):
            def __init__(self, event_list) -> None:
                super().__init__()
                self.event_list = event_list

            def process(self, events: List[BaseEvent]):
                self.event_list.extend(events)

        handle = None
        try:
            handle = self.client.start_listen_events(watcher=TestWatch(event_list))
            self.client.send_event(BaseEvent(key="key1", value="value1"))
            self.client.send_event(BaseEvent(key="key2", value="value2"))
            self.client.send_event(BaseEvent(key="key3", value="value3"))
        finally:
            if handle is not None:
                handle.stop()
        self.assertEqual(3, len(event_list))

    def test_listen_all_events_from_id(self):
        event_list = []

        class TestWatch(EventWatcher):
            def __init__(self, event_list) -> None:
                super().__init__()
                self.event_list = event_list

            def process(self, events: List[BaseEvent]):
                self.event_list.extend(events)

        try:
            event1 = self.client.send_event(BaseEvent(key="key1", value="value1"))
            self.client.start_listen_events(watcher=TestWatch(event_list), version=event1.version)
            self.client.send_event(BaseEvent(key="key2", value="value2"))
            self.client.send_event(BaseEvent(key="key3", value="value3"))
        finally:
            self.client.stop_listen_events()
        self.assertEqual(2, len(event_list))

    def test_get_latest_version(self):
        event = self.client.send_event(BaseEvent(key="key", value="value1"))
        event = self.client.send_event(BaseEvent(key="key", value="value2"))
        latest_version = self.client.get_latest_version(key="key")
        self.assertEqual(event.version, latest_version)

    def test_list_any_condition(self):
        self.client._default_namespace = 'a'
        self.client._sender = 's'
        self.client.send_event(BaseEvent(key="key_1", value="value1"))
        self.client.send_event(BaseEvent(key="key_2", value="value2"))
        result = self.client.list_events(key='*', event_type='*')
        self.assertEqual(2, len(result))
        self.client._default_namespace = 'b'
        self.client._sender = 'p'
        self.client.send_event(BaseEvent(key="key_1", value="value1", event_type='event_type'))
        result = self.client.list_events(key='*', event_type='*')
        self.assertEqual(1, len(result))
        result = self.client.list_events(key='*', event_type='*', namespace='*')
        self.assertEqual(3, len(result))
        result = self.client.list_events(key='key_1', event_type='*', namespace='*')
        self.assertEqual(2, len(result))
        result = self.client.list_events(key='key_1', event_type='event_type', namespace='*')
        self.assertEqual(1, len(result))
        result = self.client.list_events(key='key_1', namespace='*')
        self.assertEqual(2, len(result))
        result = self.client.list_events(key='key_1', namespace='*', sender='*')
        self.assertEqual(2, len(result))
        result = self.client.list_events(key='key_1', namespace='*', sender='s')
        self.assertEqual(1, len(result))
        result = self.client.list_events(key='key_1', namespace='*', sender='p')
        self.assertEqual(1, len(result))


class DbStorageTest(unittest.TestCase, NotificationTest):

    @classmethod
    def set_up_class(cls):
        cls.storage = DbEventStorage()
        cls.master = NotificationMaster(NotificationService(cls.storage))
        cls.master.run()

    @classmethod
    def setUpClass(cls):
        cls.set_up_class()

    @classmethod
    def tearDownClass(cls):
        cls.master.stop()

    def setUp(self):
        self.storage.clean_up()
        self.client = NotificationClient(server_uri="localhost:50051")

    def tearDown(self):
        self.client.stop_listen_events()
        self.client.stop_listen_event()


class MemoryStorageTest(unittest.TestCase, NotificationTest):

    @classmethod
    def set_up_class(cls):
        cls.storage = MemoryEventStorage()
        cls.master = NotificationMaster(NotificationService(cls.storage))
        cls.master.run()

    @classmethod
    def setUpClass(cls):
        cls.set_up_class()

    @classmethod
    def tearDownClass(cls):
        cls.master.stop()

    def setUp(self):
        self.storage.clean_up()
        self.client = NotificationClient(server_uri="localhost:50051")

    def tearDown(self):
        self.client.stop_listen_events()
        self.client.stop_listen_event()


class HaDbStorageTest(unittest.TestCase, NotificationTest):
    """
    This test is used to ensure the high availability would not break the original functionality.
    """

    @classmethod
    def set_up_class(cls):
        cls.storage = DbEventStorage()
        cls.master1 = start_ha_master("localhost", 50051)
        # The server startup is asynchronous, we need to wait for a while
        # to ensure it writes its metadata to the db.
        time.sleep(0.1)
        cls.master2 = start_ha_master("localhost", 50052)
        time.sleep(0.1)
        cls.master3 = start_ha_master("localhost", 50053)
        time.sleep(0.1)

    @classmethod
    def setUpClass(cls):
        cls.set_up_class()

    @classmethod
    def tearDownClass(cls):
        cls.master1.stop()
        cls.master2.stop()
        cls.master3.stop()

    def setUp(self):
        self.storage.clean_up()
        self.client = NotificationClient(server_uri="localhost:50052", enable_ha=True,
                                         list_member_interval_ms=1000,
                                         retry_timeout_ms=10000)

    def tearDown(self):
        self.client.stop_listen_events()
        self.client.stop_listen_event()
        self.client.disable_high_availability()
