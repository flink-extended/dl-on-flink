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
import unittest
import json
import time

from airflow.executors.scheduling_action import SchedulingAction
from notification_service.base_notification import BaseEvent
from airflow.contrib.jobs.event_handlers import AIFlowHandler, AiFlowTs


class TestAIFlowEventHandlers(unittest.TestCase):

    def test_one_config(self):
        met_config_1 = {"action": "START",
                        "condition": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "default",
                        "sender": "1-job-name",
                        "value_condition": "EQUAL"}
        configs = [met_config_1]
        config_str = json.dumps(configs)
        handler = AIFlowHandler(config=config_str)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='default',
                                     sender='1-job-name',
                                     create_time=round(time.time()*1000))
        ts = AiFlowTs()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

    def test_two_config(self):
        met_config_1 = {"action": "START",
                        "condition": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "default",
                        "sender": "1-job-name",
                        "value_condition": "EQUAL"}
        met_config_2 = {"action": "START",
                        "condition": "NECESSARY",
                        "event_key": "key_2",
                        "event_type": "UNDEFINED",
                        "event_value": "value_2",
                        "life": "ONCE",
                        "namespace": "default",
                        "sender": "1-job-name",
                        "value_condition": "EQUAL"}
        configs = [met_config_1, met_config_2]
        config_str = json.dumps(configs)
        handler = AIFlowHandler(config=config_str)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='default',
                                     sender='1-job-name',
                                     create_time=round(time.time()*1000))
        ts = AiFlowTs()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.NONE, action)

        event: BaseEvent = BaseEvent(key='key_2',
                                     value='value_2',
                                     namespace='default',
                                     sender='1-job-name',
                                     create_time=round(time.time() * 1000))
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

    def test_two_config_2(self):
        met_config_1 = {"action": "START",
                        "condition": "SUFFICIENT",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "default",
                        "sender": "1-job-name",
                        "value_condition": "EQUAL"}
        met_config_2 = {"action": "START",
                        "condition": "NECESSARY",
                        "event_key": "key_2",
                        "event_type": "UNDEFINED",
                        "event_value": "value_2",
                        "life": "ONCE",
                        "namespace": "default",
                        "sender": "1-job-name",
                        "value_condition": "EQUAL"}
        configs = [met_config_1, met_config_2]
        config_str = json.dumps(configs)
        handler = AIFlowHandler(config=config_str)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='default',
                                     sender='1-job-name',
                                     create_time=round(time.time()*1000))
        ts = AiFlowTs()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

    def test_namespace_any(self):
        met_config_1 = {"action": "START",
                        "condition": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "*",
                        "sender": "1-job-name",
                        "value_condition": "EQUAL"}
        configs = [met_config_1]
        config_str = json.dumps(configs)
        handler = AIFlowHandler(config=config_str)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='aa',
                                     sender='1-job-name',
                                     create_time=int(time.time()*1000))
        ts = AiFlowTs()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='bb',
                                     sender='1-job-name',
                                     create_time=int(time.time() * 1000+1))
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

        met_config_1 = {"action": "START",
                        "condition": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "1-job-name",
                        "value_condition": "EQUAL"}
        configs = [met_config_1]
        config_str = json.dumps(configs)
        handler = AIFlowHandler(config=config_str)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='bb',
                                     sender='1-job-name',
                                     create_time=int(time.time() * 1000))
        ts = AiFlowTs()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.NONE, action)

    def test_event_type_any(self):
        met_config_1 = {"action": "START",
                        "condition": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "*",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "1-job-name",
                        "value_condition": "EQUAL"}
        configs = [met_config_1]
        config_str = json.dumps(configs)
        handler = AIFlowHandler(config=config_str)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     event_type='aa',
                                     namespace='aa',
                                     sender='1-job-name',
                                     create_time=int(time.time()*1000))
        ts = AiFlowTs()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='aa',
                                     event_type='bb',
                                     sender='1-job-name',
                                     create_time=int(time.time() * 1000+1))
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

        met_config_1 = {"action": "START",
                        "condition": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "aa",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "1-job-name",
                        "value_condition": "EQUAL"}
        configs = [met_config_1]
        config_str = json.dumps(configs)
        handler = AIFlowHandler(config=config_str)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     event_type='bb',
                                     namespace='aa',
                                     sender='1-job-name',
                                     create_time=int(time.time() * 1000))
        ts = AiFlowTs()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.NONE, action)

    def test_sender_any(self):
        met_config_1 = {"action": "START",
                        "condition": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "*",
                        "value_condition": "EQUAL"}
        configs = [met_config_1]
        config_str = json.dumps(configs)
        handler = AIFlowHandler(config=config_str)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='aa',
                                     sender='aa',
                                     create_time=int(time.time()*1000))
        ts = AiFlowTs()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='aa',
                                     sender='bb',
                                     create_time=int(time.time() * 1000+1))
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

        met_config_1 = {"action": "START",
                        "condition": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "aa",
                        "value_condition": "EQUAL"}
        configs = [met_config_1]
        config_str = json.dumps(configs)
        handler = AIFlowHandler(config=config_str)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='aa',
                                     sender='bb',
                                     create_time=int(time.time() * 1000))
        ts = AiFlowTs()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.NONE, action)

    def test_key_any(self):
        met_config_1 = {"action": "START",
                        "condition": "NECESSARY",
                        "event_key": "*",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "aa",
                        "value_condition": "EQUAL"}
        configs = [met_config_1]
        config_str = json.dumps(configs)
        handler = AIFlowHandler(config=config_str)
        event: BaseEvent = BaseEvent(key='key_1_1',
                                     value='value_1',
                                     namespace='aa',
                                     sender='aa',
                                     create_time=int(time.time()*1000))
        ts = AiFlowTs()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

        event: BaseEvent = BaseEvent(key='key_1_2',
                                     value='value_1',
                                     namespace='aa',
                                     sender='aa',
                                     create_time=int(time.time() * 1000+1))
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

        met_config_1 = {"action": "START",
                        "condition": "NECESSARY",
                        "event_key": "aa",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "aa",
                        "value_condition": "EQUAL"}
        configs = [met_config_1]
        config_str = json.dumps(configs)
        handler = AIFlowHandler(config=config_str)
        event: BaseEvent = BaseEvent(key='key_1_1',
                                     value='value_1',
                                     namespace='aa',
                                     sender='aa',
                                     create_time=int(time.time()*1000))
        ts = AiFlowTs()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.NONE, action)

    def test_multiple_any_config(self):
        met_config_1 = {"action": "START",
                        "condition": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "*",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "*",
                        "sender": "1-job-name",
                        "value_condition": "EQUAL"}
        configs = [met_config_1]
        config_str = json.dumps(configs)
        handler = AIFlowHandler(config=config_str)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='default',
                                     sender='1-job-name',
                                     create_time=round(time.time()*1000))
        ts = AiFlowTs()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='default',
                                     sender='aa',
                                     create_time=round(time.time() * 1000))
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.NONE, action)

        event: BaseEvent = BaseEvent(key='key_1_1',
                                     value='value_1',
                                     namespace='default',
                                     sender='1-job-name',
                                     create_time=round(time.time() * 1000))
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.NONE, action)
