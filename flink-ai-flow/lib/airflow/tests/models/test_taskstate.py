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

from airflow.utils import timezone

from airflow.utils.session import create_session

from airflow.models.taskstate import TaskState
from tests.test_utils import db


class TestTaskState(unittest.TestCase):

    def setUp(self) -> None:
        self.dag_id = "1"
        self.task_id = "2"
        self.execution_date = timezone.datetime(2017, 1, 1)
        self._create_task_state(self.dag_id, self.task_id, self.execution_date)

    def tearDown(self) -> None:
        db.clear_db_task_state()

    def test_get_task_state(self):
        dag_id = self.dag_id
        task_id = self.task_id
        task_state = TaskState.get_task_state(dag_id, task_id, self.execution_date)
        assert task_state.dag_id == dag_id
        assert task_state.task_id == task_id

    def test_update_task_state(self):
        self._create_task_state("1", "2", self.execution_date)
        task_state = TaskState.get_task_state(self.dag_id, self.task_id, self.execution_date)
        task_state.state = 100
        task_state.update_task_state()
        task_state = TaskState.get_task_state(self.dag_id, self.task_id, self.execution_date)
        assert task_state.state == 100

    @staticmethod
    def _create_task_state(dag_id, task_id, execution_date):
        with create_session() as session:
            ts = TaskState(dag_id=dag_id, task_id=task_id, execution_date=execution_date)
            session.merge(ts)
            session.commit()
