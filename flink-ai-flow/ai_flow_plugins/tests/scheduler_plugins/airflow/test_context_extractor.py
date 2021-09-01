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
import unittest

import cloudpickle

from notification_service.base_notification import BaseEvent

from ai_flow_plugins.scheduler_plugins.airflow.context_extractor import AIFlowContextExtractorAdaptor, \
    AIFlowEventContextAdaptor

context_extractor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'context_extractor.pickle')


class TestAIFlowEventContextAdaptor(unittest.TestCase):

    def test_ai_flow_event_context_adaptor_none_context(self):
        context = AIFlowEventContextAdaptor(None)
        self.assertFalse(context.is_broadcast())
        self.assertIsNone(context.get_contexts())


class TestAIFlowContextExtractorAdaptor(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        import os
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'context_extractor_pickle_maker.py')
        os.system('python {}'.format(script_path))

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(context_extractor_path)

    def test_ai_flow_context_extractor_adaptor_serde(self):
        extractor = AIFlowContextExtractorAdaptor(context_extractor_path)
        extractor_bytes = cloudpickle.dumps(extractor)
        e = cloudpickle.loads(extractor_bytes)

        context = e.extract_context(BaseEvent(key='k', value='v'))
        self.assertFalse(context.is_broadcast())
        self.assertTrue('k' in context.get_contexts())

        context = e.extract_context(BaseEvent(key='broadcast', value='v'))
        self.assertTrue(context.is_broadcast())
