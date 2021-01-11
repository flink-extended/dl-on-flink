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
import uuid
from collections import Iterable
from typing import Union, List, Tuple, Dict, Any

import grpc
import time

from notification_service.base_notification import BaseNotification, EventWatcher, BaseEvent, EventWatcherHandle
from notification_service.proto.notification_service_pb2 \
    import SendEventRequest, ListEventsRequest, EventProto, ReturnStatus, ListAllEventsRequest, \
    GetLatestVersionByKeyRequest
from notification_service.proto import notification_service_pb2_grpc
from notification_service.proto.notification_service_pb2_grpc import NotificationServiceStub
from notification_service.util.utils import event_proto_to_event

NOTIFICATION_TIMEOUT_SECONDS = os.environ.get("NOTIFICATION_TIMEOUT_SECONDS", 5)
ALL_EVENTS_KEY = "_*"


class ThreadEventWatcherHandle(EventWatcherHandle):

    def __init__(self,
                 thread: threading.Thread,
                 thread_key: Any,
                 notification_client: 'NotificationClient'):
        self._thread = thread
        self._thread_key = thread_key
        self._notification_client = notification_client

    def stop(self):
        self._thread._flag = False
        self._thread.join()
        self._notification_client.lock.acquire()
        try:
            self._notification_client.threads[self._thread_key].remove(self._thread)
        finally:
            self._notification_client.lock.release()


