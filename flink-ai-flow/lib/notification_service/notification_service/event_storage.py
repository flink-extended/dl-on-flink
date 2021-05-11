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
from abc import ABC, abstractmethod
from collections import Iterable
from typing import Union, Tuple

from notification_service.base_notification import BaseEvent, ANY_CONDITION
from notification_service.util import db
from notification_service.util.db import EventModel


class BaseEventStorage(ABC):

    @abstractmethod
    def add_event(self, event: BaseEvent, uuid: str):
        pass

    @abstractmethod
    def list_events(self,
                    key: Union[str, Tuple[str]],
                    version: int = None,
                    event_type: str = None,
                    start_time: int = None,
                    namespace: str = None,
                    sender: str = None):
        pass

    @abstractmethod
    def list_all_events(self, start_time: int):
        pass

    @abstractmethod
    def list_all_events_from_version(self, start_version: int, end_version: int = None):
        pass

    @abstractmethod
    def clean_up(self):
        pass

    @abstractmethod
    def get_latest_version(self, key: str, namespace: str = None):
        pass


class MemoryEventStorage(BaseEventStorage):

    def __init__(self):
        self.store = []
        self.max_version = 0

    def add_event(self, event: BaseEvent, uuid: str):
        self.max_version += 1
        event.create_time = int(time.time() * 1000)
        event.version = self.max_version
        self.store.append(event)
        return event

    def list_events(self,
                    key: Union[str, Tuple[str]],
                    version: int = None,
                    event_type: str = None,
                    start_time: int = None,
                    namespace: str = None,
                    sender: str = None):
        res = []
        key = None if key == "" else key
        version = None if version == 0 else version
        event_type = None if event_type == "" else event_type
        namespace = None if namespace == "" else namespace
        sender = None if sender == "" else sender
        if isinstance(key, str):
            key = (key, )
        elif isinstance(key, Iterable):
            key = tuple(key)
        for event in self.store:
            if key is not None and event.key not in key and ANY_CONDITION not in key:
                continue
            if version is not None and event.version <= version:
                continue
            if event_type is not None and event.event_type != event_type and event_type != ANY_CONDITION:
                continue
            if start_time is not None and event.create_time < start_time:
                continue
            if namespace is not None and namespace != ANY_CONDITION and event.namespace != namespace:
                continue
            if sender is not None and sender != ANY_CONDITION and event.sender != sender:
                continue
            res.append(event)
        return res

    def list_all_events(self, start_time: int):
        res = []
        for event in self.store:
            if event.create_time >= start_time:
                res.append(event)
        return res

    def list_all_events_from_version(self, start_version: int, end_version: int = None):
        res = []
        for event in self.store:
            if 0 < end_version < event.version:
                continue
            if event.version > start_version:
                res.append(event)
        return res

    def get_latest_version(self, key: str, namespace: str = None):
        return self.max_version

    def clean_up(self):
        self.store.clear()
        self.max_version = 0


class DbEventStorage(BaseEventStorage):

    def __init__(self, db_conn=None, create_table_if_not_exists=True):
        if db_conn is not None:
            db.SQL_ALCHEMY_CONN = db_conn
        if create_table_if_not_exists:
            EventModel.create_table(db.SQL_ALCHEMY_CONN)

    def add_event(self, event: BaseEvent, uuid: str):
        return EventModel.add_event(event, uuid)

    def list_events(self,
                    key: Union[str, Tuple[str]],
                    version: int = None,
                    event_type: str = None,
                    start_time: int = None,
                    namespace: str = None,
                    sender: str = None):
        return EventModel.list_events(key, version, event_type, start_time, namespace, sender)

    def list_all_events(self, start_time: int):
        return EventModel.list_all_events(start_time)

    def list_all_events_from_version(self, start_version: int, end_version: int = None):
        return EventModel.list_all_events_from_version(start_version, end_version)

    def get_latest_version(self, key: str, namespace: str = None):
        return EventModel.get_latest_version()

    def clean_up(self):
        EventModel.cleanup()
