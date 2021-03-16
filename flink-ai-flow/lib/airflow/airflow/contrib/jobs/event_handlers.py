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

from typing import Tuple

from airflow.executors.scheduling_action import SchedulingAction
from airflow.models.eventhandler import EventHandler
from notification_service.base_notification import BaseEvent


class StartEventHandler(EventHandler):
    """
    Internal event handler that always return start scheduling action.
    """

    def handle_event(self, event: BaseEvent, task_state: object) -> Tuple[SchedulingAction, object]:
        return SchedulingAction.START, task_state


class RestartEventHandler(EventHandler):
    """
    Internal event handler that always return restart scheduling action.
    """

    def handle_event(self, event: BaseEvent, task_state: object) -> Tuple[SchedulingAction, object]:
        return SchedulingAction.RESTART, task_state


class ActionEventHandler(EventHandler):
    """
    Internal event handler that handle event base on the key of the event.
    """

    def handle_event(self, event: BaseEvent, task_state: object) -> Tuple[SchedulingAction, object]:
        if 'stop' == event.key:
            return SchedulingAction.STOP, task_state
        elif 'restart' == event.key:
            return SchedulingAction.RESTART, task_state
        else:
            return SchedulingAction.START, task_state
