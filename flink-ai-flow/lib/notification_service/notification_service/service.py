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
from notification_service.event_storage import BaseEventStorage
from notification_service.proto import notification_service_pb2_grpc, notification_service_pb2
from notification_service.utils import event_to_proto, event_list_to_proto


class NotificationService(notification_service_pb2_grpc.NotificationServiceServicer):

    def __init__(self, storage: BaseEventStorage):
        self.storage = storage
        self.notification_conditions = {}
        self.lock = asyncio.Lock()
        self.write_condition = asyncio.Condition()

    @asyncio.coroutine
    def sendEvent(self, request, context):
        try:
            return self._send_event(request)
        except Exception as e:
            print(e)
            traceback.print_stack()
            return notification_service_pb2.SendEventsResponse(
                return_code=str(notification_service_pb2.ReturnStatus.ERROR), return_msg=str(e))

    async def _send_event(self, request):
        event_proto = request.event
        event = BaseEvent(key=event_proto.key, value=event_proto.value, event_type=event_proto.event_type)
        key = event.key
        # Lock conditions dict for get/check/update of key
        await self.lock.acquire()
        if self.notification_conditions.get(key) is None:
            self.notification_conditions.update({(key, asyncio.Condition())})
        # Release lock after check/update key of notification conditions dict
        self.lock.release()
        async with self.notification_conditions.get(key), self.write_condition:
            event: BaseEvent = self.storage.add_event(event)
            self.notification_conditions.get(key).notify_all()
            self.write_condition.notify_all()

        result_event_proto = event_to_proto(event)
        return notification_service_pb2.SendEventsResponse(event=result_event_proto,
                                                           return_code=str(notification_service_pb2.ReturnStatus.SUCCESS),
                                                           return_msg='')

    @asyncio.coroutine
    def listEvents(self, request, context):
        try:
            return self._list_events(request)
        except Exception as e:
            return notification_service_pb2.ListEventsResponse(
                return_code=str(notification_service_pb2.ReturnStatus.ERROR), return_msg=str(e))

    async def _list_events(self, request):
        event_proto = request.event
        key = event_proto.key
        version = event_proto.version
        timeout_seconds = request.timeout_seconds

        if timeout_seconds == 0:
            event_models = self._query_events(key, version)
            event_proto_list = event_list_to_proto(event_models)
            return notification_service_pb2.ListEventsResponse(
                return_code=str(notification_service_pb2.ReturnStatus.SUCCESS),
                return_msg='',
                events=event_proto_list)
        else:
            start = time.time()
            # Lock conditions dict for get/check/update of key
            await self.lock.acquire()
            if self.notification_conditions.get(key) is None:
                self.notification_conditions.update({(key, asyncio.Condition())})
            # Release lock after check/update key of notification conditions dict
            self.lock.release()
            event_models = self._query_events(key, version)
            async with self.notification_conditions.get(key):
                while time.time() - start < timeout_seconds and len(event_models) == 0:
                    try:
                        await asyncio.wait_for(self.notification_conditions.get(key).wait(),
                                               timeout_seconds - time.time() + start)
                        event_models = self._query_events(key, version)
                    except asyncio.TimeoutError:
                        pass
            event_proto_list = event_list_to_proto(event_models)
            return notification_service_pb2.ListEventsResponse(
                return_code=str(notification_service_pb2.ReturnStatus.SUCCESS),
                return_msg='',
                events=event_proto_list)

    def _query_events(self, key, version):
        if version is None:
            version = 0
        return self.storage.list_events(key=key, version=version)

    @asyncio.coroutine
    def listAllEvents(self, request, context):
        try:
            return self._list_all_events(request)
        except Exception as e:
            return notification_service_pb2.ListEventsResponse(
                return_code=str(notification_service_pb2.ReturnStatus.ERROR), return_msg=str(e))

    async def _list_all_events(self, request):
        start_time = request.start_time
        timeout_seconds = request.timeout_seconds
        if 0 == timeout_seconds:
            event_models = self._query_all_events(start_time)
            event_proto_list = event_list_to_proto(event_models)
            return notification_service_pb2.ListEventsResponse(
                return_code=str(notification_service_pb2.ReturnStatus.SUCCESS),
                return_msg='',
                events=event_proto_list)
        else:
            start = time.time()
            event_models = self._query_all_events(start_time)
            async with self.write_condition:
                while time.time() - start < timeout_seconds and len(event_models) == 0:
                    try:
                        await asyncio.wait_for(self.write_condition.wait(), timeout_seconds - time.time() + start)
                        event_models = self._query_all_events(start_time=start_time)
                    except asyncio.TimeoutError:
                        pass
            event_proto_list = event_list_to_proto(event_models)
            return notification_service_pb2.ListEventsResponse(
                return_code=str(notification_service_pb2.ReturnStatus.SUCCESS),
                return_msg='',
                events=event_proto_list)

    def _query_all_events(self, start_time):
        return self.storage.list_all_events(start_time)

    @asyncio.coroutine
    def listEventsFromId(self, request, context):
        try:
            return self._list_events_by_id(request)
        except Exception as e:
            return notification_service_pb2.ListEventsResponse(
                return_code=str(notification_service_pb2.ReturnStatus.ERROR), return_msg=str(e))

    async def _list_events_by_id(self, request):
        id = request.id
        timeout_seconds = request.timeout_seconds
        if 0 == timeout_seconds:
            event_models = self._query_all_events_by_id(id)
            event_proto_list = event_list_to_proto(event_models)
            return notification_service_pb2.ListEventsResponse(
                return_code=str(notification_service_pb2.ReturnStatus.SUCCESS),
                return_msg='',
                events=event_proto_list)
        else:
            start = time.time()
            event_models = self._query_all_events_by_id(id)
            async with self.write_condition:
                while time.time() - start < timeout_seconds and len(event_models) == 0:
                    try:
                        await asyncio.wait_for(self.write_condition.wait(), timeout_seconds - time.time() + start)
                        event_models = self._query_all_events_by_id(id)
                    except asyncio.TimeoutError:
                        pass
            event_proto_list = event_list_to_proto(event_models)
            return notification_service_pb2.ListEventsResponse(
                return_code=str(notification_service_pb2.ReturnStatus.SUCCESS),
                return_msg='',
                events=event_proto_list)

    def _query_all_events_by_id(self, id):
        return self.storage.list_all_events_from_id(id)
