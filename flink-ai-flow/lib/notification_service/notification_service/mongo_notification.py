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
from mongoengine import (Document, IntField, StringField, SequenceField)
from notification_service.base_notification import BaseEvent


class MongoEvent(Document):
    server_id = StringField()
    key = StringField()
    value = StringField()
    event_type = StringField()
    version = SequenceField()
    create_time = IntField()
    auto_increase_id = SequenceField()

    @property
    def str_id(self):
        if self.id:
            return str(self.id)

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value,
            "event_type": self.event_type,
            "version": self.version,
            "create_time": self.create_time,
            "id": int(self.auto_increase_id),
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
    def get_base_events_by_id(cls, server_id: str, event_id: int = None):
        mongo_events = cls.objects(server_id=server_id).filter(auto_increase_id__gt=event_id).order_by("version")
        return cls.convert_to_base_events(mongo_events)

    @classmethod
    def get_base_events_by_version(cls, server_id: str, key: str, version: int = None):
        mongo_events = cls.objects(server_id=server_id, key=key).filter(version__gt=version).order_by("version")
        return cls.convert_to_base_events(mongo_events)

    @classmethod
    def get_base_events_by_time(cls, server_id: str, create_time: int = None):
        mongo_events = cls.objects(server_id=server_id).filter(create_time__gte=create_time).order_by("version")
        return cls.convert_to_base_events(mongo_events)

    @classmethod
    def get_by_key(cls, server_id: str, key: str = None, start: int = None, end: int = None, sort_key: str = "version"):
        if key:
            return cls.objects(server_id=server_id, key=key).order_by(sort_key)[start:end]
        else:
            raise Exception("key is empty, please provide valid key")

    @classmethod
    def delete_by_client(cls, server_id):
        cls.objects(server_id=server_id).delete()
