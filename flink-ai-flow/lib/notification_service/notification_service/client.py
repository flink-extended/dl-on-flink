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
import threading
import os
import grpc
import time

from notification_service.base_notification import BaseNotification, EventWatcher, BaseEvent
from notification_service.proto.notification_service_pb2 \
    import SendEventRequest, ListEventsRequest, EventProto, ReturnStatus, ListAllEventsRequest, \
        ListEventsFromIdRequest, GetLatestVersionByKeyRequest
from notification_service.proto import notification_service_pb2_grpc
from notification_service.proto.notification_service_pb2_grpc import NotificationServiceStub
from notification_service.utils import event_proto_to_event

NOTIFICATION_TIMEOUT_SECONDS = os.environ.get("NOTIFICATION_TIMEOUT_SECONDS", 5)
ALL_EVENTS_KEY = "_*"


class NotificationClient(BaseNotification):
    """
    NotificationClient is the notification client.
    """

    def __init__(self, server_uri):
        channel = grpc.insecure_channel(server_uri)
        self.notification_stub = notification_service_pb2_grpc.NotificationServiceStub(channel)
        self.threads = {}
        self.lock = threading.Lock()

    def send_event(self, event: BaseEvent) -> BaseEvent:
        """
        Send event to Notification
        :param event: the event updated.
        :return: A single object of notification created in Notification.
        """
        request = SendEventRequest(
            event=EventProto(key=event.key, value=event.value, event_type=event.event_type))
        response = self.notification_stub.sendEvent(request)
        if response.return_code == str(ReturnStatus.SUCCESS):
            if response.event is None:
                return None
            else:
                return event_proto_to_event(response.event)
        else:
            raise Exception(response.return_msg)

    def list_events(self, key: str, version: int = None) -> list:
        """
        List specific `key` or `version` of events in Notification Service.
        :param key: Key of the event for listening.
        :param version: (Optional) Version of the signal for listening.
        :return: Specific `key` or `version` event notification list.
        """
        request = ListEventsRequest(
            event=EventProto(key=key, version=version))
        response = self.notification_stub.listEvents(request)
        if response.return_code == str(ReturnStatus.SUCCESS):
            if response.events is None:
                return None
            else:
                events = []
                for event_proto in response.events:
                    event = event_proto_to_event(event_proto)
                    events.append(event)
                return events
        else:
            raise Exception(response.return_msg)

    def start_listen_event(self, key: str, watcher: EventWatcher, version: int = None):
        """
        Start listen specific `key` or `version` notifications in Notification Service.

        :param key: Key of notification for listening.
        :param watcher: Watcher instance for listening notification.
        :param version: (Optional) Version of notification for listening.
        """

        def list_events(stub: NotificationServiceStub, k: str, v: int, timeout_seconds: int = None):
            request = ListEventsRequest(
                event=EventProto(key=k, version=v), timeout_seconds=timeout_seconds)
            response = stub.listEvents(request)
            if response.return_code == str(ReturnStatus.SUCCESS):
                if response.events is None:
                    return None
                else:
                    events = []
                    for event_proto in response.events:
                        event = event_proto_to_event(event_proto)
                        events.append(event)
                    return events
            else:
                raise Exception(response.return_msg)

        def listen(stub, k, v, w):
            t = threading.current_thread()
            listen_version = v
            while getattr(t, '_flag', True):
                notifications = list_events(stub, k, listen_version, NOTIFICATION_TIMEOUT_SECONDS)
                if len(notifications) > 0:
                    w.process(notifications)
                    listen_version = notifications[len(notifications) - 1].version

        if self.threads.get(key) is None:
            thread = threading.Thread(target=listen,
                                      args=(self.notification_stub, key, version, watcher))
            thread.start()
            self.lock.acquire()
            try:
                self.threads[key] = thread
            finally:
                self.lock.release()

    def stop_listen_event(self, key: str = None):
        """
        Stop listen specific `key` notifications in Notification Service.

        :param key: Key of notification for listening.
        """
        if key is None:
            for (k, v) in self.threads.items():
                thread = self.threads[k]
                thread._flag = False
                thread.join()
            self.threads.clear()
        else:
            self.lock.acquire()
            try:
                if key in self.threads:
                    thread = self.threads[key]
                    thread._flag = False
                    thread.join()
                    del self.threads[key]
            finally:
                self.lock.release()

    def list_all_events(self, start_time: int):
        """
        List specific `key` or `version` of events in Notification Service.
        :param start_time: the event after this time.
        :return:
        """
        request = ListAllEventsRequest(start_time=start_time)
        response = self.notification_stub.listAllEvents(request)
        if response.return_code == str(ReturnStatus.SUCCESS):
            if response.events is None:
                return None
            else:
                events = []
                for event_proto in response.events:
                    event = event_proto_to_event(event_proto)
                    events.append(event)
                return events
        else:
            raise Exception(response.return_msg)

    def start_listen_events(self, watcher: EventWatcher, start_time=time.time_ns()):
        """
        start listen all events.
        :param watcher: process event.
        :param start_time: the earliest event time.
        :return:
        """
        if ALL_EVENTS_KEY in self.threads:
            raise Exception("already listen events, must stop first!")

        def list_events(stub: NotificationServiceStub, start, timeout_seconds: int = None):
            request = ListAllEventsRequest(start_time=start, timeout_seconds=timeout_seconds)
            response = stub.listAllEvents(request)
            if response.return_code == str(ReturnStatus.SUCCESS):
                if response.events is None:
                    return None
                else:
                    events = []
                    for event_proto in response.events:
                        event = event_proto_to_event(event_proto)
                        events.append(event)
                    return events
            else:
                raise Exception(response.return_msg)

        def list_events_from_id(stub: NotificationServiceStub, id, timeout_seconds: int = None):
            request = ListEventsFromIdRequest(id=id, timeout_seconds=timeout_seconds)
            response = stub.listEventsFromId(request)
            if response.return_code == str(ReturnStatus.SUCCESS):
                if response.events is None:
                    return None
                else:
                    events = []
                    for event_proto in response.events:
                        event = event_proto_to_event(event_proto)
                        events.append(event)
                    return events
            else:
                raise Exception(response.return_msg)

        def listen(stub, s, w):
            t = threading.current_thread()
            flag = True
            current_id = 0
            while getattr(t, '_flag', True):
                if flag:
                    notifications = list_events(stub, s, NOTIFICATION_TIMEOUT_SECONDS)
                    if len(notifications) > 0:
                        w.process(notifications)
                        current_id = notifications[len(notifications) - 1].id
                        flag = False
                else:
                    notifications = list_events_from_id(stub, current_id, NOTIFICATION_TIMEOUT_SECONDS)
                    if len(notifications) > 0:
                        w.process(notifications)
                        current_id = notifications[len(notifications) - 1].id

        if self.threads.get(ALL_EVENTS_KEY) is None:
            thread = threading.Thread(target=listen,
                                      args=(self.notification_stub, start_time, watcher))
            thread.start()
            self.lock.acquire()
            try:
                self.threads[ALL_EVENTS_KEY] = thread
            finally:
                self.lock.release()

    def stop_listen_events(self):
        """
        stop listen the events
        :return:
        """
        self.lock.acquire()
        try:
            if ALL_EVENTS_KEY in self.threads:
                thread = self.threads[ALL_EVENTS_KEY]
                thread._flag = False
                thread.join()
                del self.threads[ALL_EVENTS_KEY]
        finally:
            self.lock.release()

    def get_latest_version(self, key: str = None):
        """
        get latest event's version by key
        :param key: event's key
        :return: Version number of the specific key
        """
        self.lock.acquire()
        try:
            request = GetLatestVersionByKeyRequest(key=key)
            response = self.notification_stub.getLatestVersionByKey(request)
            if response.return_code == str(ReturnStatus.SUCCESS):
                return response.version
        finally:
            self.lock.release()
