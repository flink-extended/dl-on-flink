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
import time
import traceback

from notification_service.base_notification import BaseEvent
from notification_service.event_storage import BaseEventStorage, DbEventStorage
from notification_service.high_availability import NotificationServerHaManager
from notification_service.mongo_event_storage import MongoEventStorage
from notification_service.proto import notification_service_pb2_grpc, notification_service_pb2
from notification_service.util.utils import event_to_proto, event_list_to_proto, member_to_proto, event_proto_to_event, \
    proto_to_member
from notification_service.util.db import extract_db_engine_from_uri, DBType, parse_mongo_uri


class NotificationService(notification_service_pb2_grpc.NotificationServiceServicer):

    def __init__(self, storage: BaseEventStorage):
        self.storage = storage
        self.notification_conditions = {}
        self.lock = asyncio.Lock()
        self.write_condition = asyncio.Condition()

    @classmethod
    def from_storage_uri(cls, storage_uri: str) -> 'NotificationService':
        """
        Construct the notification service with the given storage uri
        :param storage_uri: uri of the backend storage to use
        :type storage_uri: str
        :rtype: NotificationService
        """
        db_engine = extract_db_engine_from_uri(storage_uri)
        if DBType.value_of(db_engine) == DBType.MONGODB:
            username, password, host, port, db = parse_mongo_uri(storage_uri)
            storage = MongoEventStorage(host=host,
                                        port=int(port),
                                        username=username,
                                        password=password,
                                        db=db)
            return cls(storage=storage)
        else:
            return cls(storage=DbEventStorage(storage_uri))

    def start(self):
        pass

    def stop(self):
        pass

    @asyncio.coroutine
    def sendEvent(self, request, context):
        try:
            return self._send_event(request)
        except Exception as e:
            print(e)
            traceback.print_stack()
            return notification_service_pb2.SendEventsResponse(
                return_code=notification_service_pb2.ReturnStatus.ERROR, return_msg=str(e))

    async def _send_event(self, request):
        event_proto = request.event
        event = BaseEvent(
            key=event_proto.key,
            value=event_proto.value,
            event_type=None if event_proto.event_type == "" else event_proto.event_type,
            context=None if event_proto.context == "" else event_proto.context,
            namespace=None if event_proto.namespace == "" else event_proto.namespace,
            sender=None if event_proto.sender == "" else event_proto.sender
        )
        uuid = request.uuid
        enable_idempotence = request.enable_idempotence
        key = event.key
        return_msg = ''
        # Lock conditions dict for get/check/update of key
        await self.lock.acquire()
        if self.notification_conditions.get(key) is None:
            self.notification_conditions.update({(key, asyncio.Condition())})
        # Release lock after check/update key of notification conditions dict
        self.lock.release()
        async with self.notification_conditions.get(key), self.write_condition:
            if enable_idempotence and self.storage.get_event_by_uuid(uuid) is not None:
                return_msg = 'Ignored because event already exists.'
            else:
                event: BaseEvent = self.storage.add_event(event, uuid)
            self.notification_conditions.get(key).notify_all()
            self.write_condition.notify_all()

        result_event_proto = event_to_proto(event)
        return notification_service_pb2.SendEventsResponse(
            event=result_event_proto,
            return_code=notification_service_pb2.ReturnStatus.SUCCESS,
            return_msg=return_msg)

    @asyncio.coroutine
    def listEvents(self, request, context):
        try:
            return self._list_events(request)
        except Exception as e:
            return notification_service_pb2.ListEventsResponse(
                return_code=notification_service_pb2.ReturnStatus.ERROR, return_msg=str(e))

    async def _list_events(self, request):
        keys = request.keys
        event_type = request.event_type
        start_time = request.start_time
        start_version = request.start_version
        namespace = None if request.namespace == '' else request.namespace
        sender = None if request.sender == '' else request.sender
        timeout_seconds = request.timeout_seconds

        if timeout_seconds == 0:
            event_models = self._query_events(keys, event_type, start_time, start_version, namespace, sender)
            event_proto_list = event_list_to_proto(event_models)
            return notification_service_pb2.ListEventsResponse(
                return_code=notification_service_pb2.ReturnStatus.SUCCESS,
                return_msg='',
                events=event_proto_list)
        else:
            start = time.time()
            # Lock conditions dict for get/check/update of key
            await self.lock.acquire()
            for key in keys:
                if self.notification_conditions.get(key) is None:
                    self.notification_conditions.update({(key, asyncio.Condition())})
            # Release lock after check/update key of notification conditions dict
            self.lock.release()
            event_models = []
            if len(keys) == 1:
                key = keys[0]
                condition = self.notification_conditions.get(key)
            else:
                condition = self.write_condition
            async with condition:
                while time.time() - start < timeout_seconds and len(event_models) == 0:
                    try:
                        await asyncio.wait_for(condition.wait(),
                                               timeout_seconds - time.time() + start)
                        event_models = self._query_events(
                            keys, event_type, start_time, start_version, namespace, sender)
                    except asyncio.TimeoutError:
                        pass
                if len(event_models) == 0:
                    event_models = self._query_events(
                        keys, event_type, start_time, start_version, namespace, sender)
            event_proto_list = event_list_to_proto(event_models)
            return notification_service_pb2.ListEventsResponse(
                return_code=notification_service_pb2.ReturnStatus.SUCCESS,
                return_msg='',
                events=event_proto_list)

    def _query_events(self, keys, event_type, start_time, start_version, namespace, sender):
        return self.storage.list_events(keys, start_version, event_type, start_time, namespace, sender)

    @asyncio.coroutine
    def listAllEvents(self, request, context):
        try:
            return self._list_all_events(request)
        except Exception as e:
            return notification_service_pb2.ListEventsResponse(
                return_code=notification_service_pb2.ReturnStatus.ERROR, return_msg=str(e))

    async def _list_all_events(self, request):
        start_time = request.start_time
        start_version = request.start_version
        end_version = request.end_version
        timeout_seconds = request.timeout_seconds
        if 0 == timeout_seconds:
            event_models = self._query_all_events(start_time, start_version, end_version)
            event_proto_list = event_list_to_proto(event_models)
            return notification_service_pb2.ListEventsResponse(
                return_code=notification_service_pb2.ReturnStatus.SUCCESS,
                return_msg='',
                events=event_proto_list)
        else:
            start = time.time()
            event_models = self._query_all_events(start_time, start_version, end_version)
            async with self.write_condition:
                while time.time() - start < timeout_seconds and len(event_models) == 0:
                    try:
                        await asyncio.wait_for(self.write_condition.wait(),
                                               timeout_seconds - time.time() + start)
                        event_models = self._query_all_events(
                            start_time, start_version, end_version)
                    except asyncio.TimeoutError:
                        pass
            event_proto_list = event_list_to_proto(event_models)
            return notification_service_pb2.ListEventsResponse(
                return_code=notification_service_pb2.ReturnStatus.SUCCESS,
                return_msg='',
                events=event_proto_list)

    def _query_all_events(self, start_time, start_version, end_version):
        if start_version > 0:
            return self.storage.list_all_events_from_version(start_version, end_version)
        else:
            return self.storage.list_all_events(start_time)

    @asyncio.coroutine
    def getLatestVersionByKey(self, request, context):
        try:
            return self._get_latest_version_by_key(request)
        except Exception as e:
            return notification_service_pb2.GetLatestVersionResponse(
                return_code=str(notification_service_pb2.ReturnStatus.ERROR), return_msg=str(e))

    async def _get_latest_version_by_key(self, request):
        key = request.key
        namespace = request.namespace
        timeout_seconds = request.timeout_seconds
        if 0 == timeout_seconds:
            latest_version = self._query_latest_version_by_key(key, namespace)
            return notification_service_pb2.GetLatestVersionResponse(
                return_code=str(notification_service_pb2.ReturnStatus.SUCCESS),
                return_msg='',
                version=latest_version)
        else:
            start = time.time()
            latest_version = self._query_latest_version_by_key(key, namespace)
            async with self.write_condition:
                while time.time() - start < timeout_seconds and latest_version == 0:
                    try:
                        await asyncio.wait_for(self.write_condition.wait(), timeout_seconds - time.time() + start)
                        latest_version = self._query_latest_version_by_key(key, namespace)
                    except asyncio.TimeoutError:
                        pass
            return notification_service_pb2.ListEventsResponse(
                return_code=str(notification_service_pb2.ReturnStatus.SUCCESS),
                return_msg='',
                version=latest_version)

    def _query_latest_version_by_key(self, key, namespace):
        if len(namespace) == 0:
            namespace = None
        return self.storage.get_latest_version(key=key, namespace=namespace)

    @asyncio.coroutine
    def notify(self, request, context):
        try:
            return self._notify(request)
        except Exception as e:
            return notification_service_pb2.CommonResponse(
                return_code=notification_service_pb2.ReturnStatus.ERROR, return_msg=str(e))

    async def _notify(self, request):
        for notify in request.notifies:
            if notify.key in self.notification_conditions:
                async with self.notification_conditions.get(notify.key):
                    self.notification_conditions.get(notify.key).notify_all()
        async with self.write_condition:
            self.write_condition.notify_all()
        return notification_service_pb2.CommonResponse(
            return_code=notification_service_pb2.ReturnStatus.SUCCESS,
            return_msg='')

    @asyncio.coroutine
    def listMembers(self, request, context):
        try:
            return self._list_members(request)
        except Exception as e:
            return notification_service_pb2.ListMembersResponse(
                return_code=notification_service_pb2.ReturnStatus.ERROR, return_msg=str(e))

    async def _list_members(self, request):
        # this method is used in HA mode, so we just return an empty list here.
        return notification_service_pb2.ListMembersResponse(
            return_code=notification_service_pb2.ReturnStatus.SUCCESS,
            return_msg='',
            members=[])

    @asyncio.coroutine
    def notifyNewMember(self, request, context):
        try:
            return self._notify_new_member(request)
        except Exception as e:
            return notification_service_pb2.CommonResponse(
                return_code=notification_service_pb2.ReturnStatus.ERROR, return_msg=str(e))

    async def _notify_new_member(self, request):
        # this method is used in HA mode, so we just return here.
        return notification_service_pb2.CommonResponse(
            return_code=notification_service_pb2.ReturnStatus.SUCCESS,
            return_msg='')

    @asyncio.coroutine
    def registerClient(self, request, context):
        try:
            return self._register_client(request)
        except Exception as e:
            return notification_service_pb2.RegisterClientResponse(
                return_code=notification_service_pb2.ReturnStatus.ERROR, return_msg=str(e))

    async def _register_client(self, request):
        client_id = self.storage.register_client(request.client_meta.namespace, request.client_meta.sender)
        return notification_service_pb2.RegisterClientResponse(
            return_code=notification_service_pb2.ReturnStatus.SUCCESS,
            return_msg='',
            client_id=client_id)

    @asyncio.coroutine
    def deleteClient(self, request, context):
        try:
            return self._delete_client(request)
        except Exception as e:
            return notification_service_pb2.CommonResponse(
                return_code=notification_service_pb2.ReturnStatus.ERROR, return_msg=str(e))

    async def _delete_client(self, request):
        self.storage.delete_client(request.client_id)
        return notification_service_pb2.CommonResponse(
            return_code=notification_service_pb2.ReturnStatus.SUCCESS,
            return_msg='')

    @asyncio.coroutine
    def isClientExists(self, request, context):
        try:
            return self._is_client_exists(request)
        except Exception as e:
            return notification_service_pb2.isClientExistsResponse(
                return_code=notification_service_pb2.ReturnStatus.ERROR, return_msg=str(e), is_exists=False)

    async def _is_client_exists(self, request):
        is_exists = self.storage.is_client_exists(request.client_id)
        return notification_service_pb2.isClientExistsResponse(
            return_code=notification_service_pb2.ReturnStatus.SUCCESS,
            return_msg='',
            is_exists=is_exists)