class NotificationClient(BaseNotification):
    """
    NotificationClient is the notification client.
    """

    def __init__(self, server_uri, default_namespace: str = None):
        channel = grpc.insecure_channel(server_uri)
        self._default_namespace = default_namespace
        self.notification_stub = notification_service_pb2_grpc.NotificationServiceStub(channel)
        self.threads = {}  # type: Dict[Any, List[threading.Thread]]
        self.lock = threading.Lock()

    def send_event(self, event: BaseEvent):
        """
        Send event to Notification Service.

        :param event: the event updated.
        :return: The created event which has version and create time.
        """
        request = SendEventRequest(
            event=EventProto(
                key=event.key,
                value=event.value,
                event_type=event.event_type,
                context=event.context,
                namespace=self._default_namespace),
            uuid=str(uuid.uuid4()))
        response = self.notification_stub.sendEvent(request)
        if response.return_code == ReturnStatus.SUCCESS:
            return event_proto_to_event(response.event)
        else:
            raise Exception(response.return_msg)

    def list_events(self,
                    key: Union[str, List[str]],
                    version: int = None,
                    event_type: str = None,
                    start_time: int = None) -> List[BaseEvent]:
        """
        List specific events in Notification Service.

        :param key: Key of the event for listening.
        :param version: (Optional) The version of the events must greater than this version.
        :param event_type: (Optional) Type of the events.
        :param start_time: (Optional) Start time of the events.
        :return: The event list.
        """
        if isinstance(key, str):
            key = (key, )
        elif isinstance(key, Iterable):
            key = tuple(key)
        request = ListEventsRequest(
            keys=key,
            start_version=version,
            event_type=event_type,
            start_time=start_time,
            namespace=self._default_namespace)
        response = self.notification_stub.listEvents(request)
        if response.return_code == ReturnStatus.SUCCESS:
            if response.events is None:
                return []
            else:
                events = []
                for event_proto in response.events:
                    event = event_proto_to_event(event_proto)
                    events.append(event)
                return events
        else:
            raise Exception(response.return_msg)

    def start_listen_event(self,
                           key: Union[str, Tuple[str]],
                           watcher: EventWatcher,
                           version: int = None,
                           event_type: str = None,
                           start_time: int = None) -> EventWatcherHandle:
        """
        Start listen specific `key` or `version` notifications in Notification Service.

        :param key: Key of notification for listening.
        :param watcher: Watcher instance for listening.
        :param version: (Optional) The version of the events must greater than this version.
        :param event_type: (Optional) Type of the events for listening.
        :param start_time: (Optional) Start time of the events for listening.
        :return: The handle used to stop the listening.
        """
        if isinstance(key, str):
            key = (key, )
        elif isinstance(key, Iterable):
            key = tuple(key)
        namespace = self._default_namespace

        def list_events(stub: NotificationServiceStub,
                        k: Tuple[str],
                        v: List[int],
                        t: str = None,
                        ts: int = None,
                        ns: str = None,
                        timeout_seconds: int = None):
            request = ListEventsRequest(
                keys=k,
                event_type=t,
                start_time=ts,
                start_version=v,
                timeout_seconds=timeout_seconds,
                namespace=ns)
            response = stub.listEvents(request)
            if response.return_code == ReturnStatus.SUCCESS:
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

        def listen(stub, k, v, t, ts, ns, w):
            th = threading.current_thread()
            listen_version = v
            while getattr(th, '_flag', True):
                notifications = list_events(
                    stub,
                    k,
                    listen_version,
                    t,
                    ts,
                    ns,
                    NOTIFICATION_TIMEOUT_SECONDS)
                if len(notifications) > 0:
                    w.process(notifications)
                    listen_version = notifications[len(notifications) - 1].version

        thread = threading.Thread(
            target=listen,
            args=(self.notification_stub, key, version, event_type, start_time, namespace,
                  watcher))
        thread.start()
        self.lock.acquire()
        try:
            if self.threads.get((key, namespace)) is None:
                self.threads[(key, namespace)] = []
            self.threads[(key, namespace)].append(thread)
        finally:
            self.lock.release()
        return ThreadEventWatcherHandle(thread, (key, namespace), self)

    def stop_listen_event(self, key: Union[str, Tuple[str]] = None):
        """
        Stop listen specific `key` notifications in Notification Service.

        :param key: Keys of notification for listening.
        """
        namespace = self._default_namespace
        if key is None:
            for (thread_key, v) in self.threads.items():
                if thread_key == ALL_EVENTS_KEY:
                    # do not stop the global listen threads,
                    # which are controlled by `stop_listen_events`.
                    continue
                threads = self.threads[thread_key]
                for thread in threads:
                    thread._flag = False
                    thread.join()
            self.threads.clear()
        else:
            self.lock.acquire()
            if isinstance(key, str):
                key = (key, )
            try:
                if (key, namespace) in self.threads:
                    threads = self.threads[(key, namespace)]
                    for thread in threads:
                        thread._flag = False
                        thread.join()
                    del self.threads[(key, namespace)]
            finally:
                self.lock.release()

    def list_all_events(self,
                        start_time: int = None,
                        start_version: int = None,
                        end_version: int = None) -> List[BaseEvent]:
        """
        List specific `key` or `version` of events in Notification Service.

        :param start_time: (Optional) Start time of the events.
        :param start_version: (Optional) the version of the events must greater than the
                              start_version.
        :param end_version: (Optional) the version of the events must equal or less than the
                            end_version.
        :return: The event list.
        """
        request = ListAllEventsRequest(start_time=start_time,
                                       start_version=start_version,
                                       end_version=end_version)
        response = self.notification_stub.listAllEvents(request)
        if response.return_code == ReturnStatus.SUCCESS:
            if response.events is None:
                return []
            else:
                events = []
                for event_proto in response.events:
                    event = event_proto_to_event(event_proto)
                    events.append(event)
                return events
        else:
            raise Exception(response.return_msg)

    def start_listen_events(self,
                            watcher: EventWatcher,
                            start_time=int(time.time() * 1000),
                            version: int = None) -> EventWatcherHandle:
        """
        Start listen all events.

        :param watcher: process event.
        :param start_time: (Optional) the earliest event time.
        :param version: (Optional) the start version of the event.
        :return: The handle used to stop the listening.
        """
        if ALL_EVENTS_KEY in self.threads:
            raise Exception("already listen events, must stop first!")

        def list_events(stub: NotificationServiceStub, start, timeout_seconds: int = None):
            request = ListAllEventsRequest(start_time=start, timeout_seconds=timeout_seconds)
            response = stub.listAllEvents(request)
            if response.return_code == ReturnStatus.SUCCESS:
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

        def list_events_from_version(stub: NotificationServiceStub, v, timeout_seconds: int = None):
            request = ListAllEventsRequest(start_version=v, timeout_seconds=timeout_seconds)
            response = stub.listAllEvents(request)
            if response.return_code == ReturnStatus.SUCCESS:
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

        def listen(stub, s, v, w):
            t = threading.current_thread()
            flag = True if v is None else False
            current_version = 0 if v is None else v
            while getattr(t, '_flag', True):
                if flag:
                    notifications = list_events(stub, s, NOTIFICATION_TIMEOUT_SECONDS)
                    if len(notifications) > 0:
                        w.process(notifications)
                        current_version = notifications[len(notifications) - 1].version
                        flag = False
                else:
                    notifications = list_events_from_version(stub,
                                                             current_version,
                                                             NOTIFICATION_TIMEOUT_SECONDS)
                    if len(notifications) > 0:
                        w.process(notifications)
                        current_version = notifications[len(notifications) - 1].version

        thread = threading.Thread(target=listen,
                                  args=(self.notification_stub, start_time, version, watcher))
        thread.start()
        self.lock.acquire()
        try:
            if self.threads.get(ALL_EVENTS_KEY) is None:
                self.threads[ALL_EVENTS_KEY] = []
            self.threads[ALL_EVENTS_KEY].append(thread)
        finally:
            self.lock.release()
        return ThreadEventWatcherHandle(thread, ALL_EVENTS_KEY, self)

    def stop_listen_events(self):
        """
        Stop the global listening threads.
        """
        self.lock.acquire()
        try:
            if ALL_EVENTS_KEY in self.threads:
                threads = self.threads[ALL_EVENTS_KEY]
                for thread in threads:
                    thread._flag = False
                    thread.join()
                del self.threads[ALL_EVENTS_KEY]
        finally:
            self.lock.release()

    def get_latest_version(self, key: str = None):
        """
        get latest event's version by key.
        :param key: Key of notification for listening.
        :return: Version number of the specific key.
        """
        self.lock.acquire()
        try:
            request = GetLatestVersionByKeyRequest(key=key)
            response = self.notification_stub.getLatestVersionByKey(request)
            if response.return_code == str(ReturnStatus.SUCCESS):
                return response.version
        finally:
            self.lock.release()
