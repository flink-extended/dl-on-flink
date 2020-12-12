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
from enum import Enum
from airflow.utils.db import provide_session
from sqlalchemy import Column, Integer, PickleType, String
from airflow.models.base import Base, ID_LEN
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.sqlalchemy import UtcDateTime


class TaskAction(str, Enum):
    """
    NONE: No action needs to be taken.
    START: Start to initialize the task instance.
    RESTART: Start to initialize the task instance or stop running the task instance and
                       start the task instance.
    STOP: Stop running the task instance.
    """
    NONE = "NONE"
    START = "START"
    RESTART = "RESTART"
    STOP = "STOP"


START_ACTION = {
    TaskAction.START,
    TaskAction.RESTART,
}

SCHEDULED_ACTION = {
    TaskAction.START,
    TaskAction.RESTART,
    TaskAction.STOP
}


class TaskState(Base, LoggingMixin):
    __tablename__ = "task_state"

    task_id = Column(String(ID_LEN), primary_key=True)
    dag_id = Column(String(ID_LEN), primary_key=True)
    execution_date = Column(UtcDateTime, primary_key=True)
    ack_id = Column(Integer, nullable=True)
    task_state = Column(PickleType, nullable=True)
    event_handler = Column(PickleType, nullable=True)
    action = Column(String(32), nullable=True)

    def __init__(self, task_instance):
        super().__init__()
        self.task_id = task_instance.task_id
        self.dag_id = task_instance.dag_id
        self.execution_date = task_instance.execution_date
        self.ack_id = 0

    @classmethod
    @provide_session
    def query_task_state(cls, ti, session=None):
        return session.query(TaskState).filter(TaskState.dag_id == ti.dag_id,
                                               TaskState.task_id == ti.task_id,
                                               TaskState.execution_date == ti.execution_date).first()

    @classmethod
    def in_stop_or_restart(cls, action):
        return action is not None and (TaskAction(action) == TaskAction.RESTART
                                       or TaskAction(action) == TaskAction.STOP)


@provide_session
def action_is_stop_or_restart(ti, session=None) -> bool:
    ts = TaskState.query_task_state(ti, session)
    return TaskState.in_stop_or_restart(ts.action)
