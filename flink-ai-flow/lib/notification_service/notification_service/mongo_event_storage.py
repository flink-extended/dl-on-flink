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
import socket
from collections import Iterable
from typing import Union, Tuple

from mongoengine import connect
from notification_service.event_storage import BaseEventStorage
from notification_service.base_notification import BaseEvent
from notification_service.mongo_notification import MongoEvent


class MongoEventStorage(BaseEventStorage):
    def __init__(self, *args, **kwargs):
        self.db_conn = self.setup_connection(**kwargs)
        self.server_ip = socket.gethostbyname(socket.gethostname())

    def setup_connection(self, **kwargs):
        db_conf = {
            "host": kwargs.get("host"),
            "port": kwargs.get("port"),
            "db": kwargs.get("db"),
        }
        username = kwargs.get("username", None)
        password = kwargs.get("password", None)
        authentication_source = kwargs.get("authentication_source", "admin")
        if (username or password) and not (username and password):
            raise Exception("Please provide valid username and password")
        if username and password:
            db_conf.update({
                "username": username,
                "password": password,
                "authentication_source": authentication_source
            })
        return connect(**db_conf)

    def get_latest_version(self, key: str, namespace: str = None):
        mongo_events = MongoEvent.get_by_key(key, 0, 1, "-version")
        if not mongo_events:
            return 0
        return mongo_events[0].version

    def add_event(self, event: BaseEvent, uuid: str):
        kwargs = {
            "server_ip": self.server_ip,
            "create_time": int(time.time() * 1000),
            "event_type": event.event_type,
            "key": event.key,
            "value": event.value,
            "context": event.context,
            "namespace": event.namespace,
            "sender": event.sender,
            "uuid": uuid
        }
        mongo_event = MongoEvent(**kwargs)
        mongo_event.save()
        mongo_event.reload()
        event.create_time = mongo_event.create_time
        event.version = mongo_event.version
        return event

    def list_events(self,
                    key: Union[str, Tuple[str]],
                    version: int = None,
                    event_type: str = None,
                    start_time: int = None,
                    namespace: str = None,
                    sender: str = None):
        key = None if key == "" else key
        version = None if version == 0 else version
        event_type = None if event_type == "" else event_type
        namespace = None if namespace == "" else namespace
        sender = None if sender == "" else sender
        if isinstance(key, str):
            key = (key,)
        elif isinstance(key, Iterable):
            key = tuple(key)
        res = MongoEvent.get_base_events(key, version, event_type, start_time, namespace, sender)
        return res

    def list_all_events(self, start_time: int):
        res = MongoEvent.get_base_events_by_time(start_time)
        return res

    def list_all_events_from_version(self, start_version: int, end_version: int = None):
        res = MongoEvent.get_base_events_by_version(start_version, end_version)
        return res

    def clean_up(self):
        MongoEvent.delete_by_client(self.server_ip)
