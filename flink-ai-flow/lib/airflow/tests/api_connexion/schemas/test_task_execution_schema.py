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

import datetime as dt
import getpass
import unittest


from airflow.api_connexion.schemas.task_execution_schema import (
    task_execution_schema,
)
from airflow.models import DAG, SlaMiss, TaskInstance as TI
from airflow.models.taskexecution import TaskExecution
from airflow.operators.dummy import DummyOperator
from airflow.utils.session import create_session, provide_session
from airflow.utils.state import State
from airflow.utils.timezone import datetime


class TestTaskExecutionSchema(unittest.TestCase):
    def setUp(self):
        self.default_time = datetime(2020, 1, 1)
        with DAG(dag_id="TEST_DAG_ID"):
            self.task = DummyOperator(task_id="TEST_TASK_ID", start_date=self.default_time)

        self.default_ti_init = {
            "execution_date": self.default_time,
            "state": State.RUNNING,
        }
        self.default_ti_extras = {
            "start_date": self.default_time + dt.timedelta(days=1),
            "end_date": self.default_time + dt.timedelta(days=2),
            "pid": 100,
            "duration": 10000,
            "pool": "default_pool",
            "queue": "default_queue",
        }

    def tearDown(self):
        with create_session() as session:
            session.query(TaskExecution).delete()
            session.query(SlaMiss).delete()

    @provide_session
    def test_task_execution_schema_without_sla(self, session):
        ti = TI(task=self.task, **self.default_ti_init)
        for key, value in self.default_ti_extras.items():
            setattr(ti, key, value)
        te = TaskExecution(task_id=ti.task_id,
                           start_date=ti.start_date,
                           execution_date=ti.execution_date,
                           state=ti.state,
                           dag_id=ti.dag_id,
                           seq_num=ti.try_number,
                           end_date=ti.end_date,
                           duration=ti.duration,
                           hostname=ti.hostname,
                           unixname=ti.unixname,
                           job_id=ti.job_id,
                           pool_slots=ti.pool_slots,
                           pool=ti.pool,
                           queue=ti.queue,
                           priority_weight=ti.priority_weight,
                           operator=ti.operator,
                           queued_dttm=ti.queued_dttm,
                           queued_by_job_id=ti.queued_by_job_id,
                           pid=ti.pid,
                           executor_config=ti.executor_config)

        session.add(te)
        session.commit()
        serialized_te = task_execution_schema.dump((te, None))
        expected_json = {
            "dag_id": "TEST_DAG_ID",
            "duration": 10000.0,
            "end_date": "2020-01-03T00:00:00+00:00",
            "execution_date": "2020-01-01T00:00:00+00:00",
            "executor_config": "{}",
            "hostname": "",
            "operator": "DummyOperator",
            "pid": 100,
            "pool": "default_pool",
            "pool_slots": 1,
            "priority_weight": 1,
            "queue": "default_queue",
            "queued_when": None,
            "sla_miss": None,
            "start_date": "2020-01-02T00:00:00+00:00",
            "state": "running",
            "task_id": "TEST_TASK_ID",
            "seq_num": 0,
            "unixname": getpass.getuser(),
        }
        self.assertDictEqual(serialized_te, expected_json)

    @provide_session
    def test_task_instance_schema_with_sla(self, session):
        ti = TI(task=self.task, **self.default_ti_init)
        for key, value in self.default_ti_extras.items():
            setattr(ti, key, value)
        te = TaskExecution(task_id=ti.task_id,
                           start_date=ti.start_date,
                           execution_date=ti.execution_date,
                           state=ti.state,
                           dag_id=ti.dag_id,
                           seq_num=ti.try_number,
                           end_date=ti.end_date,
                           duration=ti.duration,
                           hostname=ti.hostname,
                           unixname=ti.unixname,
                           job_id=ti.job_id,
                           pool_slots=ti.pool_slots,
                           pool=ti.pool,
                           queue=ti.queue,
                           priority_weight=ti.priority_weight,
                           operator=ti.operator,
                           queued_dttm=ti.queued_dttm,
                           queued_by_job_id=ti.queued_by_job_id,
                           pid=ti.pid,
                           executor_config=ti.executor_config)
        sla_miss = SlaMiss(
            task_id="TEST_TASK_ID",
            dag_id="TEST_DAG_ID",
            execution_date=self.default_time,
        )
        session.add(ti)
        session.add(sla_miss)
        session.commit()
        serialized_te = task_execution_schema.dump((te, sla_miss))
        expected_json = {
            "dag_id": "TEST_DAG_ID",
            "duration": 10000.0,
            "end_date": "2020-01-03T00:00:00+00:00",
            "execution_date": "2020-01-01T00:00:00+00:00",
            "executor_config": "{}",
            "hostname": "",
            "operator": "DummyOperator",
            "pid": 100,
            "pool": "default_pool",
            "pool_slots": 1,
            "priority_weight": 1,
            "queue": "default_queue",
            "queued_when": None,
            "sla_miss": {
                "dag_id": "TEST_DAG_ID",
                "description": None,
                "email_sent": False,
                "execution_date": "2020-01-01T00:00:00+00:00",
                "notification_sent": False,
                "task_id": "TEST_TASK_ID",
                "timestamp": None,
            },
            "start_date": "2020-01-02T00:00:00+00:00",
            "state": "running",
            "task_id": "TEST_TASK_ID",
            "seq_num": 0,
            "unixname": getpass.getuser(),
        }
        self.assertDictEqual(serialized_te, expected_json)
