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
import copy
import logging
from typing import Tuple, Dict, List, Optional

from ai_flow.meta.workflow_meta import WorkflowMeta

from ai_flow.workflow.control_edge import WorkflowSchedulingRule, WorkflowAction, ConditionType, EventCondition, \
    EventMeetConfig, ValueCondition, EventLife
from notification_service.base_notification import BaseEvent, ANY_CONDITION


class SchedulingRuleState(object):
    def __init__(self):
        self.event_map: Dict[Tuple[str, str, str, str], BaseEvent] = {}
        self.schedule_time = 0
        self.latest_time = 0

    def __str__(self):
        return "EVENT_MAP: {0} TIME: {1} LATEST: {2}".format(self.event_map, self.schedule_time, self.latest_time)


class WorkflowHandlerState(object):
    def __init__(self, rules_cnt: int):
        self.rule_states: List[SchedulingRuleState] = [SchedulingRuleState() for _ in range(rules_cnt)]

    def add_event(self, event: BaseEvent):
        for rule_state in self.rule_states:
            rule_state.event_map[(event.namespace, event.event_type, event.sender, event.key)] = copy.deepcopy(event)
            rule_state.latest_time = event.create_time


class WorkflowEventHandler:
    def __init__(self, workflow: WorkflowMeta):
        self.scheduling_rules = workflow.scheduling_rules

    def handle_event(self, event: BaseEvent, workflow_state: object) -> Tuple[WorkflowAction, object]:
        rules = self.scheduling_rules
        if workflow_state is None:
            workflow_state = WorkflowHandlerState(len(rules))
        af_ts = copy.deepcopy(workflow_state)
        af_ts.add_event(event)
        actions = self._check_rules(rules, af_ts)

        # pick the first triggered action
        for action in actions:
            if action is not None:
                logging.debug("WorkflowEventHandler {} handle event {} triggered action: {}"
                              .format(self.scheduling_rules, event, action))
                return action, af_ts

        logging.debug("WorkflowEventHandler {} handle event {} no action triggered return action {}"
                      .format(self.scheduling_rules, event, WorkflowAction.NONE))
        return WorkflowAction.NONE, af_ts

    @staticmethod
    def _match_config_events(namespace, event_type, sender, key, event_map: Dict):
        events = []

        def match_condition(config_value, event_value) -> bool:
            if config_value == ANY_CONDITION or event_value == config_value:
                return True
            else:
                return False

        for e_key, event in event_map.items():
            c_namespace = match_condition(namespace, event.namespace)
            c_event_type = match_condition(event_type, event.event_type)
            c_sender = match_condition(sender, event.sender)
            c_key = match_condition(key, event.key)
            if c_namespace and c_event_type and c_sender and c_key:
                events.append(event)
        return events

    def _check_rules(self, rules: List[WorkflowSchedulingRule], ts: WorkflowHandlerState) -> List[WorkflowAction]:
        rule_states = ts.rule_states
        rules_num = len(rules)
        res: List[Optional[WorkflowAction]] = [None] * rules_num
        for i in range(rules_num):
            rule = rules[i]
            rule_state = rule_states[i]
            if self._check_rule(rule, rule_state):
                rule_state.schedule_time = rule_state.latest_time
                res[i] = rule.action
        return res

    def _check_rule(self, rule: WorkflowSchedulingRule, ts: SchedulingRuleState) -> bool:
        event_condition = rule.event_condition
        if ConditionType.MEET_ANY == event_condition.condition_type:
            return self._check_meet_any_event_condition(rule.event_condition, ts)
        elif ConditionType.MEET_ALL == event_condition.condition_type:
            return self._check_meet_all_event_condition(rule.event_condition, ts)
        else:
            logging.warning("Unsupported ConditionType {}".format(event_condition.condition_type))
            return False

    def _check_meet_any_event_condition(self, event_condition: EventCondition, ts: SchedulingRuleState) -> bool:
        for event_meet_config in event_condition.events:
            if self._check_event_meet(event_meet_config, ts):
                return True
        return False

    def _check_meet_all_event_condition(self, event_condition: EventCondition, ts: SchedulingRuleState) -> bool:
        for event_meet_config in event_condition.events:
            if not self._check_event_meet(event_meet_config, ts):
                return False
        return True

    def _check_event_meet(self, event_meet_config: EventMeetConfig, ts: SchedulingRuleState) -> bool:
        event_map: Dict = ts.event_map
        schedule_time = ts.schedule_time
        events = self._match_config_events(event_meet_config.namespace,
                                           event_meet_config.event_type,
                                           event_meet_config.sender,
                                           event_meet_config.event_key,
                                           event_map)
        if 0 == len(events):
            return False
        for event in events:
            v, event_time = event.value, event.create_time
            if event_meet_config.life == EventLife.ONCE:
                if event_meet_config.value_condition == ValueCondition.EQUALS:
                    if v == event_meet_config.event_value and event_time > schedule_time:
                        return True
                else:
                    if event_time > schedule_time:
                        return True
            else:
                if event_meet_config.value_condition == ValueCondition.EQUALS:
                    if v == event_meet_config.event_value:
                        return True
                else:
                    return True
        # no event meet
        return False
