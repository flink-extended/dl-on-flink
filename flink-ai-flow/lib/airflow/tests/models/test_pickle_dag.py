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

"""Unit tests for SerializedDagModel."""

import unittest

from airflow.models import TaskInstance
from airflow.models.baseoperator import EventMetHandler
from airflow.models.dagpickle import DagPickle

from airflow.models.taskstate import TaskAction, TaskState
from airflow.operators.dummy_operator import DummyOperator
from airflow.models.dag import DAG
from airflow.utils import db, timezone


def clear_db_serialized_dags():
    with db.create_session() as session:
        session.query(DagPickle).delete()


class TestHandler(EventMetHandler):

    def met(self, ti: TaskInstance, ts: TaskState) -> TaskAction:
        return TaskAction.START


class DagPickleTest(unittest.TestCase):
    """Unit tests for SerializedDagModel."""

    def setUp(self):
        clear_db_serialized_dags()

    def tearDown(self):
        clear_db_serialized_dags()

    def test_event_op_pickle_dag_read_write(self):
        now = timezone.utcnow()
        dag_id = 'test_add_taskstate_0'
        dag = DAG(dag_id=dag_id, start_date=now)
        task0 = DummyOperator(task_id='backfill_task_0', owner='test', dag=dag)
        task0.add_event_dependency('key', "EVENT")
        task0.set_event_met_handler(TestHandler())
        with db.create_session() as session:
            p_dag = DagPickle(dag)
            session.add(p_dag)
            session.commit()
            pp_dag = session.query(DagPickle).first()
        self.assertEqual(dag_id, pp_dag.dag_id)
        self.assertEqual(1, len(pp_dag.pickle.task_dict["backfill_task_0"].event_dependencies()))
