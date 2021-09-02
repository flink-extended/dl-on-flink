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
from typing import Text

import dill
from airflow.utils.session import provide_session

from sqlalchemy import Column, PickleType, String, Integer, Float, Text as SqlText
from airflow.models.base import COLLATION_ARGS, ID_LEN, Base
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.sqlalchemy import UtcDateTime


class TaskExecution(Base, LoggingMixin):
    __tablename__ = "task_execution"

    task_id = Column(String(ID_LEN, **COLLATION_ARGS), primary_key=True)
    dag_id = Column(String(ID_LEN, **COLLATION_ARGS), primary_key=True)
    execution_date = Column(UtcDateTime, primary_key=True)
    seq_num = Column(Integer, primary_key=True)
    start_date = Column(UtcDateTime)
    end_date = Column(UtcDateTime)
    duration = Column(Float)
    state = Column(String(20))
    hostname = Column(String(1000))
    unixname = Column(String(1000))
    job_id = Column(Integer)
    pool = Column(String(50), nullable=False)
    pool_slots = Column(Integer, default=1)
    queue = Column(String(256))
    priority_weight = Column(Integer)
    operator = Column(String(1000))
    queued_dttm = Column(UtcDateTime)
    queued_by_job_id = Column(Integer)
    pid = Column(Integer)
    executor_config = Column(PickleType(pickler=dill))
    execution_label = Column(SqlText)

    def __init__(self,
                 task_id,
                 dag_id,
                 execution_date,
                 seq_num,
                 start_date,
                 end_date,
                 duration,
                 state,
                 hostname,
                 unixname,
                 job_id,
                 pool,
                 pool_slots,
                 queue,
                 priority_weight,
                 operator,
                 queued_dttm,
                 queued_by_job_id,
                 pid,
                 executor_config):
        super().__init__()
        self.dag_id = dag_id
        self.task_id = task_id
        self.execution_date = execution_date
        self.seq_num = seq_num
        self.start_date = start_date
        self.end_date = end_date
        self.duration = duration
        self.state = state
        self.hostname = hostname
        self.unixname = unixname
        self.job_id = job_id
        self.pool = pool
        self.pool_slots = pool_slots
        self.queue = queue
        self.priority_weight = priority_weight
        self.operator = operator
        self.queued_dttm = queued_dttm
        self.queued_by_job_id = queued_by_job_id
        self.pid = pid
        self.executor_config = executor_config
        self._log = logging.getLogger("airflow.task")

    @provide_session
    def update_task_execution_label(self, label: Text, session=None):
        self.execution_label = label
        session.merge(self)
        session.commit()

    def __repr__(self):
        return f"<TaskExecution: {self.dag_id}.{self.task_id} {self.execution_date} {self.seq_num} [{self.state}]>"
