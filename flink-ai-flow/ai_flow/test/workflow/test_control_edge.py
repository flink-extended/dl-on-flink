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
import unittest

from ai_flow.util import json_utils

from ai_flow.workflow.control_edge import EventMeetConfig, EventLife, ValueCondition, EventCondition, ConditionType, \
    MeetAnyEventCondition, MeetAllEventCondition, JobSchedulingRule, JobAction, ControlEdge
from notification_service.base_notification import UNDEFINED_EVENT_TYPE, DEFAULT_NAMESPACE


class TestEventMeetConfig(unittest.TestCase):

    def test_event_meet_config(self):
        event_config = EventMeetConfig(event_key='key', event_value='value')
        self.assertEqual(event_config.event_key, 'key')
        self.assertEqual(event_config.event_value, 'value')
        self.assertEqual(event_config.event_type, UNDEFINED_EVENT_TYPE)
        self.assertEqual(event_config.namespace, DEFAULT_NAMESPACE)
        self.assertIsNone(event_config.sender)
        self.assertEqual(event_config.life, EventLife.ONCE)
        self.assertEqual(event_config.value_condition, ValueCondition.EQUALS)


class TestEventCondition(unittest.TestCase):

    def test_event_condition_add_event(self):
        condition = EventCondition([], ConditionType.MEET_ANY)
        condition.add_event(event_key='k1', event_value='v1')
        condition.add_event(event_key='k2', event_value='v2')
        expected_list = [EventMeetConfig('k1', 'v1'), EventMeetConfig('k2', 'v2')]
        self.assertListEqual(expected_list, condition.events)

        # duplicate event will not added twice
        condition.add_event(event_key='k1', event_value='v1')
        condition.add_event(event_key='k2', event_value='v2')
        self.assertListEqual(expected_list, condition.events)

    def test_event_condition_serde(self):
        condition = EventCondition([], ConditionType.MEET_ANY)
        condition.add_event(event_key='k1', event_value='v1')
        condition.add_event(event_key='k2', event_value='v2')
        loaded_condition = json_utils.loads(json_utils.dumps(condition))
        self.assertEqual(condition, loaded_condition)
        loaded_condition.add_event(event_key='k1', event_value='v1')
        loaded_condition.add_event(event_key='k2', event_value='v2')
        self.assertEqual(condition, loaded_condition)


class MeetAnyEventConditionTest(unittest.TestCase):

    def test_meet_any_event_condition(self):
        condition = MeetAnyEventCondition()
        self.assertEqual(ConditionType.MEET_ANY, condition.condition_type)


class MeetAllEventConditionTest(unittest.TestCase):

    def test_meet_all_event_condition(self):
        condition = MeetAllEventCondition()
        self.assertEqual(ConditionType.MEET_ALL, condition.condition_type)


class SchedulingRuleTest(unittest.TestCase):

    def test_scheduling_rule(self):
        condition = MeetAllEventCondition()
        action = JobAction.START
        rule = JobSchedulingRule(condition, action)
        self.assertEqual(condition, rule.event_condition)
        self.assertEqual(action, rule.action)

    def test_scheduling_rule_serde(self):
        condition = MeetAllEventCondition()
        action = JobAction.START
        rule = JobSchedulingRule(condition, action)
        loaded_rule = json_utils.loads(json_utils.dumps(rule))
        self.assertEqual(rule, loaded_rule)


class ControlEdgeTest(unittest.TestCase):

    def test_control_edge(self):
        condition = MeetAllEventCondition()
        action = JobAction.START
        rule = JobSchedulingRule(condition, action)
        edge = ControlEdge('task', rule)
        self.assertEqual('*', edge.source)
        self.assertEqual('task', edge.destination)
        self.assertEqual(rule, edge.scheduling_rule)
