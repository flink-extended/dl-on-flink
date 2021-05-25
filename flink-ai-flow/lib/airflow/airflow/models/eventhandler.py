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
from __future__ import annotations

import json
from typing import Tuple, Dict
from notification_service.base_notification import BaseEvent, DEFAULT_NAMESPACE, ANY_CONDITION
from airflow.executors.scheduling_action import SchedulingAction


class EventKey(object):

    def __init__(self, key, event_type, namespace=DEFAULT_NAMESPACE, sender=ANY_CONDITION) -> None:
        super().__init__()
        self.key = key
        self.event_type = event_type
        self.namespace = namespace
        self.sender = sender


class EventHandler(object):
    """
    EventMetHandler: process event[Event] message and task decide what [TaskAction] to take.
    """
    def handle_event(self, event: BaseEvent, task_state: object) -> Tuple[SchedulingAction, object]:
        """
        :param event: scheduler accepted event.
        :param task_state: user defined state that can help decide the [TaskAction].
        :return: TaskAction to take, the user defined state
        """
        pass

    @staticmethod
    def serialize(handler_to_serialize: EventHandler) -> str:
        """
        Serialize the event handler to json string. All field of the event handler should be JSON serializable.
        If some fields are not JSON serializable, TypeError will raise.
        :param handler_to_serialize: the event handler to serialize.
        :type handler_to_serialize: EventHandler
        :return: json string.
        :rtype: str
        """
        object_dict = dict(handler_to_serialize.__dict__)
        object_dict['__module'] = handler_to_serialize.__class__.__module__
        object_dict['__classname'] = handler_to_serialize.__class__.__name__
        return json.dumps(object_dict)

    @staticmethod
    def deserialize(str_to_deserialize: str) -> EventHandler:
        """
        Deserialize the event handler json string to event handler.
        The json string should be a dictionary that includes both __module__ and __classname__. If either is missing,
        KeyError will raise.
        :param str_to_deserialize: json string to deserialize to event handler.
        :type str_to_deserialize: str
        :return: Deserialized event handler
        :rtype: EventHandler
        """
        import importlib
        object_dict: Dict = json.loads(str_to_deserialize)
        module_name = object_dict.pop('__module')
        classname = object_dict.pop('__classname')
        module = importlib.import_module(module_name)
        clazz = getattr(module, classname)
        handler = clazz(**object_dict)
        for k, v in object_dict.items():
            setattr(handler, k, v)
        return handler