class HighAvailableNotificationService(NotificationService):

    def __init__(self,
                 storage,
                 ha_manager,
                 server_uri,
                 ha_storage,
                 ttl_ms: int = 10000,
                 min_notify_interval_ms: int = 100):
        super(HighAvailableNotificationService, self).__init__(storage)
        self.server_uri = server_uri
        self.ha_storage = ha_storage
        self.ttl_ms = ttl_ms
        self.min_notify_interval_ms = min_notify_interval_ms
        self.ha_manager = ha_manager  # type: NotificationServerHaManager
        self.member_updated_condition = asyncio.Condition()

    def start(self):
        self.ha_manager.start(self.server_uri,
                              self.ha_storage,
                              self.ttl_ms,
                              self.min_notify_interval_ms,
                              self.member_updated_condition)

    def stop(self):
        self.ha_manager.stop()

    async def _send_event(self, request):
        response = await super(HighAvailableNotificationService, self)._send_event(request)
        try:
            if response.return_code == notification_service_pb2.ReturnStatus.SUCCESS:
                self.ha_manager.notify_others(event_proto_to_event(response.event))
        finally:
            return response

    async def _list_members(self, request):
        timeout_seconds = request.timeout_seconds
        if 0 == timeout_seconds:
            return notification_service_pb2.ListMembersResponse(
                return_code=notification_service_pb2.ReturnStatus.SUCCESS,
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
            return notification_service_pb2.ListMembersResponse(
                return_code=notification_service_pb2.ReturnStatus.SUCCESS,
                return_msg='',
                members=[member_to_proto(member) for member in members])

    async def _notify_new_member(self, request):
        self.ha_manager.add_living_member(proto_to_member(request.member))
        async with self.member_updated_condition:
            self.member_updated_condition.notify_all()
        return notification_service_pb2.CommonResponse(
            return_code=notification_service_pb2.ReturnStatus.SUCCESS,
            return_msg='')
