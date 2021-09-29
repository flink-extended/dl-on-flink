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
import base64
from typing import Set, Text

import cloudpickle
from notification_service.base_notification import BaseEvent

from ai_flow.api.context_extractor \
    import ContextExtractor as AIFlowContextExtractor, \
    EventContext as AIFlowEventContext
from airflow.events.context_extractor \
    import ContextExtractor as AirflowContextExtractor, \
    EventContext as AirflowEventContext


class AIFlowEventContextAdaptor(AirflowEventContext):

    def __init__(self, ai_flow_event_context: AIFlowEventContext):
        self._ai_flow_event_context = ai_flow_event_context

    def is_broadcast(self) -> bool:
        if self._ai_flow_event_context is None:
            return False
        return self._ai_flow_event_context.is_broadcast()

    def get_contexts(self) -> Set[Text]:
        if self._ai_flow_event_context is None:
            return None
        return self._ai_flow_event_context.get_contexts()


class AIFlowContextExtractorAdaptor(AirflowContextExtractor):

    def __init__(self, ai_flow_context_extractor_base_64_str: str):
        self.ai_flow_context_extractor_base_64 = ai_flow_context_extractor_base_64_str.encode('utf-8')

    def extract_context(self, event: BaseEvent) -> AirflowEventContext:
        context_extractor: AIFlowContextExtractor = \
            cloudpickle.loads(base64.b64decode(self.ai_flow_context_extractor_base_64))
        return AIFlowEventContextAdaptor(context_extractor.extract_context(event))
