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
from notification_service.base_notification import EventWatcher, BaseEvent, UNDEFINED_EVENT_TYPE
from ai_flow.client.ai_flow_client import get_ai_flow_client


def send_event(key: str, value: str, event_type: str = UNDEFINED_EVENT_TYPE):
    """
    Send event to Notification Service.

    :param event_type: the event type.
    :param key: Key of events updated in Notification Service.
    :param value: Value of events updated in Notification Service.
    :return: A single object of :py:class:`notification_service.base_notification.BaseEvent`
    created in notification service.
    """
    return get_ai_flow_client().send_event(BaseEvent(key=key, value=value, event_type=event_type))


def list_events(key: str, version: int = None) -> list:
    """
    List specific `key` or `version` events in Notification Service.

    :param key: Key of event for listening.
    :param version: (Optional) Version of event for listening.
    """
    return get_ai_flow_client().list_events(key=key, version=version)


def start_listen_event(key: str, watcher: EventWatcher, version=None):
    """
    Start listen specific `key` or `version` events in Notification Service.

    :param key: Key of event for listening.
    :param watcher: Watcher instance for listening notification.
    :param version: (Optional) Version of event for listening.
    """
    get_ai_flow_client().start_listen_event(key=key, watcher=watcher, version=version)


def stop_listen_event(key: str = None):
    """
    Stop listen specific `key` events in Notification Service.
    :param key: Key of event for listening.
    """
    get_ai_flow_client().stop_listen_event(key=key)
