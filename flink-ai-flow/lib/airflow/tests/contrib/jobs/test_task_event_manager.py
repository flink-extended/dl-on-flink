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
import datetime
import time
import unittest
from typing import Tuple

from notification_service.base_notification import BaseEvent

from airflow.contrib.jobs.dagrun_event_manager import DagRunEventExecutor, EventHandleResult, \
    DagRunEventManager, DagRunEventExecutorRunner, DagRunId
from airflow.executors.scheduling_action import SchedulingAction
from airflow.models import DagBag, DagRun
from airflow.models.serialized_dag import SerializedDagModel
from airflow.models.taskstate import TaskState
from airflow.utils import timezone
from airflow.utils.mailbox import Mailbox
from airflow.utils.state import State
from airflow.utils.types import DagRunType
from tests.test_utils import db


class EventHandlerTestBase(unittest.TestCase):
    def setUp(self) -> None:
        db.clear_db_runs()
        db.clear_db_task_state()
        db.clear_db_serialized_dags()
        self._serialized_dag, self._dag_run = self.init_dag_and_dag_run('../../dags/test_task_event_handler_dag.py',
                                                                        'test_event_handler',
                                                                        timezone.datetime(2017, 1, 1))

    @staticmethod
    def init_dag_and_dag_run(dag_file: str,
                             dag_id: str,
                             execution_date: datetime.datetime) -> Tuple[SerializedDagModel, DagRun]:
        dags = DagBag(dag_folder=dag_file).dags

        dag = dags[dag_id]
        SerializedDagModel.write_dag(dag)
        serialized_dag = SerializedDagModel.get(dag.dag_id)
        dag_run = dag.create_dagrun(run_type=DagRunType.MANUAL,
                                    execution_date=execution_date,
                                    state=State.RUNNING)
        return serialized_dag, dag_run

    @staticmethod
    def create_task_state(dag_run: DagRun, task_id: str):
        TaskState(dag_id=dag_run.dag_id,
                  task_id=task_id,
                  execution_date=dag_run.execution_date).update_task_state()


class TestDagRunEventManager(EventHandlerTestBase):
    def test_dag_run_event_manager(self):
        mailbox = Mailbox()
        event_manager = DagRunEventManager(mailbox)
        event_manager.start()

        self.create_task_state(dag_run=self._dag_run, task_id='operator_toggle_handler')
        event = BaseEvent("test_event", "test_event", namespace="default")

        event_manager.handle_event(DagRunId(self._dag_run.dag_id, self._dag_run.run_id), event)
        event_manager.handle_event(DagRunId(self._dag_run.dag_id, self._dag_run.run_id), event)

        handle_event = mailbox.get_message()
        message = EventHandleResult.from_event(handle_event)
        assert message == EventHandleResult(DagRunId(self._dag_run.dag_id, self._dag_run.run_id), "operator_toggle_handler", SchedulingAction.START)

        handle_event = mailbox.get_message()
        message = EventHandleResult.from_event(handle_event)
        assert message == EventHandleResult(DagRunId(self._dag_run.dag_id, self._dag_run.run_id), "operator_toggle_handler", SchedulingAction.STOP)

        time.sleep(2)
        event_manager.handle_event(DagRunId(self._dag_run.dag_id, self._dag_run.run_id), event)
        handle_event = mailbox.get_message()
        message = EventHandleResult.from_event(handle_event)
        assert message == EventHandleResult(DagRunId(self._dag_run.dag_id, self._dag_run.run_id), "operator_toggle_handler", SchedulingAction.START)
        event_manager.end()

    def test_dag_run_event_manager_resubmit_if_exit_with_nonempty_queue(self):
        mailbox = Mailbox()
        event_manager = DagRunEventManager(mailbox, max_num_event=1)
        event_manager.start()

        self.create_task_state(dag_run=self._dag_run, task_id='operator_toggle_handler')
        event = BaseEvent("test_event", "test_event", namespace="default")
        event_manager.handle_event(DagRunId(self._dag_run.dag_id, self._dag_run.run_id), event)
        event_manager.handle_event(DagRunId(self._dag_run.dag_id, self._dag_run.run_id), event)

        assert mailbox.get_message() is not None
        assert mailbox.get_message_with_timeout(5) is not None

    def test_dag_run_event_manager_multiple_dag_runs(self):
        dag_run1 = self._dag_run
        _, dag_run2 = self.init_dag_and_dag_run('../../dags/test_task_event_handler_dag.py',
                                                'test_event_handler', timezone.datetime(2017, 1, 2))
        self.create_task_state(dag_run1, 'operator_toggle_handler')
        self.create_task_state(dag_run2, 'operator_toggle_handler')

        event = BaseEvent("test_event", "test_event", namespace="default")
        mailbox = Mailbox()

        event_manager = DagRunEventManager(mailbox=mailbox)
        event_manager.handle_event(DagRunId(dag_run1.dag_id, dag_run1.run_id), event)
        event_manager.handle_event(DagRunId(dag_run2.dag_id, dag_run2.run_id), event)
        messages = [EventHandleResult.from_event(mailbox.get_message()),
                    EventHandleResult.from_event(mailbox.get_message())]
        assert EventHandleResult(DagRunId(dag_run1.dag_id, dag_run1.run_id), "operator_toggle_handler", SchedulingAction.START) in messages
        assert EventHandleResult(DagRunId(dag_run2.dag_id, dag_run2.run_id), "operator_toggle_handler", SchedulingAction.START) in messages

        event_manager.handle_event(DagRunId(dag_run1.dag_id, dag_run1.run_id), event)
        event_manager.handle_event(DagRunId(dag_run2.dag_id, dag_run2.run_id), event)
        messages = [EventHandleResult.from_event(mailbox.get_message()),
                    EventHandleResult.from_event(mailbox.get_message())]
        assert EventHandleResult(DagRunId(dag_run1.dag_id, dag_run1.run_id), "operator_toggle_handler", SchedulingAction.STOP) in messages
        assert EventHandleResult(DagRunId(dag_run2.dag_id, dag_run2.run_id), "operator_toggle_handler", SchedulingAction.STOP) in messages

        event_manager.end()

    def test_dag_run_event_manager_release_runner(self):
        dag_run1 = self._dag_run
        _, dag_run2 = self.init_dag_and_dag_run('../../dags/test_task_event_handler_dag.py',
                                                'test_event_handler', timezone.datetime(2017, 1, 2))
        self.create_task_state(dag_run1, 'operator_toggle_handler')
        self.create_task_state(dag_run2, 'operator_toggle_handler')

        event = BaseEvent("test_event", "test_event", namespace="default")
        mailbox = Mailbox()

        event_manager = DagRunEventManager(mailbox=mailbox)
        event_manager.handle_event(DagRunId(dag_run1.dag_id, dag_run1.run_id), event)

        time.sleep(5)
        event_manager.handle_event(DagRunId(dag_run1.dag_id, dag_run2.run_id), event)
        assert (DagRunId(dag_run2.dag_id, dag_run2.run_id)) in event_manager._event_executor_runners
        assert (DagRunId(dag_run1.dag_id, dag_run1.run_id)) not in event_manager._event_executor_runners

        event_manager.end()


