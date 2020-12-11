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

import unittest
from airflow.jobs.backfill_job import BackfillJob
from airflow import models, settings
from airflow.models import (
    DAG, TaskFail, TaskReschedule
)
from airflow.models.taskstate import TaskState
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils import timezone
from airflow.utils.db import create_session
from airflow.utils.state import State


class TaskStateTest(unittest.TestCase):

    def create_dag_run(self, dag,
                       state=State.RUNNING,
                       task_states=None,
                       execution_date=None,
                       is_backfill=False,
                       ):
        now = timezone.utcnow()
        if execution_date is None:
            execution_date = now
        if is_backfill:
            run_id = BackfillJob.ID_PREFIX + now.isoformat()
        else:
            run_id = 'manual__' + now.isoformat()
        dag_run = dag.create_dagrun(
            run_id=run_id,
            execution_date=execution_date,
            start_date=now,
            state=state,
            external_trigger=False,
        )

        if task_states is not None:
            session = settings.Session()
            for task_id, state in task_states.items():
                ti = dag_run.get_task_instance(task_id)
                ti.set_state(state, session)
            session.close()

        return dag_run

    def setUp(self):
        with create_session() as session:
            session.query(TaskFail).delete()
            session.query(TaskReschedule).delete()
            session.query(TaskState).delete()
            session.query(models.TaskInstance).delete()
            session.query(models.DagRun).delete()

    def tearDown(self):
        pass

    def test_add_taskstate(self):
        now = timezone.utcnow()
        session = settings.Session()
        dag_id = 'test_add_taskstate'
        dag = DAG(dag_id=dag_id, start_date=now)
        task0 = DummyOperator(task_id='backfill_task_0', owner='test', dag=dag)
        self.create_dag_run(dag, execution_date=now, is_backfill=True)
        count = session.query(TaskState).count()
        self.assertEqual(1, count)

