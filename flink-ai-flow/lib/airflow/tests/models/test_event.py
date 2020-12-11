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

from tests.test_utils.db import clear_db_event_model
import unittest
import time
from airflow import settings
from airflow.models.event import EventModel, Event, EventType


class EventModelTest(unittest.TestCase):
    def setUp(self):
        clear_db_event_model()

    def test_events(self):
        session = settings.Session()
        event = EventModel.add_event(event=Event(key="key", value="value1"), session=session)
        self.assertTrue(event is not None)
        self.assertEqual(1, event.version)
        events = EventModel.list_all_events(start_time=0, session=session)
        self.assertGreater(len(events), 0)
        event = EventModel.add_event(event=Event(key="key", value="value2"), session=session)
        event = EventModel.add_event(event=Event(key="key", value="value3"), session=session)

        events = EventModel.list_events(key='key', version=1)
        self.assertEqual(2, len(events))

    def test_none_events(self):
        events = EventModel.list_all_events(start_time=0)
        self.assertEqual([], events)

    def test_event_type(self):
        self.assertTrue(EventType.is_in('TASK_STATUS_CHANGED'))

        self.assertTrue(not EventType.is_in('MODEL_DEPLOYED'))
