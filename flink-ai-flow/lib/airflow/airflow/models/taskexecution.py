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
import dill
from airflow.utils.db import provide_session

from sqlalchemy import Column, Float, Integer, PickleType, String, func
from airflow.models.base import Base, ID_LEN
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.sqlalchemy import UtcDateTime


class TaskExecution(Base, LoggingMixin):

    __tablename__ = "task_execution"

    task_id = Column(String(ID_LEN), primary_key=True)
    dag_id = Column(String(ID_LEN), primary_key=True)
    execution_date = Column(UtcDateTime, primary_key=True)
    seq_num = Column(Integer, primary_key=True)
    start_date = Column(UtcDateTime)
    end_date = Column(UtcDateTime)
    duration = Column(Float)
    try_number = Column(Integer, default=0)
    hostname = Column(String(1000))
    job_id = Column(Integer)
    pool = Column(String(50), nullable=False)
    pool_slots = Column(Integer, default=1)
    queue = Column(String(256))
    queued_dttm = Column(UtcDateTime)
    pid = Column(Integer)

    def __init__(self, task):
        super().__init__()
        self.task_id = task.task_id
        self.dag_id = task.dag_id
        self.execution_date = task.execution_date
        self.seq_num = 0
        self.start_date = task.start_date
        self.end_date = task.end_date
        self.duration = task.duration
        self.try_number = task.try_number
        self.hostname = task.hostname
        self.job_id = task.job_id
        self.pool = task.pool
        self.pool_slots = task.pool_slots
        self.queue = task.queue
        self.queued_dttm = task.queued_dttm
        self.pid = task.pid

    @provide_session
    def add_to_db(self, session=None):
        def next_num():
            return session.query(TaskExecution)\
                       .filter(TaskExecution.dag_id == self.dag_id,
                               TaskExecution.task_id == self.task_id,
                               TaskExecution.execution_date == self.execution_date).count() + 1
        self.seq_num = next_num()
        session.add(self)
        session.commit()

    def __str__(self):
        return "dag_id:{0} task_id:{1} execution_date:{2} seq_num:{3}"\
            .format(self.dag_id, self.task_id, self.execution_date, self.seq_num)


