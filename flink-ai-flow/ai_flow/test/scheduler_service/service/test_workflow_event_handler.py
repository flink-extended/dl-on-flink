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
import time

from ai_flow.meta.workflow_meta import WorkflowMeta

from ai_flow.scheduler_service.service.workflow_event_handler import WorkflowEventHandler, WorkflowHandlerState

from ai_flow.workflow.control_edge import WorkflowSchedulingRule, MeetAnyEventCondition, EventLife, ValueCondition, \
    WorkflowAction, MeetAllEventCondition
from airflow.executors.scheduling_action import SchedulingAction
from notification_service.base_notification import BaseEvent


class TestWorkflowEventHandler(unittest.TestCase):

    def setUp(self) -> None:
        self.workflow_meta = WorkflowMeta('workflow', 0)

    def test_one_config(self):
        rule = WorkflowSchedulingRule(MeetAnyEventCondition().add_event(
            event_key="key_1",
            event_value="value_1",
            sender="1-job-name",
            value_condition=ValueCondition.EQUALS), action=WorkflowAction.START)
        self.workflow_meta.scheduling_rules = [rule]
        handler = WorkflowEventHandler(self.workflow_meta)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='default',
                                     sender='1-job-name',
                                     create_time=round(time.time() * 1000))
        action, ts = handler.handle_event(event, None)
        self.assertEqual(SchedulingAction.START, action)

    def test_two_events_config(self):
        condition = MeetAllEventCondition() \
            .add_event(event_key="key_1", event_value="value_1", sender="1-job-name") \
            .add_event(event_key="key_2", event_value="value_2", sender="1-job-name")
        rule = WorkflowSchedulingRule(condition, action=WorkflowAction.START)
        self.workflow_meta.scheduling_rules = [rule]
        handler = WorkflowEventHandler(self.workflow_meta)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='default',
                                     sender='1-job-name',
                                     create_time=round(time.time() * 1000))
        action, ts = handler.handle_event(event, None)
        self.assertEqual(SchedulingAction.NONE, action)

        event: BaseEvent = BaseEvent(key='key_2',
                                     value='value_2',
                                     namespace='default',
                                     sender='1-job-name',
                                     create_time=round(time.time() * 1000))
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

    def test_two_rules(self):
        condition = MeetAnyEventCondition() \
            .add_event(event_key="key_1", event_value="value_1", sender="1-job-name")
        rule1 = WorkflowSchedulingRule(condition, action=WorkflowAction.START)
        condition = MeetAllEventCondition() \
            .add_event(event_key="key_2", event_value="value_2", sender="1-job-name")
        rule2 = WorkflowSchedulingRule(condition, action=WorkflowAction.START)
        self.workflow_meta.scheduling_rules = [rule1, rule2]
        handler = WorkflowEventHandler(self.workflow_meta)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='default',
                                     sender='1-job-name',
                                     create_time=round(time.time() * 1000))
        action, ts = handler.handle_event(event, None)
        self.assertEqual(SchedulingAction.START, action)

    def test_namespace_any(self):
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event(
            event_key="key_1",
            event_value="value_1",
            namespace="*",
            sender="1-job-name"), action=WorkflowAction.START)
        self.workflow_meta.scheduling_rules = [rule]
        handler = WorkflowEventHandler(self.workflow_meta)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='aa',
                                     sender='1-job-name',
                                     create_time=int(time.time() * 1000))
        action, ts = handler.handle_event(event, None)
        self.assertEqual(SchedulingAction.START, action)

        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='bb',
                                     sender='1-job-name',
                                     create_time=int(time.time() * 1000 + 1))
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event(
            event_key="key_1",
            event_value="value_1",
            namespace="aa",
            sender="1-job-name"), action=WorkflowAction.START)

        self.workflow_meta.scheduling_rules = [rule]
        handler = WorkflowEventHandler(self.workflow_meta)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='bb',
                                     sender='1-job-name',
                                     create_time=int(time.time() * 1000))
        action, ts = handler.handle_event(event, None)
        self.assertEqual(SchedulingAction.NONE, action)

    def test_event_type_any(self):
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event(
            event_key="key_1",
            event_type="*",
            event_value="value_1",
            namespace="aa",
            sender="1-job-name"), action=WorkflowAction.START)
        self.workflow_meta.scheduling_rules = [rule]
        handler = WorkflowEventHandler(self.workflow_meta)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     event_type='aa',
                                     namespace='aa',
                                     sender='1-job-name',
                                     create_time=int(time.time() * 1000))
        action, ts = handler.handle_event(event, None)
        self.assertEqual(SchedulingAction.START, action)

        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='aa',
                                     event_type='bb',
                                     sender='1-job-name',
                                     create_time=int(time.time() * 1000 + 1))
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event(
            event_key="key_1",
            event_type="aa",
            event_value="value_1",
            namespace="aa",
            sender="1-job-name"), action=WorkflowAction.START)
        self.workflow_meta.scheduling_rules = [rule]
        handler = WorkflowEventHandler(self.workflow_meta)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     event_type='bb',
                                     namespace='aa',
                                     sender='1-job-name',
                                     create_time=int(time.time() * 1000))
        action, ts = handler.handle_event(event, None)
        self.assertEqual(SchedulingAction.NONE, action)

    def test_sender_any(self):
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event(
            event_key="key_1",
            event_value="value_1",
            namespace="aa",
            sender="*"), action=WorkflowAction.START)
        self.workflow_meta.scheduling_rules = [rule]
        handler = WorkflowEventHandler(self.workflow_meta)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='aa',
                                     sender='aa',
                                     create_time=int(time.time() * 1000))
        action, ts = handler.handle_event(event, None)
        self.assertEqual(SchedulingAction.START, action)

        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='aa',
                                     sender='bb',
                                     create_time=int(time.time() * 1000 + 1))
        action, ts = handler.handle_event(event, None)
        self.assertEqual(SchedulingAction.START, action)

        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event(
            event_key="key_1",
            event_value="value_1",
            namespace="aa",
            sender="aa"), action=WorkflowAction.START)
        self.workflow_meta.scheduling_rules = [rule]
        handler = WorkflowEventHandler(self.workflow_meta)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='aa',
                                     sender='bb',
                                     create_time=int(time.time() * 1000))
        action, ts = handler.handle_event(event, None)
        self.assertEqual(SchedulingAction.NONE, action)

    def test_key_any(self):
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event(
            event_key="*",
            event_value="value_1",
            namespace="aa",
            sender="aa"), action=WorkflowAction.START)
        self.workflow_meta.scheduling_rules = [rule]
        handler = WorkflowEventHandler(self.workflow_meta)
        event: BaseEvent = BaseEvent(key='key_1_1',
                                     value='value_1',
                                     namespace='aa',
                                     sender='aa',
                                     create_time=int(time.time() * 1000))
        action, ts = handler.handle_event(event, None)
        self.assertEqual(SchedulingAction.START, action)

        event: BaseEvent = BaseEvent(key='key_1_2',
                                     value='value_1',
                                     namespace='aa',
                                     sender='aa',
                                     create_time=int(time.time() * 1000 + 1))
        action, ts = handler.handle_event(event, ts)
        self.assertEqual(SchedulingAction.START, action)

        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event(
            event_key="aa",
            event_value="value_1",
            namespace="aa",
            sender="aa"), action=WorkflowAction.START)
        self.workflow_meta.scheduling_rules = [rule]
        handler = WorkflowEventHandler(self.workflow_meta)
        event: BaseEvent = BaseEvent(key='key_1_1',
                                     value='value_1',
                                     namespace='aa',
                                     sender='aa',
                                     create_time=int(time.time() * 1000))
        action, ts = handler.handle_event(event, None)
        self.assertEqual(SchedulingAction.NONE, action)

    def test_multiple_any_config(self):
        rule = WorkflowSchedulingRule(MeetAllEventCondition().add_event(
            event_key="key_1",
            event_value="value_1",
            event_type="*",
            namespace="*",
            sender="1-job-name"), action=WorkflowAction.START)
        self.workflow_meta.scheduling_rules = [rule]
        handler = WorkflowEventHandler(self.workflow_meta)
        event: BaseEvent = BaseEvent(key='key_1',
                                     value='value_1',
                                     namespace='default',
                                     sender='1-job-name',
                                     create_time=round(time.time() * 1000))
        action, ts = handler.handle_event(event, None)
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

    def test_event_handler_schedule_time(self):
        condition = MeetAnyEventCondition() \
            .add_event(event_key="key_1", event_value="value_1", sender="1-job-name")
        rule1 = WorkflowSchedulingRule(condition, action=WorkflowAction.START)
        condition = MeetAllEventCondition() \
            .add_event(event_key="key_1", event_value="value_1", sender="1-job-name") \
            .add_event(event_key='key_2', event_value='value_2', sender="1-job-name")
        rule2 = WorkflowSchedulingRule(condition, action=WorkflowAction.STOP)

        self.workflow_meta.scheduling_rules = [rule1, rule2]
        handler = WorkflowEventHandler(self.workflow_meta)

        event1_time = round(time.time() * 1000)
        event1: BaseEvent = BaseEvent(key='key_1',
                                      value='value_1',
                                      namespace='default',
                                      sender='1-job-name',
                                      create_time=event1_time)
        action, ts = handler.handle_event(event1, None)
        ts: WorkflowHandlerState = ts
        self.assertEqual(event1_time, ts.rule_states[0].schedule_time)
        self.assertEqual(event1_time, ts.rule_states[0].latest_time)
        self.assertNotEqual(event1_time, ts.rule_states[1].schedule_time)
        self.assertEqual(event1_time, ts.rule_states[1].latest_time)

    def test_two_rule_trigger_at_same_time_take_action_from_first_rule(self):
        condition = MeetAnyEventCondition() \
            .add_event(event_key="key_1", event_value="value_1", sender="1-job-name")
        rule1 = WorkflowSchedulingRule(condition, action=WorkflowAction.START)
        condition = MeetAllEventCondition() \
            .add_event(event_key="key_1", event_value="value_1", sender="1-job-name") \
            .add_event(event_key='key_2', event_value='value_2', sender="1-job-name")
        rule2 = WorkflowSchedulingRule(condition, action=WorkflowAction.STOP)

        self.workflow_meta.scheduling_rules = [rule1, rule2]
        handler = WorkflowEventHandler(self.workflow_meta)
        event1: BaseEvent = BaseEvent(key='key_1',
                                      value='value_1',
                                      namespace='default',
                                      sender='1-job-name',
                                      create_time=round(time.time() * 1000))
        event2: BaseEvent = BaseEvent(key='key_2',
                                      value='value_2',
                                      namespace='default',
                                      sender='1-job-name',
                                      create_time=round(time.time() * 1000))
        action, ts = handler.handle_event(event2, None)
        self.assertEqual(SchedulingAction.NONE, action)

        action, ts = handler.handle_event(event1, ts)
        self.assertEqual(SchedulingAction.START, action)

    def test_two_rules_trigger_will_clear_all_event_life(self):
        condition = MeetAnyEventCondition() \
            .add_event(event_key="key_1", event_value="value_1", sender="1-job-name")
        rule1 = WorkflowSchedulingRule(condition, action=WorkflowAction.START)
        condition = MeetAllEventCondition() \
            .add_event(event_key="key_1", event_value="value_1", sender="1-job-name") \
            .add_event(event_key='key_2', event_value='value_2', sender="1-job-name")
        rule2 = WorkflowSchedulingRule(condition, action=WorkflowAction.STOP)

        self.workflow_meta.scheduling_rules = [rule1, rule2]
        handler = WorkflowEventHandler(self.workflow_meta)
        event1: BaseEvent = BaseEvent(key='key_1',
                                      value='value_1',
                                      namespace='default',
                                      sender='1-job-name',
                                      create_time=round(time.time() * 1000))
        event2: BaseEvent = BaseEvent(key='key_2',
                                      value='value_2',
                                      namespace='default',
                                      sender='1-job-name',
                                      create_time=round(time.time() * 1000))
        action, ts = handler.handle_event(event2, None)
        self.assertEqual(SchedulingAction.NONE, action)
        action, ts = handler.handle_event(event1, ts)
        self.assertEqual(SchedulingAction.START, action)
        action, ts = handler.handle_event(event2, ts)
        self.assertEqual(SchedulingAction.NONE, action)

    def test_unordered_event_life_once(self):
        condition = MeetAnyEventCondition() \
            .add_event(event_key="key_1", event_value="value_1", sender="1-job-name")
        rule1 = WorkflowSchedulingRule(condition, action=WorkflowAction.START)

        self.workflow_meta.scheduling_rules = [rule1]
        handler = WorkflowEventHandler(self.workflow_meta)
        event1: BaseEvent = BaseEvent(key='key_1',
                                      value='value_1',
                                      namespace='default',
                                      sender='1-job-name',
                                      create_time=round(time.time() * 1000))
        event1_in_past: BaseEvent = BaseEvent(key='key_1',
                                              value='value_1',
                                              namespace='default',
                                              sender='1-job-name',
                                              create_time=0)
        action, ts = handler.handle_event(event1, None)
        self.assertEqual(SchedulingAction.START, action)
        action, ts = handler.handle_event(event1_in_past, ts)
        self.assertEqual(SchedulingAction.NONE, action)

    def test_unordered_event_life_repeated(self):
        condition = MeetAnyEventCondition() \
            .add_event(event_key="key_1", event_value="value_1", sender="1-job-name", life=EventLife.REPEATED)
        rule1 = WorkflowSchedulingRule(condition, action=WorkflowAction.START)

        self.workflow_meta.scheduling_rules = [rule1]
        handler = WorkflowEventHandler(self.workflow_meta)
        event1: BaseEvent = BaseEvent(key='key_1',
                                      value='value_1',
                                      namespace='default',
                                      sender='1-job-name',
                                      create_time=round(time.time() * 1000))
        event1_in_past: BaseEvent = BaseEvent(key='key_1',
                                              value='value_1',
                                              namespace='default',
                                              sender='1-job-name',
                                              create_time=0)
        action, ts = handler.handle_event(event1, None)
        self.assertEqual(SchedulingAction.START, action)
        action, ts = handler.handle_event(event1_in_past, ts)
        self.assertEqual(SchedulingAction.START, action)
