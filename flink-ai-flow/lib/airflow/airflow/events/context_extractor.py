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
from typing import Optional, Text, Set

from notification_service.base_notification import BaseEvent

DAG_RUN_DEFAULT_CONTEXT = 'default'


class EventContext(object):
    """
    The context of the event returns by ContextExtractor.
    """

    def is_broadcast(self) -> bool:
        """
        :return: Whether the event should be broadcast.
        """
        raise NotImplementedError()

    def get_contexts(self) -> Set[Text]:
        """
        :return: A set of contexts the event belongs to.
        """
        raise NotImplementedError()


class Broadcast(EventContext):
    """
    This class indicates that the event should be broadcast.
    """

    def is_broadcast(self) -> bool:
        return True

    def get_contexts(self) -> Set[Text]:
        return set()


class ContextList(EventContext):
    """
    A set of context the event belongs to.

    Note: 'default' is a reserved key word for default context.
    """

    def __init__(self):
        self._contexts: Set[Text] = set()

    def is_broadcast(self) -> bool:
        return False

    def get_contexts(self) -> Set[Text]:
        return self._contexts

    def add_context(self, context: Text):
        self._contexts.add(context)


class ContextExtractor(object):
    """
    ContextExtractor can be implemented by user to decide if an event should be broadcast or we should extract context
    from an event. If the event should be broadcast, it will be handle by all the dagruns and task instances
    of that dag. Otherwise, only dagruns and task instances with the same context can handle the event.
    """

    def extract_context(self, event: BaseEvent) -> EventContext:
        """
        This method is called to decide if an event should be broadcast or we should extract context from the event.
        If the event should be broadcast, return :class:`Broadcast`. The event will be handle by all the dagruns
        and task executions of that dag. Otherwise, return :class:`ContextList`. Only dagruns
        and task executions with the same context can handle the event.

        If a :class:`ContextList` with an empty set or None is returns, the event is dropped.

        :param event: The :class:`~notification_service.base_notification.BaseEvent` to extract context from.
        :return: The context of the event or it should be broadcast.
        """
        pass


class BroadcastAllContextExtractor(ContextExtractor):
    """
    BroadcastAllContextExtractor is the default ContextExtractor to used. It marks all events as broadcast events.
    """

    def extract_context(self, event: BaseEvent) -> Optional[Text]:
        return Broadcast()
