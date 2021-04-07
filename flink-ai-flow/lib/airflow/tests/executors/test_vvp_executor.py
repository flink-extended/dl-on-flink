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
import os
import unittest
from unittest import mock
import time

from airflow.models.serialized_dag import SerializedDagModel

from airflow.executors.scheduling_action import SchedulingAction
from airflow.models.dag import DagModel
from airflow.models.taskinstance import TaskInstance, TaskInstanceKey
from airflow.utils import timezone
from airflow.utils.state import State
from airflow.models.dagbag import DagBag
from airflow.utils.session import create_session
from airflow.executors.vvp_executor import VVPExecutor
from airflow.utils.vvp import DeploymentSpec
from tests.test_utils import db


class TestVVPExecutor(unittest.TestCase):
    def setUp(self):
        db.clear_db_jobs()
        db.clear_db_dags()
        db.clear_db_serialized_dags()
        db.clear_db_runs()
        db.clear_db_task_execution()

    def build_dag(self, session):
        DEFAULT_DATE = timezone.datetime(2020, 1, 1)
        dag_id = 'vvp_dag'
        task_id = 'op_1'
        dag_bag = DagBag(
            dag_folder='../dags/test_vvp_dag.py',
            include_examples=False,
        )

        dag = dag_bag.get_dag(dag_id)
        task = dag.get_task(task_id)
        dag.create_dagrun(
            run_id="vvp_dag_run",
            state=State.RUNNING,
            execution_date=DEFAULT_DATE,
            start_date=DEFAULT_DATE,
            session=session,
        )
        ti = TaskInstance(task=task, execution_date=DEFAULT_DATE)
        ti.state = State.SCHEDULED
        dag_model = DagModel(
            dag_id=dag_id,
            is_paused=False,
            concurrency=5,
            has_task_concurrency_limits=False,
        )
        s_dag = SerializedDagModel(dag=dag)
        session.merge(s_dag)
        session.merge(dag_model)
        session.merge(ti)
        session.commit()
        return ti

    def test_start_stop_task(self):
        with create_session() as session:
            ti = self.build_dag(session)
            vvp_executor = VVPExecutor(parallelism=3)
            vvp_executor.vvp_restful_util.start_deployment = mock.Mock(return_value=True)
            vvp_executor.vvp_restful_util.stop_deployment = mock.Mock(return_value=True)
            vvp_executor.start()
            vvp_executor.schedule_task(TaskInstanceKey(ti.dag_id, ti.task_id, ti.execution_date, ti.try_number),
                                       SchedulingAction.START)
            self.wait_queue_empty(vvp_executor)
            ti1 = self.get_ti_from_db(session, ti)
            self.assertEqual(State.RUNNING, ti1.state)
            vvp_executor.schedule_task(TaskInstanceKey(ti.dag_id, ti.task_id, ti.execution_date, ti.try_number),
                                       SchedulingAction.STOP)
            self.wait_queue_empty(vvp_executor)
            ti2 = self.get_ti_from_db(session, ti)
            self.assertEqual(State.KILLED, ti2.state)
            vvp_executor.end()

    def test_sync_executor(self):
        with create_session() as session:
            ti = self.build_dag(session)
            vvp_executor = VVPExecutor(parallelism=3)
            vvp_executor.vvp_restful_util.start_deployment = mock.Mock(return_value=True)
            vvp_executor.vvp_restful_util.stop_deployment = mock.Mock(return_value=True)
            vvp_executor.vvp_restful_util.get_namespaces = mock.Mock(return_value=['ns1'])
            vvp_executor.vvp_restful_util.list_deployments \
                = mock.Mock(return_value=[DeploymentSpec(id='dp_id', namespace='ns1', state='SUCCESS')])
            vvp_executor.start()
            vvp_executor.schedule_task(TaskInstanceKey(ti.dag_id, ti.task_id, ti.execution_date, ti.try_number),
                                       SchedulingAction.START)
            self.wait_queue_empty(vvp_executor)
            ti1 = self.get_ti_from_db(session, ti)
            self.assertEqual(State.RUNNING, ti1.state)
            vvp_executor.sync()
            ti2 = self.get_ti_from_db(session, ti)
            self.assertEqual(State.SUCCESS, ti2.state)
            vvp_executor.end()

    def test_recover_executor(self):
        with create_session() as session:
            ti = self.build_dag(session)
            vvp_executor = VVPExecutor(parallelism=3)
            vvp_executor.vvp_restful_util.start_deployment = mock.Mock(return_value=True)
            vvp_executor.vvp_restful_util.stop_deployment = mock.Mock(return_value=True)
            vvp_executor.vvp_restful_util.get_namespaces = mock.Mock(return_value=['ns1'])
            vvp_executor.vvp_restful_util.list_deployments \
                = mock.Mock(return_value=[DeploymentSpec(id='dp_id', namespace='ns1', state='SUCCESS')])
            vvp_executor.schedule_task(TaskInstanceKey(ti.dag_id, ti.task_id, ti.execution_date, ti.try_number),
                                       SchedulingAction.START)
            self.assertEqual(1, vvp_executor.queue.qsize())
            message = vvp_executor.queue.get()
            self.assertEqual(0, vvp_executor.queue.qsize())
            vvp_executor.recover_state()
            self.assertEqual(1, vvp_executor.queue.qsize())
            message = vvp_executor.queue.get()
            self.assertEqual(SchedulingAction.START, message[1])


    def wait_queue_empty(self, vvp_executor):
        while True:
            if vvp_executor.queue.qsize() == 0:
                break
            else:
                time.sleep(1)

    def get_ti_from_db(self, session, ti):
        return session.query(TaskInstance).filter(TaskInstance.dag_id == ti.dag_id,
                                                  TaskInstance.task_id == ti.task_id,
                                                  TaskInstance.execution_date == ti.execution_date).first()
