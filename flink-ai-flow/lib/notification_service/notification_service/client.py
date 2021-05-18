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
import logging
import os
import threading
import time
import uuid
from collections import Iterable
from functools import wraps
from random import shuffle
from typing import Union, List, Tuple, Dict, Any

import grpc

from notification_service.base_notification import BaseNotification, EventWatcher, BaseEvent, EventWatcherHandle, \
    ANY_CONDITION
from notification_service.proto import notification_service_pb2_grpc
from notification_service.proto.notification_service_pb2 \
    import SendEventRequest, ListEventsRequest, EventProto, ReturnStatus, ListAllEventsRequest, \
    GetLatestVersionByKeyRequest, ListMembersRequest
from notification_service.util.utils import event_proto_to_event, proto_to_member, sleep_and_detecting_running

if not hasattr(time, 'time_ns'):
    time.time_ns = lambda: int(time.time() * 1e9)

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

    def __init__(self,
                 server_uri: str,
                 default_namespace: str = None,
                 enable_ha: bool = False,
                 list_member_interval_ms: int = 5000,
                 retry_interval_ms: int = 1000,
                 retry_timeout_ms: int = 10000,
                 sender: str = None):
        """
        The constructor of the NotificationClient.

        :param server_uri: Target server uri/uris. If `enable_ha` is True, multiple uris separated
                           by "," can be accepted.
        :param default_namespace: The default namespace that this client is working on.
        :param enable_ha: Enable high-available functionality.
        :param list_member_interval_ms: When `enable_ha` is True, this client will request the
                                        living members periodically. A member means a server node
                                        of the Notification server cluster. This param specifies
                                        the interval of the listing member requests.
        :param retry_interval_ms: When `enable_ha` is True and a rpc call has failed on all the
                                  living members, this client will retry until success or timeout.
                                  This param specifies the retry interval.

        :param retry_timeout_ms: When `enable_ha` is True and a rpc call has failed on all the
                                 living members, this client will retry until success or timeout.
                                 This param specifies the retry timeout.
        :param sender: The identify of the client.
        """
        channel = grpc.insecure_channel(server_uri)
        self._default_namespace = default_namespace
        self.notification_stub = notification_service_pb2_grpc.NotificationServiceStub(channel)
        self.threads = {}  # type: Dict[Any, List[threading.Thread]]
        self.lock = threading.Lock()
        self.enable_ha = enable_ha
        self.list_member_interval_ms = list_member_interval_ms
        self.retry_interval_ms = retry_interval_ms
        self.retry_timeout_ms = retry_timeout_ms
        self._sender = sender
        if self.enable_ha:
            server_uris = server_uri.split(",")
            self.living_members = []
            self.current_uri = None
            last_error = None
            for server_uri in server_uris:
                channel = grpc.insecure_channel(server_uri)
                notification_stub = notification_service_pb2_grpc.NotificationServiceStub(channel)
                try:
                    request = ListMembersRequest(timeout_seconds=0)
                    response = notification_stub.listMembers(request)
                    if response.return_code == ReturnStatus.SUCCESS:
                        self.living_members = [proto_to_member(proto).server_uri
                                               for proto in response.members]
                    else:
                        raise Exception(response.return_msg)
                    self.current_uri = server_uri
                    self.notification_stub = notification_stub
                    break
                except grpc.RpcError as e:
                    last_error = e
            if self.current_uri is None:
                raise Exception("No available server uri!") from last_error
            self.ha_change_lock = threading.Lock()
            self.ha_running = True
            self.notification_stub = self._wrap_rpcs(self.notification_stub, server_uri)
            self.list_member_thread = threading.Thread(target=self._list_members, daemon=True)
            self.list_member_thread.start()

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
                namespace=self._default_namespace,
                sender=self._sender
            ),
            uuid=str(uuid.uuid4()))
        response = self.notification_stub.sendEvent(request)
        if response.return_code == ReturnStatus.SUCCESS:
            return event_proto_to_event(response.event)
        else:
            raise Exception(response.return_msg)

    def list_events(self,
                    key: Union[str, List[str]],
                    namespace: str = None,
                    version: int = None,
                    event_type: str = None,
                    start_time: int = None,
                    sender: str = None) -> List[BaseEvent]:
        """
        List specific events in Notification Service.

        :param key: Key of the event for listening.
        :param namespace: (Optional) Namespace of the event for listening.
        :param version: (Optional) Version of the events must greater than this version.
        :param event_type: (Optional) Type of the events.
        :param start_time: (Optional) Start time of the events.
        :param sender: The event sender.
        :return: The event list.
        """
        if isinstance(key, str):
            key = (key,)
        elif isinstance(key, Iterable):
            key = tuple(key)
        request = ListEventsRequest(
            keys=key,
            start_version=version,
            event_type=event_type,
            start_time=start_time,
            namespace=self._default_namespace if namespace is None else namespace,
            sender=sender
        )
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
                           namespace: str = None,
                           version: int = None,
                           event_type: str = None,
                           start_time: int = None,
                           sender: str = None) -> EventWatcherHandle:
        """
        Start listen specific `key` or `version` notifications in Notification Service.

        :param key: Key of notification for listening.
        :param watcher: Watcher instance for listening.
        :param namespace: (Optional) Namespace of the event for listening.
        :param version: (Optional) The version of the events must greater than this version.
        :param event_type: (Optional) Type of the events for listening.
        :param start_time: (Optional) Start time of the events for listening.
        :param sender: The event sender.
        :return: The handle used to stop the listening.
        """
        if isinstance(key, str):
            key = (key,)
        elif isinstance(key, Iterable):
            key = tuple(key)
        namespace = self._default_namespace if namespace is None else namespace
        sender = ANY_CONDITION if sender is None else sender
        event_type = ANY_CONDITION if event_type is None else event_type

        def list_events(client,
                        k: Tuple[str],
                        v: List[int],
                        t: str = None,
                        ts: int = None,
                        ns: str = None,
                        sd: str = None,
                        timeout_seconds: int = None):
            request = ListEventsRequest(
                keys=k,
                event_type=t,
                start_time=ts,
                start_version=v,
                timeout_seconds=timeout_seconds,
                namespace=ns,
                sender=sd
            )
            response = client.notification_stub.listEvents(request)
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

        def listen(client, k, v, t, ts, ns, sd, w):
            th = threading.current_thread()
            listen_version = v
            while getattr(th, '_flag', True):
                notifications = list_events(
                    client,
                    k,
                    listen_version,
                    t,
                    ts,
                    ns,
                    sd,
                    NOTIFICATION_TIMEOUT_SECONDS)
                if len(notifications) > 0:
                    w.process(notifications)
                    listen_version = notifications[len(notifications) - 1].version

        thread = threading.Thread(
            target=listen,
            args=(self, key, version, event_type, start_time, namespace, sender,
                  watcher),
            daemon=True)
        thread.start()
        self.lock.acquire()
        try:
            if self.threads.get((key, namespace, event_type, sender)) is None:
                self.threads[(key, namespace, event_type, sender)] = []
            self.threads[(key, namespace, event_type, sender)].append(thread)
        finally:
            self.lock.release()
        return ThreadEventWatcherHandle(thread, (key, namespace, event_type, sender), self)

    def stop_listen_event(self, key: Union[str, Tuple[str]] = None,
                          namespace: str = None,
                          event_type: str = None,
                          sender: str = None):
        """
        Stop listen specific `key` notifications in Notification Service.

        :param key: Keys of notification for listening.
        :param namespace: (Optional) Namespace of notification for listening.
        :param event_type: (Optional) Type of the events for listening.
        :param sender: The event sender.
        """
        namespace = self._default_namespace if namespace is None else namespace
        event_type = ANY_CONDITION if event_type is None else event_type
        sender = ANY_CONDITION if sender is None else sender
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
                key = (key,)
            try:
                if (key, namespace, event_type, sender) in self.threads:
                    threads = self.threads[(key, namespace, event_type, sender)]
                    for thread in threads:
                        thread._flag = False
                        thread.join()
                    del self.threads[(key, namespace, event_type, sender)]
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

        def list_events(client, start, timeout_seconds: int = None):
            request = ListAllEventsRequest(start_time=start, timeout_seconds=timeout_seconds)
            response = client.notification_stub.listAllEvents(request)
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

        def list_events_from_version(client, v, timeout_seconds: int = None):
            request = ListAllEventsRequest(start_version=v, timeout_seconds=timeout_seconds)
            response = client.notification_stub.listAllEvents(request)
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

        def listen(client, s, v, w):
            t = threading.current_thread()
            flag = True if v is None else False
            current_version = 0 if v is None else v
            while getattr(t, '_flag', True):
                if flag:
                    notifications = list_events(client, s, NOTIFICATION_TIMEOUT_SECONDS)
                    if len(notifications) > 0:
                        w.process(notifications)
                        current_version = notifications[len(notifications) - 1].version
                        flag = False
                else:
                    notifications = list_events_from_version(client,
                                                             current_version,
                                                             NOTIFICATION_TIMEOUT_SECONDS)
                    if len(notifications) > 0:
                        w.process(notifications)
                        current_version = notifications[len(notifications) - 1].version

        thread = threading.Thread(target=listen,
                                  args=(self, start_time, version, watcher),
                                  daemon=True)
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

    def get_latest_version(self, key: str = None, namespace: str = None):
        """
        get latest event's version by key.
        :param key: (Optional) Key of notification for listening.
        :param namespace: (Optional) Namespace of notification for listening.
        :return: Version number of the specific key.
        """
        self.lock.acquire()
        try:
            request = GetLatestVersionByKeyRequest(key=key,
                                                   namespace=self._default_namespace if namespace is None else namespace)
            response = self.notification_stub.getLatestVersionByKey(request)
            if response.return_code == str(ReturnStatus.SUCCESS):
                return response.version
        finally:
            self.lock.release()

    def disable_high_availability(self):
        if hasattr(self, "ha_running"):
            self.ha_running = False
            self.list_member_thread.join()

    def _list_members(self):
        while self.ha_running:
            # refresh the living members
            request = ListMembersRequest(timeout_seconds=int(self.list_member_interval_ms / 1000))
            response = self.notification_stub.listMembers(request)
            if response.return_code == ReturnStatus.SUCCESS:
                with self.ha_change_lock:
                    self.living_members = [proto_to_member(proto).server_uri
                                           for proto in response.members]
            else:
                logging.error("Exception thrown when updating the living members: %s" %
                              response.return_msg)

    def _ha_wrapper(self, func):
        @wraps(func)
        def call_with_retry(*args, **kwargs):
            current_func = getattr(self.notification_stub,
                                   func.__name__).inner_func
            start_time = time.time_ns() / 1000000
            failed_members = set()
            while True:
                try:
                    return current_func(*args, **kwargs)
                except grpc.RpcError:
                    logging.error("Exception thrown when calling rpc, change the connection.",
                                  exc_info=True)
                    with self.ha_change_lock:
                        # check the current_uri to ensure thread safety
                        if current_func.server_uri == self.current_uri:
                            living_members = list(self.living_members)
                            failed_members.add(self.current_uri)
                            shuffle(living_members)
                            found_new_member = False
                            for server_uri in living_members:
                                if server_uri in failed_members:
                                    continue
                                next_uri = server_uri
                                channel = grpc.insecure_channel(next_uri)
                                notification_stub = self._wrap_rpcs(
                                    notification_service_pb2_grpc.NotificationServiceStub(channel),
                                    next_uri)
                                self.notification_stub = notification_stub
                                current_func = getattr(self.notification_stub,
                                                       current_func.__name__).inner_func
                                self.current_uri = next_uri
                                found_new_member = True
                            if not found_new_member:
                                logging.error("No available living members currently. Sleep and retry.")
                                failed_members.clear()
                                sleep_and_detecting_running(self.retry_interval_ms,
                                                            lambda: self.ha_running)

                # break if stopped or timeout
                if not self.ha_running or \
                        time.time_ns() / 1000000 > start_time + self.retry_timeout_ms:
                    if not self.ha_running:
                        raise Exception("HA has been disabled.")
                    else:
                        raise Exception("Rpc retry timeout!")

        call_with_retry.inner_func = func
        return call_with_retry

    def _wrap_rpcs(self, stub, server_uri):
        for method_name, method in dict(stub.__dict__).items():
            method.__name__ = method_name
            method.server_uri = server_uri
            setattr(stub, method_name, self._ha_wrapper(method))
        return stub
