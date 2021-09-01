from ai_flow.api.context_extractor import ContextExtractor
from typing import Optional, Text

from airflow.events.context_extractor import EventContext, Broadcast, ContextList
from notification_service.base_notification import BaseEvent


class FixedContextExtractor(ContextExtractor):

    def __init__(self, context):
        self._context = context

    def extract_context(self, event: BaseEvent) -> EventContext:
        if event.key == 'broadcast':
            return Broadcast()

        context_list = ContextList()
        context_list.add_context(self._context)
        return context_list


class ErrorContextExtractor(ContextExtractor):

    def extract_context(self, event: BaseEvent) -> EventContext:
        raise RuntimeError('ContextExtractor Exception')
