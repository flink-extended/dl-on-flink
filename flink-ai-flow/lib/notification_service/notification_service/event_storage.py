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
from notification_service.base_notification import BaseEvent


class BaseEventStorage(object):

    def add_event(self, event: BaseEvent):
        pass

    def list_events(self, key: str, version: int = None):
        pass

    def list_all_events(self, start_time: int):
        pass

    def list_all_events_from_id(self, id: int):
        pass


class MemoryEventStorage(BaseEventStorage):
    def __init__(self):
        self.store = []
        self.max_id = 0
        self.kv = {}

    def add_event(self, event: BaseEvent):
        self.max_id += 1
        event.id = self.max_id
        event.create_time = time.time_ns()
        if event.key not in self.kv:
            self.kv[event.key] = 0
        self.kv[event.key] += 1
        event.version = self.kv[event.key]
        self.store.append(event)
        return event

    def list_events(self, key: str, version: int = None):
        res = []
        for event in self.store:
            if event.key == key and event.version > version:
                res.append(event)
        return res

    def list_all_events(self, start_time: int):
        res = []
        for event in self.store:
            if event.create_time >= start_time:
                res.append(event)
        return res

    def list_all_events_from_id(self, id: int):
        res = []
        for event in self.store:
            if event.id > id:
                res.append(event)
        return res

    def clean_up(self):
        self.store.clear()
        self.kv.clear()
        self.max_id = 0

