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
import uuid
from typing import List, Dict

import grpc
import logging
import threading
from abc import ABC, abstractmethod
from collections import deque

from notification_service.base_notification import Member, BaseEvent
from notification_service.proto import notification_service_pb2_grpc
from notification_service.proto.notification_service_pb2 import NotifyRequest, Notify, NotifyNewMemberRequest
from notification_service.proto.notification_service_pb2_grpc import NotificationServiceStub
from notification_service.util import db
from notification_service.util.db import MemberModel
from notification_service.util.utils import sleep_and_detecting_running, member_to_proto


class NotificationServerHaManager(ABC):

    @abstractmethod
    def start(self, server_uri, storage, ttl_ms, min_notify_interval, member_updated_condition):
        pass

    @abstractmethod
    def notify_others(self, event: BaseEvent):
        pass

    @abstractmethod
    def get_living_members(self):
        pass

    @abstractmethod
    def add_living_member(self, member: Member):
        pass

    @abstractmethod
    def stop(self):
        pass


class HighAvailabilityStorage(ABC):

    @abstractmethod
    def list_living_members(self, ttl_ms) -> List[Member]:
        pass

    @abstractmethod
    def update_member(self, server_uri, server_uuid):
        pass

    @abstractmethod
    def clear_dead_members(self, ttl_ms):
        pass


class DbHighAvailabilityStorage(HighAvailabilityStorage):

    def __init__(self, db_conn=None, create_table_if_not_exists=True):
        if db_conn is not None:
            db.SQL_ALCHEMY_CONN = db_conn
        if create_table_if_not_exists:
            MemberModel.create_table(db.SQL_ALCHEMY_CONN)

    def list_living_members(self, ttl_ms):
        return MemberModel.get_living_members(ttl_ms)

    def list_dead_members(self, ttl_ms):
        return MemberModel.get_dead_members(ttl_ms)

    def update_member(self, server_uri, server_uuid):
        MemberModel.update_member(server_uri, server_uuid)

    def delete_member(self, server_uri=None, server_uuid=None):
        MemberModel.delete_member(server_uri, server_uuid)

    def clear_dead_members(self, ttl_ms):
        MemberModel.clear_dead_members(ttl_ms)


class SimpleNotificationServerHaManager(NotificationServerHaManager):

    def __init__(self):
        self.server_uri = None
        self.storage = None  # type: HighAvailabilityStorage
        self.ttl_ms = None
        self.cached_notify = deque()
        self.living_members = []
        self.member_connections = {}  # type: Dict[str, NotificationServiceStub]
        self.running = False
        self.heartbeat_thread = None
        self.notify_thread = None
        self.min_notify_interval_ms = None
        self.notified_others_after_start = False
        self.member_updated_condition = None
        self.uuid = str(uuid.uuid4())

    def start(self, server_uri, storage, ttl_ms, min_notify_interval_ms, member_updated_condition):
        self.server_uri = server_uri
        self.storage = storage
        self.ttl_ms = ttl_ms
        self.min_notify_interval_ms = min_notify_interval_ms
        self.member_updated_condition = member_updated_condition
        self.running = True
        self.heartbeat_thread = threading.Thread(target=self.start_heartbeat, daemon=True)
        self.heartbeat_thread.start()
        self.notify_thread = threading.Thread(target=self.start_notify, daemon=True)
        self.notify_thread.start()

    def start_heartbeat(self):
        while self.running:
            try:
                # do heartbeat
                self.storage.clear_dead_members(self.ttl_ms)
                self.storage.update_member(self.server_uri, self.uuid)
                self.living_members = self.storage.list_living_members(self.ttl_ms)
                if not self.notified_others_after_start:
                    for member in self.living_members:
                        if member.server_uri == self.server_uri:
                            continue
                        channel = grpc.insecure_channel(member.server_uri)
                        self.member_connections[member.server_uri] = \
                            notification_service_pb2_grpc.NotificationServiceStub(channel)
                        try:
                            self.member_connections[member.server_uri].notifyNewMember(
                                NotifyNewMemberRequest(member=member_to_proto(
                                    Member(1, self.server_uri, int(time.time_ns() / 1000000))
                                )))
                        except grpc.RpcError:
                            logging.error("Notify new member to '%s' failed." % member.server_uri,
                                          exc_info=True)
                    self.notified_others_after_start = True
            except Exception as e:
                logging.error("Exception thrown when send heartbeat to the HA storage.",
                              exc_info=True)
            sleep_and_detecting_running(self.ttl_ms / 2, lambda: self.running)

    def start_notify(self):
        while self.running:
            # update connections
            living_member_server_uris = set()
            for member in self.living_members:
                if member.server_uri == self.server_uri:
                    continue
                if member.server_uri not in self.member_connections:
                    try:
                        channel = grpc.insecure_channel(member.server_uri)
                        self.member_connections[member.server_uri] = \
                            notification_service_pb2_grpc.NotificationServiceStub(channel)
                    except Exception:
                        logging.error("Exception thrown when connect to another member: %s." %
                                      member.server_uri,
                                      exc_info=True)
                        continue
                living_member_server_uris.add(member.server_uri)
            for server_uri in list(self.member_connections.keys()):
                if server_uri not in living_member_server_uris:
                    del self.member_connections[server_uri]

            notifies = []
            while len(self.cached_notify) > 0:
                event = self.cached_notify.popleft()
                notify = Notify(key=event.key, namespace=event.namespace)
                notifies.append(notify)

            # notify others
            if len(notifies) > 0:
                for server_uri, stub in self.member_connections.items():
                    try:
                        stub.notify(NotifyRequest(notifies=notifies))
                    except Exception:
                        logging.error("Exception thrown when notify another member: %s." %
                                      server_uri,
                                      exc_info=True)
            sleep_and_detecting_running(self.min_notify_interval_ms, lambda: self.running, 100)

    def notify_others(self, event):
        self.cached_notify.append(event)

    def get_living_members(self):
        if len(self.living_members) == 0:
            self.living_members = self.storage.list_living_members(self.ttl_ms)
        return self.living_members

    def add_living_member(self, member: Member):
        if member.server_uri not in [member.server_uri for member in self.living_members]:
            self.living_members.append(member)

    def detach_member_from_cluster(self):
        self.storage.delete_member(self.server_uri)

    def stop(self):
        self.running = False
        self.detach_member_from_cluster()
        self.heartbeat_thread.join()
        self.notify_thread.join()
