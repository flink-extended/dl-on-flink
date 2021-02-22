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
import unittest
from typing import Tuple

from notification_service.base_notification import BaseEvent

from airflow.executors.scheduling_action import SchedulingAction
from airflow.models.eventhandler import EventHandler


class MockEventHandler(EventHandler):

    def __init__(self, start: int, step: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.start = start
        self.step = step

    def handle_event(self, event: BaseEvent, task_state: int) -> Tuple[SchedulingAction, int]:
        if task_state is None:
            task_state = self.start
        else:
            task_state = task_state + self.step
        return SchedulingAction.NONE, task_state


class TestEventHandler(unittest.TestCase):
    def test_serialize(self):
        mock_event = BaseEvent(key="k", value="v")
        event_handler = MockEventHandler(0, 1)
        s = EventHandler.serialize(event_handler)
        deserialized_event_handler = EventHandler.deserialize(s)
        assert type(deserialized_event_handler) == type(event_handler)
        assert deserialized_event_handler.handle_event(mock_event, None) == (SchedulingAction.NONE, 0)
        assert deserialized_event_handler.handle_event(mock_event, 0) == (SchedulingAction.NONE, 1)
