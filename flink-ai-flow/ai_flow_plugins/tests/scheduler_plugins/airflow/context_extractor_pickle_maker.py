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
import os

import cloudpickle

from notification_service.base_notification import BaseEvent

from ai_flow.api.context_extractor import ContextExtractor, EventContext, Broadcast, ContextList

context_extractor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'context_extractor.pickle')


class EventKeyContextExtractor(ContextExtractor):
    def extract_context(self, event: BaseEvent) -> EventContext:
        if event.key == 'broadcast':
            return Broadcast()

        context_list = ContextList()
        context_list.add_context(event.key)
        return context_list


if __name__ == '__main__':
    e = EventKeyContextExtractor()

    with open(context_extractor_path, 'wb') as f:
        cloudpickle.dump(e, f)
