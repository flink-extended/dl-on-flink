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
from abc import ABC, abstractmethod
from typing import Text, Set

from ai_flow.util.json_utils import Jsonable

from notification_service.base_notification import BaseEvent

WORKFLOW_EXECUTION_DEFAULT_CONTEXT = 'default'


class EventContext(ABC):
    """
    The context of the event returns by ContextExtractor.
    """

    @abstractmethod
    def is_broadcast(self) -> bool:
        """
        :return: Whether the event should be broadcast.
        """
        pass

    @abstractmethod
    def get_contexts(self) -> Set[Text]:
        """
        :return: A set of contexts the event belongs to.
        """
        pass


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


class ContextExtractor(ABC, Jsonable):
    """
    ContextExtractor can be implemented by user to decide if an event should be broadcast or we should extract context
    from an event. If the event should be broadcast, it will be handle by all the workflow executions and job executions
    of that workflow. Otherwise, only workflow execution and job executions with the same context can handle the event.
    """

    @abstractmethod
    def extract_context(self, event: BaseEvent) -> EventContext:
        """
        This method is called to decide if an event should be broadcast or we should extract context from the event.
        If the event should be broadcast, return :class:`Broadcast`. The event will be handle by all the workflow
        executions and job executions of that workflow. Otherwise, return :class:`ContextList`. Only workflow execution
        and job executions with the same context can handle the event.

        If a :class:`ContextList` with an empty set or None is returns, the event is dropped.

        :param event: The :class:`~notification_service.base_notification.BaseEvent` to extract context from.
        :return: The context of the event or it should be broadcast.
        """
        pass


class BroadcastAllContextExtractor(ContextExtractor):
    """
    BroadcastAllContextExtractor is the default ContextExtractor to used. It marks all events as broadcast events.
    """

    def extract_context(self, event: BaseEvent) -> EventContext:
        return Broadcast()
