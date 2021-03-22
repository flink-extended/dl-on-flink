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
from __future__ import annotations

import logging
from datetime import datetime

import dill
from sqlalchemy.orm import Session

from airflow.utils.session import provide_session

from sqlalchemy import Column, PickleType, String
from airflow.models.base import COLLATION_ARGS, ID_LEN, Base
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.sqlalchemy import UtcDateTime


class TaskState(Base, LoggingMixin):
    __tablename__ = "task_state"

    task_id = Column(String(ID_LEN, **COLLATION_ARGS), primary_key=True)
    dag_id = Column(String(ID_LEN, **COLLATION_ARGS), primary_key=True)
    execution_date = Column(UtcDateTime, primary_key=True)
    task_state = Column(PickleType(pickler=dill))

    def __init__(self, task_id, dag_id, execution_date, task_state=None):
        super().__init__()
        self.dag_id = dag_id
        self.task_id = task_id
        self.execution_date = execution_date
        self._log = logging.getLogger("airflow.task")
        if task_state:
            self.task_state = task_state

    @staticmethod
    @provide_session
    def get_task_state(dag_id: str, task_id: str, executor_date: datetime, session: Session = None) -> TaskState:
        return session.query(TaskState).filter(TaskState.dag_id == dag_id,
                                               TaskState.task_id == task_id,
                                               TaskState.execution_date == executor_date).first()

    @provide_session
    def update_task_state(self, session: Session = None):
        session.merge(self)
        session.commit()

