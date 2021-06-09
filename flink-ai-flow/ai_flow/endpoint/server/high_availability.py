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
import asyncio
import logging

import grpc
import threading
import time
import uuid
from abc import ABC, abstractmethod

from typing import Dict

from ai_flow.protobuf.high_availability_pb2 import ListMembersResponse, ReturnStatus, MemberProto, \
    NotifyNewMemberResponse, NotifyNewMemberRequest
from ai_flow.protobuf.high_availability_pb2_grpc import HighAvailabilityManagerServicer, \
    HighAvailabilityManagerStub

if not hasattr(time, 'time_ns'):
    time.time_ns = lambda: int(time.time() * 1e9)


class Member(object):

    def __init__(self, version, server_uri, update_time):
        self.version = version
        self.server_uri = server_uri
        self.update_time = update_time


def member_to_proto(member: Member):
    return MemberProto(
        version=member.version, server_uri=member.server_uri, update_time=member.update_time)


def proto_to_member(member_proto):
    return Member(member_proto.version, member_proto.server_uri, member_proto.update_time)


def sleep_and_detecting_running(interval_ms, is_running_callable, min_interval_ms=500):
    start_time = time.time_ns() / 1000000
    while is_running_callable() and time.time_ns() / 1000000 < start_time + interval_ms:
        remaining = time.time_ns() / 1000000 - start_time
        if remaining > min_interval_ms:
            time.sleep(min_interval_ms / 1000)
        else:
            time.sleep(remaining / 1000)


class AIFlowServerHaManager(ABC):

    @abstractmethod
    def start(self, server_uri, storage, ttl_ms):
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


class SimpleAIFlowServerHaManager(AIFlowServerHaManager):

    def __init__(self):
        self.server_uri = None
        self.storage = None
        self.ttl_ms = None
        self.living_members = []
        self.member_connections = {}  # type: Dict[str, HighAvailabilityManagerStub]
        self.running = False
        self.heartbeat_thread = None
        self.notified_others_after_start = False
        self.uuid = str(uuid.uuid4())

    def start(self, server_uri, storage, ttl_ms):
        self.server_uri = server_uri
        self.storage = storage
        self.ttl_ms = ttl_ms
        self.running = True
        self.heartbeat_thread = threading.Thread(target=self.start_heartbeat, daemon=True)
        self.heartbeat_thread.start()

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
                            HighAvailabilityManagerStub(channel)
                        try:
                            self.member_connections[member.server_uri].notifyNewMember(
                                NotifyNewMemberRequest(member=member_to_proto(
                                    Member(1, self.server_uri, int(time.time_ns() / 1000000))
                                )))
                        except grpc.RpcError:
                            logging.error("Notify new member to '%s' failed." % member.server_uri,
                                          exc_info=True)
                    self.notified_others_after_start = True
            except Exception:
                logging.error("Exception thrown when send heartbeat to the HA storage.",
                              exc_info=True)
            sleep_and_detecting_running(self.ttl_ms / 2, lambda: self.running)

    def get_living_members(self):
        if len(self.living_members) == 0:
            self.living_members = self.storage.list_living_members(self.ttl_ms)
        return self.living_members

    def add_living_member(self, member: Member):
        if member.server_uri not in [member.server_uri for member in self.living_members]:
            self.living_members.append(member)

    def stop(self):
        self.running = False
        self.heartbeat_thread.join()


class HighAvailableService(HighAvailabilityManagerServicer):

    def __init__(self,
                 ha_manager,
                 server_uri,
                 ha_storage,
                 ttl_ms: int = 10000):
        self.ha_manager = ha_manager
        self.server_uri = server_uri
        self.ha_storage = ha_storage
        self.ttl_ms = ttl_ms
        self.member_updated_condition = asyncio.Condition()

    def start(self):
        self.ha_manager.start(self.server_uri,
                              self.ha_storage,
                              self.ttl_ms)

    def stop(self):
        self.ha_manager.stop()

    @asyncio.coroutine
    def listMembers(self, request, context):
        try:
            return self._list_members(request)
        except Exception as e:
            return ListMembersResponse(
                return_code=ReturnStatus.CALL_ERROR, return_msg=str(e))

    async def _list_members(self, request):
        timeout_seconds = request.timeout_seconds
        if 0 == timeout_seconds:
            return ListMembersResponse(
                return_code=ReturnStatus.CALL_SUCCESS,
                return_msg='',
                members=[member_to_proto(member) for member in self.ha_manager.get_living_members()])
        else:
            start = time.time()
            members = self.ha_manager.get_living_members()
            async with self.member_updated_condition:
                while time.time() - start < timeout_seconds:
                    try:
                        await asyncio.wait_for(self.member_updated_condition.wait(),
                                               timeout_seconds - time.time() + start)
                        members = self.ha_manager.get_living_members()
                        break
                    except asyncio.TimeoutError:
                        pass
            return ListMembersResponse(
                return_code=ReturnStatus.CALL_SUCCESS,
                return_msg='',
                members=[member_to_proto(member) for member in members])

    @asyncio.coroutine
    def notifyNewMember(self, request, context):
        try:
            return self._notify_new_member(request)
        except Exception as e:
            return ListMembersResponse(
                return_code=ReturnStatus.CALL_ERROR, return_msg=str(e))

    async def _notify_new_member(self, request):
        self.ha_manager.add_living_member(proto_to_member(request.member))
        async with self.member_updated_condition:
            self.member_updated_condition.notify_all()
        return NotifyNewMemberResponse(
            return_code=ReturnStatus.CALL_SUCCESS,
            return_msg='')
