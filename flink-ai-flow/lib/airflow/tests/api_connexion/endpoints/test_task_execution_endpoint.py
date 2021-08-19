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

from airflow.models import DagBag, DagRun, SlaMiss, TaskInstance
from airflow.models.taskexecution import TaskExecution
from airflow.security import permissions
from airflow.utils.session import provide_session
from airflow.utils.state import State
from airflow.utils.timezone import datetime
from airflow.utils.types import DagRunType
from airflow.www import app
from tests.test_utils.api_connexion_utils import assert_401, create_user, delete_user
from tests.test_utils.config import conf_vars
from tests.test_utils.db import clear_db_runs, clear_db_sla_miss, clear_db_task_execution

DEFAULT_DATETIME_1 = datetime(2020, 1, 1)
DEFAULT_DATETIME_STR_1 = "2020-01-01T00:00:00+00:00"
DEFAULT_DATETIME_STR_2 = "2020-01-02T00:00:00+00:00"


class TestTaskExecutionEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        with conf_vars({("api", "auth_backend"): "tests.test_utils.remote_user_api_auth_backend"}):
            cls.app = app.create_app(testing=True)  # type:ignore
        create_user(
            cls.app,  # type: ignore
            username="test",
            role_name="Test",
            permissions=[
                (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
                (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG_RUN),
                (permissions.ACTION_CAN_READ, permissions.RESOURCE_TASK_INSTANCE),
                (permissions.ACTION_CAN_EDIT, permissions.RESOURCE_TASK_INSTANCE),
                (permissions.ACTION_CAN_READ, permissions.RESOURCE_TASK_EXECUTION),
                (permissions.ACTION_CAN_EDIT, permissions.RESOURCE_TASK_EXECUTION),
            ],
        )
        create_user(cls.app, username="test_no_permissions", role_name="TestNoPermissions")  # type: ignore

    @classmethod
    def tearDownClass(cls) -> None:
        delete_user(cls.app, username="test")  # type: ignore
        cls.app = app.create_app(testing=True)  # type:ignore

    def setUp(self) -> None:
        self.default_time = DEFAULT_DATETIME_1
        self.ti_init = {
            "execution_date": self.default_time,
            "state": State.RUNNING,
        }
        self.ti_extras = {
            "start_date": self.default_time + dt.timedelta(days=1),
            "end_date": self.default_time + dt.timedelta(days=2),
            "pid": 100,
            "duration": 10000,
            "pool": "default_pool",
            "queue": "default_queue",
            "job_id": 0,
        }
        self.client = self.app.test_client()  # type:ignore
        clear_db_runs()
        clear_db_task_execution()
        clear_db_sla_miss()
        DagBag(include_examples=True, read_dags_from_db=False).sync_to_db()
        self.dagbag = DagBag(include_examples=True, read_dags_from_db=True)

    def create_task_executions(
        self,
        session,
        dag_id: str = "example_python_operator",
        update_extras: bool = True,
        single_dag_run: bool = True,
        task_instances=None,
        dag_run_state=State.RUNNING,
    ):
        """Method to create task instances using kwargs and default arguments"""

        dag = self.dagbag.get_dag(dag_id)
        tasks = dag.tasks
        counter = len(tasks)
        if task_instances is not None:
            counter = min(len(task_instances), counter)

        for i in range(counter):
            if task_instances is None:
                pass
            elif update_extras:
                self.ti_extras.update(task_instances[i])
            else:
                self.ti_init.update(task_instances[i])
            ti = TaskInstance(task=tasks[i], **self.ti_init)

            for key, value in self.ti_extras.items():
                setattr(ti, key, value)
            session.add(ti)

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

            if single_dag_run is False:
                dr = DagRun(
                    dag_id=dag_id,
                    run_id=f"TEST_DAG_RUN_ID_{i}",
                    execution_date=self.ti_init["execution_date"],
                    run_type=DagRunType.MANUAL.value,
                    state=dag_run_state,
                )
                session.add(dr)

        if single_dag_run:
            dr = DagRun(
                dag_id=dag_id,
                run_id="TEST_DAG_RUN_ID",
                execution_date=self.default_time,
                run_type=DagRunType.MANUAL.value,
                state=dag_run_state,
            )
            session.add(dr)
        session.commit()


class TestListTaskExecutions(TestTaskExecutionEndpoint):
    @provide_session
    def test_should_respond_200_list_task_execution(self, session):
        self.create_task_executions(session)
        response = self.client.get(
            "/api/v1/dags/example_python_operator/dagRuns/TEST_DAG_RUN_ID/taskExecutions",
            environ_overrides={"REMOTE_USER": "test"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json['task_executions'][0],
            {
                "dag_id": "example_python_operator",
                "duration": 10000.0,
                "end_date": "2020-01-03T00:00:00+00:00",
                "execution_date": "2020-01-01T00:00:00+00:00",
                "executor_config": "{}",
                "hostname": "",
                "operator": "PythonOperator",
                "pid": 100,
                "pool": "default_pool",
                "pool_slots": 1,
                "priority_weight": 6,
                "queue": "default_queue",
                "queued_when": None,
                "sla_miss": None,
                "start_date": "2020-01-02T00:00:00+00:00",
                "state": "running",
                "task_id": "print_the_context",
                "seq_num": 0,
                "unixname": getpass.getuser(),
            },
        )

    @provide_session
    def test_should_respond_200_list_task_execution_with_sla(self, session):
        self.create_task_executions(session)
        session.query()
        sla_miss = SlaMiss(
            task_id="print_the_context",
            dag_id="example_python_operator",
            execution_date=self.default_time,
            timestamp=self.default_time,
        )
        session.add(sla_miss)
        session.commit()
        response = self.client.get(
            "/api/v1/dags/example_python_operator/dagRuns/TEST_DAG_RUN_ID/taskExecutions",
            environ_overrides={"REMOTE_USER": "test"},
        )
        self.assertEqual(response.status_code, 200)

        self.assertDictEqual(
            response.json['task_executions'][0],
            {
                "dag_id": "example_python_operator",
                "duration": 10000.0,
                "end_date": "2020-01-03T00:00:00+00:00",
                "execution_date": "2020-01-01T00:00:00+00:00",
                "executor_config": "{}",
                "hostname": "",
                "operator": "PythonOperator",
                "pid": 100,
                "pool": "default_pool",
                "pool_slots": 1,
                "priority_weight": 6,
                "queue": "default_queue",
                "queued_when": None,
                "sla_miss": {
                    "dag_id": "example_python_operator",
                    "description": None,
                    "email_sent": False,
                    "execution_date": "2020-01-01T00:00:00+00:00",
                    "notification_sent": False,
                    "task_id": "print_the_context",
                    "timestamp": "2020-01-01T00:00:00+00:00",
                },
                "start_date": "2020-01-02T00:00:00+00:00",
                "state": "running",
                "task_id": "print_the_context",
                "seq_num": 0,
                "unixname": getpass.getuser(),
            },
        )

    @provide_session
    def test_should_respond_200_get_task_executions(self, session):
        self.create_task_executions(session)
        response = self.client.get(
            "/api/v1/dags/example_python_operator/dagRuns/TEST_DAG_RUN_ID/taskInstances/print_the_context/taskExecutions",
            environ_overrides={"REMOTE_USER": "test"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json['task_executions'][0],
            {
                "dag_id": "example_python_operator",
                "duration": 10000.0,
                "end_date": "2020-01-03T00:00:00+00:00",
                "execution_date": "2020-01-01T00:00:00+00:00",
                "executor_config": "{}",
                "hostname": "",
                "operator": "PythonOperator",
                "pid": 100,
                "pool": "default_pool",
                "pool_slots": 1,
                "priority_weight": 6,
                "queue": "default_queue",
                "queued_when": None,
                "sla_miss": None,
                "start_date": "2020-01-02T00:00:00+00:00",
                "state": "running",
                "task_id": "print_the_context",
                "seq_num": 0,
                "unixname": getpass.getuser(),
            },
        )

    @provide_session
    def test_should_respond_200_get_task_executions_with_sla(self, session):
        self.create_task_executions(session)
        session.query()
        sla_miss = SlaMiss(
            task_id="print_the_context",
            dag_id="example_python_operator",
            execution_date=self.default_time,
            timestamp=self.default_time,
        )
        session.add(sla_miss)
        session.commit()
        response = self.client.get(
            "/api/v1/dags/example_python_operator/dagRuns/TEST_DAG_RUN_ID/taskInstances/print_the_context/taskExecutions",
            environ_overrides={"REMOTE_USER": "test"},
        )
        self.assertEqual(response.status_code, 200)

        self.assertDictEqual(
            response.json['task_executions'][0],
            {
                "dag_id": "example_python_operator",
                "duration": 10000.0,
                "end_date": "2020-01-03T00:00:00+00:00",
                "execution_date": "2020-01-01T00:00:00+00:00",
                "executor_config": "{}",
                "hostname": "",
                "operator": "PythonOperator",
                "pid": 100,
                "pool": "default_pool",
                "pool_slots": 1,
                "priority_weight": 6,
                "queue": "default_queue",
                "queued_when": None,
                "sla_miss": {
                    "dag_id": "example_python_operator",
                    "description": None,
                    "email_sent": False,
                    "execution_date": "2020-01-01T00:00:00+00:00",
                    "notification_sent": False,
                    "task_id": "print_the_context",
                    "timestamp": "2020-01-01T00:00:00+00:00",
                },
                "start_date": "2020-01-02T00:00:00+00:00",
                "state": "running",
                "task_id": "print_the_context",
                "seq_num": 0,
                "unixname": getpass.getuser(),
            },
        )

    def test_should_raises_401_unauthenticated(self):
        response = self.client.get(
            "api/v1/dags/example_python_operator/dagRuns/TEST_DAG_RUN_ID/taskInstances/print_the_context/taskExecutions"
        )
        assert_401(response)

    def test_should_raise_403_forbidden(self):
        response = self.client.get(
            "api/v1/dags/example_python_operator/dagRuns/TEST_DAG_RUN_ID/taskInstances/print_the_context/taskExecutions",
            environ_overrides={'REMOTE_USER': "test_no_permissions"},
        )
        assert response.status_code == 403
