# -*- coding: utf-8 -*-
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

import json
import copy
from enum import Enum
from typing import List, Dict, Text
import time
from notification_service.base_notification import BaseEvent, UNDEFINED_EVENT_TYPE
from airflow.models import TaskInstance
from airflow.models.baseoperator import EventMetHandler
from airflow.models.taskstate import TaskState
from airflow.executors.scheduling_action import SchedulingAction


class MetCondition(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    NECESSARY = "NECESSARY"


class EventLife(str, Enum):
    """
    ONCE: the event value will be used only once
    REPEATED: the event value will be used repeated
    """
    ONCE = "ONCE"
    REPEATED = "REPEATED"


class MetValueCondition(str, Enum):
    """
    EQUAL: the condition that notification service updates a value which equals to the event value
    UPDATE: the condition that notification service has a update operation on the event key which event
            value belongs to
    """
    EQUAL = "EQUAL"
    UPDATE = "UPDATE"


class MetConfig(object):
    def __init__(self,
                 event_key: Text,
                 event_value: Text,
                 event_type: Text = UNDEFINED_EVENT_TYPE,
                 condition: MetCondition = MetCondition.NECESSARY,
                 action: SchedulingAction = SchedulingAction.START,
                 life: EventLife = EventLife.ONCE,
                 value_condition: MetValueCondition = MetValueCondition.EQUAL
                 ):
        self.event_type = event_type
        self.event_key = event_key
        self.event_value = event_value
        self.condition = condition
        self.action = action
        self.life = life
        self.value_condition = value_condition


class AiFlowTs(object):
    def __init__(self):
        self.event_map = {}
        self.schedule_time = 0

    def __str__(self):
        return "EVENT_MAP: {0} TIME: {1}".format(self.event_map, self.schedule_time)


class ActionWrapper(object):
    def __init__(self, action=SchedulingAction.NONE):
        self.action = action


class AIFlowMetHandler(EventMetHandler):
    def __init__(self, config_str: str):
        self.configs: List[MetConfig] = AIFlowMetHandler.parse_configs(config_str)

    @staticmethod
    def parse_configs(config_str: str):
        configs: List[MetConfig] = []
        config_json = json.loads(config_str)
        for config in config_json:
            met_config = MetConfig(event_key=config['event_key'],
                                   event_value=config['event_value'],
                                   event_type=config['event_type'],
                                   action=SchedulingAction(config['action']),
                                   condition=MetCondition(config['condition']),
                                   value_condition=MetValueCondition(config['value_condition']),
                                   life=EventLife(config['life']))
            configs.append(met_config)
        return configs

    def handle_event(self, event: BaseEvent, ti: TaskInstance, ts: TaskState, session=None) -> SchedulingAction:

        if ts.task_state is None:
            ts.task_state = AiFlowTs()
        af_ts = copy.deepcopy(ts.task_state)
        af_ts.event_map[(event.key, event.event_type)] = event
        aw = ActionWrapper()
        res = self.met_sc(af_ts, aw)
        if res:
            if aw.action in SchedulingAction:
                af_ts.schedule_time = time.time_ns()
            ts.task_state = af_ts
            session.merge(ts)
            session.commit()
            if len(self.configs) == 0:
                return SchedulingAction.START
            else:
                return aw.action
        else:
            ts.task_state = af_ts
            session.merge(ts)
            session.commit()
            return SchedulingAction.NONE

    def met_sc(self, ts: AiFlowTs, aw: ActionWrapper)->bool:
        event_map: Dict = ts.event_map
        schedule_time = ts.schedule_time
        has_necessary_edge = False
        for met_config in self.configs:
            key = met_config.event_key
            value = met_config.event_value
            event_type = met_config.event_type

            if met_config.condition == MetCondition.SUFFICIENT:
                if (key, event_type) not in event_map:
                    continue
                event: BaseEvent = event_map[(key, event_type)]
                v, event_time = event.value, event.create_time
                if met_config.life == EventLife.ONCE:
                    if met_config.value_condition == MetValueCondition.EQUAL:
                        if v == value and event_time > schedule_time:
                            aw.action = met_config.action
                            return True
                    else:
                        if event_time > schedule_time:
                            aw.action = met_config.action
                            return True
                else:
                    if met_config.value_condition == MetValueCondition.EQUAL:
                        if v == value:
                            aw.action = met_config.action
                            return True
                    else:
                        aw.action = met_config.action
                        return True
            else:
                has_necessary_edge = True
                if (key, event_type) not in event_map:
                    return False
                event: BaseEvent = event_map[(key, event_type)]
                v, event_time = event.value, event.create_time
                if met_config.life == EventLife.ONCE:
                    if met_config.value_condition == MetValueCondition.EQUAL:
                        if schedule_time >= event_time:
                            return False
                        else:
                            if v != value:
                                return False
                    else:
                        if schedule_time >= event_time:
                            return False

                else:
                    if met_config.value_condition == MetValueCondition.EQUAL:
                        if v != value:
                            return False

                    else:
                        if v is None:
                            return False
        if has_necessary_edge:
            aw.action = self.configs[0].action
            return True
        else:
            return False