class TestTaskEventExecutorRunner(EventHandlerTestBase):

    def test_task_event_executor_runner(self):
        event = BaseEvent("test_event", "test_event", namespace="default")

        self.create_task_state(dag_run=self._dag_run, task_id='operator_toggle_handler')

        mailbox = Mailbox()
        executor_runner = DagRunEventExecutorRunner(mailbox, DagRunId(self._dag_run.dag_id, self._dag_run.run_id), 10)
        executor_runner.put_event(event)
        executor_runner.put_event(event)

        executor_runner.run()
        handle_event = mailbox.get_message()
        message = EventHandleResult.from_event(handle_event)
        assert message == EventHandleResult(DagRunId(self._dag_run.dag_id, self._dag_run.run_id),
                                            "operator_toggle_handler", SchedulingAction.START)

        handle_event = mailbox.get_message()
        message = EventHandleResult.from_event(handle_event)
        assert message == EventHandleResult(DagRunId(self._dag_run.dag_id, self._dag_run.run_id),
                                            "operator_toggle_handler", SchedulingAction.STOP)

    def test_task_event_executor_runner_max_event(self):
        event = BaseEvent("test_event", "test_event", namespace="default")

        self.create_task_state(dag_run=self._dag_run, task_id='operator_toggle_handler')

        mailbox = Mailbox()

        executor_runner = DagRunEventExecutorRunner(mailbox, DagRunId(self._dag_run.dag_id, self._dag_run.run_id), 5)
        for i in range(10):
            executor_runner.put_event(event)

        executor_runner.run()

        messages = []
        for i in range(5):
            messages.append(mailbox.get_message())

        assert executor_runner._event_queue.qsize() == 5


class TestTaskEventExecutor(EventHandlerTestBase):

    def test_execute_event_handler(self):
        event = BaseEvent("test_event", "test_event", namespace="default")

        self.create_task_state(dag_run=self._dag_run, task_id='operator_toggle_handler')

        event_executor = DagRunEventExecutor(self._serialized_dag)
        actions = event_executor.execute_event_handler(self._dag_run, event=event)
        assert actions['operator_toggle_handler'] == SchedulingAction.START
        assert TaskState.get_task_state(dag_id="test_event_handler",
                                        task_id="operator_toggle_handler",
                                        executor_date=self._dag_run.execution_date).task_state is True

        actions = event_executor.execute_event_handler(self._dag_run, event=event)
        assert actions['operator_toggle_handler'] == SchedulingAction.STOP
        assert TaskState.get_task_state(dag_id="test_event_handler",
                                        task_id="operator_toggle_handler",
                                        executor_date=self._dag_run.execution_date).task_state is False
