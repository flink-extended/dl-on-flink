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
import abc
import time

from typing import List, Union, Tuple

UNDEFINED_EVENT_TYPE = "UNDEFINED"
ANY_CONDITION = "*"
DEFAULT_NAMESPACE = "default"


class BaseEvent(object):
    def __init__(self,
                 key: str,
                 value: str,
                 event_type: str = UNDEFINED_EVENT_TYPE,
                 version: int = None,
                 create_time: int = None,
                 context: str = None,
                 namespace: str = None,
                 sender: str = None):
        self.key = key
        self.value = value
        self.event_type = event_type
        self.version = version
        self.create_time = create_time
        self.context = context
        self.namespace = namespace
        self.sender = sender

    def __str__(self) -> str:
        return 'key:{0}, value:{1}, type:{2}, version:{3}, create_time:{4}, ' \
               'context: {5}, namespace: {6}, sender: {7}' \
            .format(self.key, self.value, self.event_type, self.version, self.create_time,
                    self.context, self.namespace, self.sender)

    def __eq__(self, other):
        if not isinstance(other, BaseEvent):
            return False
        return self.key == other.key and \
            self.value == other.value and \
            self.event_type == other.event_type and \
            self.version == other.version and \
            self.create_time == other.create_time and \
            self.context == other.context and \
            self.namespace == other.namespace and \
            self.sender == other.sender


class EventWatcher(metaclass=abc.ABCMeta):
    """
    SignalWatcher is used to represent a standard event handler, which defines the
    logic related to signal notifications.
    """

    @abc.abstractmethod
    def process(self, events: List[BaseEvent]):
        pass


class EventWatcherHandle(metaclass=abc.ABCMeta):
    """
    The EventWatcherHandle used to stop the relevant watch thread.
    """

    @abc.abstractmethod
    def stop(self):
        pass


class BaseNotification(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def send_event(self, event: BaseEvent):
        """
        Send event to Notification Service.

        :param event: the event updated.
        :return: The created event which has version and create time.
        """
        pass

    @abc.abstractmethod
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
        :param namespace: Namespace of the event for listening.
        :param version: (Optional) The version of the events must greater than this version.
        :param event_type: (Optional) Type of the events.
        :param start_time: (Optional) Start time of the events.
        :param sender: The event sender.
        :return: The event list.
        """
        pass

    @abc.abstractmethod
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
        :param namespace: Namespace of the event for listening.
        :param watcher: Watcher instance for listening.
        :param version: (Optional) The version of the events must greater than this version.
        :param event_type: (Optional) Type of the events for listening.
        :param start_time: (Optional) Start time of the events for listening.
        :param sender: The event sender.
        :return: The handle used to stop the listening.
        """
        pass

    @abc.abstractmethod
    def stop_listen_event(self, key: Union[str, Tuple[str]] = None,
                          namespace: str = None,
                          event_type: str = None,
                          sender: str = None
                          ):
        """
        Stop listen specific `key` notifications in Notification Service.

        :param key: Keys of notification for listening.
        :param namespace: Namespace of notification for listening.
        :param event_type: (Optional) Type of the events for listening.
        :param sender: The event sender.
        """
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    def stop_listen_events(self):
        """
        Stop the global listening threads.
        """
        pass

    @abc.abstractmethod
    def get_latest_version(self, key: str = None, namespace: str = None):
        """
        get latest event's version by key.
        :param key: Key of notification for listening.
        :param namespace: Namespace of notification for listening.
        :return: Version number of the specific key.
        """
        pass


class Member(object):

    def __init__(self, version, server_uri, update_time):
        self.version = version
        self.server_uri = server_uri
        self.update_time = update_time
