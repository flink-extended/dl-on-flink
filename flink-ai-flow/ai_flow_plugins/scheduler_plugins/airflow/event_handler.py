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
import logging
from typing import Tuple, List, Dict, Optional
import json
import copy

from ai_flow.util import json_utils

from ai_flow.workflow.control_edge import JobSchedulingRule, ConditionType, EventLife, ValueCondition, JobAction, \
    EventMeetConfig, EventCondition

from airflow.utils.state import State

from ai_flow.workflow import status
from airflow.events.scheduler_events import SchedulerInnerEventType

from airflow.executors.scheduling_action import SchedulingAction
from airflow.models.eventhandler import EventHandler
from notification_service.base_notification import BaseEvent, ANY_CONDITION


class StartEventHandler(EventHandler):
    """
    Internal event handler that always return start scheduling action.
    """

    def handle_event(self, event: BaseEvent, task_state: object) -> Tuple[SchedulingAction, object]:
        return SchedulingAction.START, task_state


class RestartEventHandler(EventHandler):
    """
    Internal event handler that always return restart scheduling action.
    """

    def handle_event(self, event: BaseEvent, task_state: object) -> Tuple[SchedulingAction, object]:
        return SchedulingAction.RESTART, task_state


class ActionEventHandler(EventHandler):
    """
    Internal event handler that handle event base on the key of the event.
    """

    def handle_event(self, event: BaseEvent, task_state: object) -> Tuple[SchedulingAction, object]:
        if 'stop' == event.key:
            return SchedulingAction.STOP, task_state
        elif 'restart' == event.key:
            return SchedulingAction.RESTART, task_state
        else:
            return SchedulingAction.START, task_state


class AiFlowTs(object):
    def __init__(self, rules_cnt: int):
        self.rule_states: List[SchedulingRuleState] = [SchedulingRuleState() for _ in range(rules_cnt)]

    def add_event(self, event: BaseEvent):
        for rule_state in self.rule_states:
            rule_state.event_map[(event.namespace, event.event_type, event.sender, event.key)] = copy.deepcopy(event)
            rule_state.latest_time = event.create_time


class SchedulingRuleState(object):
    def __init__(self):
        self.event_map: Dict[Tuple[str, str, str, str], BaseEvent] = {}
        self.schedule_time = 0
        self.latest_time = 0

    def __str__(self):
        return "EVENT_MAP: {0} TIME: {1} LATEST: {2}".format(self.event_map, self.schedule_time, self.latest_time)


class ActionWrapper(object):
    def __init__(self, action=SchedulingAction.NONE):
        self.action = action


def _airflow_task_state_to_aiflow_status(airflow_task_state) -> Optional[status.Status]:
    if State.SUCCESS == airflow_task_state:
        return status.Status.FINISHED
    elif State.FAILED == airflow_task_state:
        return status.Status.FAILED
    elif State.RUNNING == airflow_task_state:
        return status.Status.RUNNING
    elif State.KILLED == airflow_task_state or State.SHUTDOWN == airflow_task_state:
        return status.Status.KILLED
    elif State.KILLING:
        # map KILLING to value None so that it will not trigger any action
        return None
    else:
        return status.Status.INIT


def job_action_to_scheduling_action(action: JobAction) -> SchedulingAction:
    if JobAction.START == action:
        return SchedulingAction.START
    elif JobAction.RESTART == action:
        return SchedulingAction.RESTART
    elif JobAction.STOP == action:
        return SchedulingAction.STOP
    elif JobAction.NONE == action:
        return SchedulingAction.NONE
    else:
        logging.warning("Cannot map JobAction {} to SchedulingAction, SchedulingAction.NONE will be used"
                        .format(action))
        return SchedulingAction.NONE


class AIFlowHandler(EventHandler):
    """
    AIFlowHandler is an implementation of EventHandler,
    which implements the semantics of ai flow based on event scheduling.
    """

    def __init__(self, config: str):
        self.config = config

    @staticmethod
    def _parse_configs(scheduling_rules_json_str: str) -> List[JobSchedulingRule]:
        rules: List[JobSchedulingRule] = json_utils.loads(scheduling_rules_json_str)
        return rules

    def handle_event(self, event: BaseEvent, task_state: object) -> Tuple[SchedulingAction, object]:
        rules = self._parse_configs(self.config)
        if SchedulerInnerEventType.TASK_STATUS_CHANGED.value == event.event_type:
            event = copy.deepcopy(event)
            event.value = _airflow_task_state_to_aiflow_status(event.value)
        if task_state is None:
            task_state = AiFlowTs(len(rules))
        af_ts = copy.deepcopy(task_state)
        af_ts.add_event(event)
        actions = self._check_rules(rules, af_ts)

        # pick the first triggered action
        for action in actions:
            if action is not None:
                scheduling_action = job_action_to_scheduling_action(action)
                logging.debug("AIFlowHandler {} handle event {} triggered action: {}"
                              .format(self.config, event, scheduling_action))
                return scheduling_action, af_ts

        logging.debug("AIFlowHandler {} handle event {} no action triggered return action {}"
                      .format(self.config, event, SchedulingAction.NONE))
        return SchedulingAction.NONE, af_ts

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

    def _check_rules(self, rules: List[JobSchedulingRule], ts: AiFlowTs) -> List[JobAction]:
        rule_states = ts.rule_states
        rules_num = len(rules)
        res: List[Optional[JobAction]] = [None] * rules_num
        for i in range(rules_num):
            rule = rules[i]
            rule_state = rule_states[i]
            if self._check_rule(rule, rule_state):
                rule_state.schedule_time = rule_state.latest_time
                res[i] = rule.action
        return res

    def _check_rule(self, rule: JobSchedulingRule, ts: SchedulingRuleState) -> bool:
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
