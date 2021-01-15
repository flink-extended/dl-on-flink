# -*- coding: utf-8 -*-
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

from enum import Enum

from notification_service.base_notification import BaseEvent

from airflow.utils.state import State


class EventType(str, Enum):
    """
    DAG_RUN_EXECUTABLE: schedule a new DagRun
    DAG_RUN_FINISHED: a DagRun finished
    TASK_STATUS_CHANGED: TaskInstance status changed
    UNDEFINED: Some event happened
    STOP_SCHEDULER_CMD: Stop the scheduler only used in test mode
    """
    DAG_RUN_EXECUTABLE = "DAG_RUN_EXECUTABLE"
    DAG_RUN_FINISHED = "DAG_RUN_FINISHED"
    TASK_STATUS_CHANGED = "TASK_STATUS_CHANGED"
    UNDEFINED = "UNDEFINED"
    STOP_SCHEDULER_CMD = "STOP_SCHEDULER_CMD"

    @staticmethod
    def is_in(ss):
        if ss == EventType.DAG_RUN_EXECUTABLE.value \
            or ss == EventType.TASK_STATUS_CHANGED.value \
            or ss == EventType.UNDEFINED.value \
            or ss == EventType.DAG_RUN_FINISHED.value\
            or ss == EventType.STOP_SCHEDULER_CMD.value:
            return True
        else:
            return False


class Event(BaseEvent):
    """
    Event describes an event in the workflow.
    """
    pass


class DagRunEvent(Event):
    def __init__(self, dag_run_id: int, simple_dag):
        super().__init__(str(dag_run_id), "", EventType.DAG_RUN_EXECUTABLE)
        self.simple_dag = simple_dag


class DagRunFinishedEvent(Event):
    def __init__(self, dag_run_id: int, state=State.SUCCESS):
        super().__init__(str(dag_run_id), str(state), EventType.DAG_RUN_FINISHED)


class StopSchedulerCMDEvent(Event):

    def __init__(self):
        super().__init__("", "", EventType.STOP_SCHEDULER_CMD)


class TaskInstanceHelper(object):
    @classmethod
    def _utf_time_format(cls):
        return '%Y-%m-%dT%H:%M:%S.%fZ'

    @classmethod
    def to_task_key(cls, dag_id, task_id, execution_date):
        import json
        t_key = {}
        t_key['dag_id'] = dag_id
        t_key['task_id'] = task_id
        t_key['execution_date'] = execution_date.strftime(cls._utf_time_format())
        return json.dumps(t_key)

    @classmethod
    def from_task_key(cls, str):
        import json
        import pytz
        from datetime import datetime
        json_object = json.loads(str)
        return json_object['dag_id'], \
               json_object['task_id'], \
               datetime.strptime(json_object['execution_date'], cls._utf_time_format()).replace(tzinfo=pytz.utc)

    @classmethod
    def to_event_value(cls, state, try_number):
        import json
        t_value = {}
        t_value['try_num'] = try_number
        t_value['state'] = state
        return json.dumps(t_value)

    @classmethod
    def from_event_value(cls, str):
        import json
        json_object = json.loads(str)
        return json_object['state'], json_object['try_num']


class TaskStatusEvent(Event):

    def __init__(self, task_instance_key: str, status: str):
        super().__init__(task_instance_key, status, EventType.TASK_STATUS_CHANGED, None, None)


class EventState(object):
    def __init__(self, event_key):
        self.event_key = event_key
        self.event_version_list = []


class EventStateBag(object):
    def __init__(self):
        self.event_states = {}


def event_model_list_to_events(event_model_list):
    events = []
    if event_model_list is not None:
        for event_model in event_model_list:
            event = Event(key=event_model.key, value=event_model.value,
                          event_type=event_model.event_type, version=event_model.version,
                          create_time=event_model.create_time)
            events.append(event)
    return events
