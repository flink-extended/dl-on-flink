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
from datetime import datetime

from airflow.executors.scheduling_action import SchedulingAction
from notification_service.base_notification import BaseEvent
from ai_flow_plugins.scheduler_plugins.airflow.event_handler import AIFlowHandler, AiFlowTs


class TestAIFlowEventHandlers(unittest.TestCase):

    def test_one_config(self):
        met_config_1 = {"action": "START",
                        "condition_type": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "default",
                        "sender": "1-job-name",
                        "value_condition": "EQUALS"}
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
                        "condition_type": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "default",
                        "sender": "1-job-name",
                        "value_condition": "EQUALS"}
        met_config_2 = {"action": "START",
                        "condition_type": "NECESSARY",
                        "event_key": "key_2",
                        "event_type": "UNDEFINED",
                        "event_value": "value_2",
                        "life": "ONCE",
                        "namespace": "default",
                        "sender": "1-job-name",
                        "value_condition": "EQUALS"}
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
                        "condition_type": "SUFFICIENT",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "default",
                        "sender": "1-job-name",
                        "value_condition": "EQUALS"}
        met_config_2 = {"action": "START",
                        "condition_type": "NECESSARY",
                        "event_key": "key_2",
                        "event_type": "UNDEFINED",
                        "event_value": "value_2",
                        "life": "ONCE",
                        "namespace": "default",
                        "sender": "1-job-name",
                        "value_condition": "EQUALS"}
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
                        "condition_type": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "*",
                        "sender": "1-job-name",
                        "value_condition": "EQUALS"}
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
                        "condition_type": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "1-job-name",
                        "value_condition": "EQUALS"}
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
                        "condition_type": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "*",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "1-job-name",
                        "value_condition": "EQUALS"}
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
                        "condition_type": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "aa",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "1-job-name",
                        "value_condition": "EQUALS"}
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
                        "condition_type": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "*",
                        "value_condition": "EQUALS"}
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
                        "condition_type": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "aa",
                        "value_condition": "EQUALS"}
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
                        "condition_type": "NECESSARY",
                        "event_key": "*",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "aa",
                        "value_condition": "EQUALS"}
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
                        "condition_type": "NECESSARY",
                        "event_key": "aa",
                        "event_type": "UNDEFINED",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "aa",
                        "sender": "aa",
                        "value_condition": "EQUALS"}
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
                        "condition_type": "NECESSARY",
                        "event_key": "key_1",
                        "event_type": "*",
                        "event_value": "value_1",
                        "life": "ONCE",
                        "namespace": "*",
                        "sender": "1-job-name",
                        "value_condition": "EQUALS"}
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

    def test_handle_task_status_change_event(self):
        from airflow.events.scheduler_events import TaskStateChangedEvent
        from airflow.utils.state import State

        met_config_1 = {"action": "START",
                        "condition_type": "SUFFICIENT",
                        "event_key": "dag_1.task_1",
                        "event_type": "TASK_STATUS_CHANGED",
                        "event_value": "RUNNING",
                        "life": "ONCE",
                        "namespace": "test",
                        "sender": "task_1",
                        "value_condition": "EQUALS"}
        met_config_2 = {"action": "STOP",
                        "condition_type": "SUFFICIENT",
                        "event_key": "dag_1.task_1",
                        "event_type": "TASK_STATUS_CHANGED",
                        "event_value": "FINISHED",
                        "life": "ONCE",
                        "namespace": "test",
                        "sender": "task_1",
                        "value_condition": "EQUALS"}
        configs = [met_config_1, met_config_2]
        config_str = json.dumps(configs)
        handler = AIFlowHandler(config=config_str)

        ts = AiFlowTs()

        event = TaskStateChangedEvent("task_1", "test.dag_1", datetime.utcnow(), State.RUNNING).to_event()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

        time.sleep(0.01)
        event = TaskStateChangedEvent("task_1", "test.dag_1", datetime.utcnow(), State.KILLING).to_event()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.NONE, action)

        time.sleep(0.01)
        event = TaskStateChangedEvent("task_1", "test.dag_1", datetime.utcnow(), State.SUCCESS).to_event()
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.STOP, action)
