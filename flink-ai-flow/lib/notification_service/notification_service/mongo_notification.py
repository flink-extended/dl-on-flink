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
from typing import Tuple

from mongoengine import (Document, IntField, StringField, SequenceField)
from notification_service.base_notification import BaseEvent, ANY_CONDITION


class MongoEvent(Document):
    server_ip = StringField()   # track server that the event belongs to
    key = StringField()
    value = StringField()
    event_type = StringField()
    version = SequenceField()  # use 'version' as the auto increase id
    create_time = IntField()
    context = StringField()
    namespace = StringField()
    sender = StringField()
    uuid = StringField()

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value,
            "event_type": self.event_type,
            "version": int(self.version),
            "create_time": self.create_time,
            "context": self.context,
            "namespace": self.namespace,
            "sender": self.sender
        }

    def to_base_event(self):
        base_event = BaseEvent(**self.to_dict())
        return base_event

    @classmethod
    def convert_to_base_events(cls, mongo_events: list = None):
        if not mongo_events:
            return []
        base_events = []
        for mongo_event in mongo_events:
            base_events.append(mongo_event.to_base_event())
        return base_events

    @classmethod
    def get_base_events_by_version(cls, start_version: int, end_version: int = None):
        conditions = dict()
        conditions["version__gt"] = start_version
        if end_version is not None and end_version > 0:
            conditions["version__lte"] = end_version
        mongo_events = cls.objects(**conditions).order_by("version")
        return cls.convert_to_base_events(mongo_events)

    @classmethod
    def get_base_events(cls,
                        key: Tuple[str],
                        version: int = None,
                        event_type: str = None,
                        start_time: int = None,
                        namespace: str = None,
                        sender: str = None):
        conditions = dict()
        if len(key) == 1:
            if ANY_CONDITION != key[0]:
                conditions["key"] = key[0]
        elif len(key) > 1:
            conditions["key__in"] = list(key)
        if version is not None and version > 0:
            conditions["version__gt"] = version
        if event_type is not None:
            if event_type != ANY_CONDITION:
                conditions["event_type"] = event_type
        if start_time is not None and start_time > 0:
            conditions["start_time_gte"] = start_time
        if ANY_CONDITION != namespace:
            conditions["namespace"] = namespace
        if sender is not None and ANY_CONDITION != sender:
            conditions["sender"] = sender
        mongo_events = cls.objects(**conditions).order_by("version")
        return cls.convert_to_base_events(mongo_events)

    @classmethod
    def get_base_events_by_time(cls, create_time: int = None):
        mongo_events = cls.objects(create_time__gte=create_time).order_by("version")
        return cls.convert_to_base_events(mongo_events)

    @classmethod
    def get_by_key(cls, key: str = None, start: int = None, end: int = None, sort_key: str = "version"):
        if key:
            return cls.objects(key=key).order_by(sort_key)[start:end]
        else:
            raise Exception("key is empty, please provide valid key")

    @classmethod
    def delete_by_client(cls, server_ip):
        cls.objects(server_ip=server_ip).delete()
