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

from airflow.utils.state import State

from ai_flow.workflow import status
from airflow.events.scheduler_events import SchedulerInnerEventType

from ai_flow.workflow.control_edge import ConditionConfig, ConditionType, EventLife, ValueCondition, TaskAction
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
    def __init__(self):
        # key: namespace event_type sender event_key
        # value: BaseEvent
        self.event_map = {}
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


class AIFlowHandler(EventHandler):
    """
    AIFlowHandler is an implementation of EventHandler,
    which implements the semantics of ai flow based on event scheduling.
    """
    def __init__(self, config: str):
        self.config = config

    @staticmethod
    def _parse_configs(config_str: str):
        configs: List[ConditionConfig] = []
        config_json = json.loads(config_str)
        for config in config_json:
            condition_config = ConditionConfig(event_key=config['event_key'],
                                               event_value=config['event_value'],
                                               event_type=config['event_type'],
                                               action=TaskAction(config['action']),
                                               condition_type=ConditionType(config['condition_type']),
                                               value_condition=ValueCondition(config['value_condition']),
                                               life=EventLife(config['life']),
                                               namespace=config['namespace'],
                                               sender=config['sender'])
            configs.append(condition_config)
        return configs

    def handle_event(self, event: BaseEvent, task_state: object) -> Tuple[SchedulingAction, object]:
        if SchedulerInnerEventType.TASK_STATUS_CHANGED.value == event.event_type:
            event = BaseEvent(**event.__dict__)
            event.value = _airflow_task_state_to_aiflow_status(event.value)
        configs: List[ConditionConfig] = AIFlowHandler._parse_configs(self.config)
        if task_state is None:
            task_state = AiFlowTs()
        af_ts = copy.deepcopy(task_state)
        af_ts.event_map[(event.namespace, event.event_type, event.sender, event.key)] = event
        af_ts.latest_time = event.create_time
        aw = ActionWrapper()
        res = self._check_condition(configs, af_ts, aw)
        if res:
            if SchedulingAction(aw.action) in SchedulingAction:
                af_ts.schedule_time = af_ts.latest_time
            if len(configs) == 0:
                logging.debug("AIFlowHandler {} handle event {}, action: {}".format(self.config, event, "START"))
                return SchedulingAction.START, af_ts
            else:
                logging.debug("AIFlowHandler {} handle event {}, action: {}".format(self.config, event,
                                                                                   SchedulingAction(aw.action)))
                return SchedulingAction(aw.action), af_ts
        else:
            logging.debug("AIFlowHandler {} handle event {}, action: {}".format(self.config, event, "NONE"))
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

    def _check_condition(self, configs, ts: AiFlowTs, aw: ActionWrapper) -> bool:
        event_map: Dict = ts.event_map
        schedule_time = ts.schedule_time
        has_necessary_edge = False
        for condition_config in configs:
            namespace = condition_config.namespace
            sender = condition_config.sender
            key = condition_config.event_key
            value = condition_config.event_value
            event_type = condition_config.event_type
            events = self._match_config_events(namespace, event_type, sender, key, event_map)
            if condition_config.condition_type == ConditionType.SUFFICIENT:
                if 0 == len(events):
                    continue
                for event in events:
                    v, event_time = event.value, event.create_time
                    if condition_config.life == EventLife.ONCE:
                        if condition_config.value_condition == ValueCondition.EQUALS:
                            if v == value and event_time > schedule_time:
                                aw.action = condition_config.action
                                return True
                        else:
                            if event_time > schedule_time:
                                aw.action = condition_config.action
                                return True
                    else:
                        if condition_config.value_condition == ValueCondition.EQUALS:
                            if v == value:
                                aw.action = condition_config.action
                                return True
                        else:
                            aw.action = condition_config.action
                            return True
            else:
                has_necessary_edge = True
                if 0 == len(events):
                    return False
                final_flag = False
                for event in events:
                    flag = True
                    v, event_time = event.value, event.create_time
                    if condition_config.life == EventLife.ONCE:
                        if condition_config.value_condition == ValueCondition.EQUALS:
                            if schedule_time >= event_time:
                                flag = False
                            else:
                                if v != value:
                                    flag = False
                        else:
                            if schedule_time >= event_time:
                                flag = False

                    else:
                        if condition_config.value_condition == ValueCondition.EQUALS:
                            if v != value:
                                flag = False

                        else:
                            if v is None:
                                flag = False
                    if flag:
                        final_flag = True
                        break
                if not final_flag:
                    return False

        if has_necessary_edge:
            aw.action = configs[0].action
            return True
        else:
            return False
