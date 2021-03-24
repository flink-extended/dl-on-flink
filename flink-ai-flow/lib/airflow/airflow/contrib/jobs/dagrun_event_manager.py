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
import threading
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from queue import Queue, Empty
from typing import Optional, Set, Dict, cast

from notification_service.base_notification import BaseEvent

from airflow.contrib.jobs.background_service import BackgroundService
from airflow.executors.scheduling_action import SchedulingAction
from airflow.models import BaseOperator, DagRun
from airflow.models.dag import DagEventDependencies
from airflow.models.eventhandler import EventKey
from airflow.models.serialized_dag import SerializedDagModel
from airflow.models.taskstate import TaskState
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.mailbox import Mailbox
from airflow.events.scheduler_events import EventHandleEvent


class DagRunId(object):
    """
    DagRunId include dag id and run id of a dag run that is necessary to uniquely identify a dag run of a dag.
    """

    def __init__(self, dag_id: str, run_id: str) -> None:
        self.dag_id = dag_id
        self.run_id = run_id

    def __eq__(self, o: object) -> bool:
        if type(o) is type(self):
            o = cast(DagRunId, o)
            return self.dag_id == o.dag_id and self.run_id == o.run_id
        return False

    def __hash__(self) -> int:
        return hash(self.dag_id) + hash(self.run_id)


class EventHandleResult(object):
    """
    :class:`EventHandleResult` contains dag_run_id, task_id, and scheduling_action. It is sent back to the
    scheduler after executing the event_handler for the task.
    """

    def __init__(self, dag_run_id: DagRunId, task_id: str, scheduling_action: SchedulingAction):
        self.dag_run_id = dag_run_id
        self.task_id = task_id
        self.scheduling_action = scheduling_action

    def __eq__(self, o: object) -> bool:
        return self.__dict__ == o.__dict__

    def to_event(self) -> EventHandleEvent:
        return EventHandleEvent(dag_id=self.dag_run_id.dag_id,
                                dag_run_id=self.dag_run_id.run_id,
                                task_id=self.task_id,
                                action=self.scheduling_action)

    @classmethod
    def from_event(cls, event: EventHandleEvent) -> 'EventHandleResult':
        return EventHandleResult(DagRunId(dag_id=event.dag_id, run_id=event.dag_run_id),
                                 task_id=event.task_id,
                                 scheduling_action=event.action)


class DagRunEventManager(BackgroundService, LoggingMixin):
    """
    :class:`DagRunEventManager` accepts event and the dag_run_id of the dag run to handle the event from the
    Scheduler. It manage the life cycle of the :class:`DagRunEventExecutorRunner`.
    """

    def __init__(self, mailbox: Mailbox, context=None, max_workers=None, max_num_event=16):
        super().__init__(context)
        self._mailbox = mailbox
        self._event_executor_runners: Dict[DagRunId, DagRunEventExecutorRunner] = dict()
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="DagRunEventExecutor")
        self._max_num_event = max_num_event

        # DagRunEventExecutor will be added to the set right after it is submitted to ExecutorPool and removed
        # right after it is finished running.
        self._running_event_executor_runners: Set[DagRunId] = set()
        self._lock = threading.Lock()

    def start(self):
        """
        Do nothing
        """
        pass

    def handle_event(self, dag_run_id: DagRunId, event: BaseEvent):
        """
        Handle the event for :class:`DagRun` with the given dag run id.
        :param dag_run_id: id of the dagrun.
        :type dag_run_id: DagRunId
        :param event: the event to be handled.
        :type event: BaseEvent
        """
        with self._lock:
            # create DagRunEventExecutorRunner if not exist
            if dag_run_id not in self._event_executor_runners:
                self._event_executor_runners[dag_run_id] = \
                    DagRunEventExecutorRunner(mailbox=self._mailbox,
                                              dag_run_id=dag_run_id,
                                              max_num_event=self._max_num_event)
            self._event_executor_runners[dag_run_id].put_event(event)

            # submit the DagRunEventExecutorRunner to ExecutorPool if it is not running
            if dag_run_id in self._running_event_executor_runners:
                self.log.debug("{} has running runner".format(dag_run_id))
                return

            self._submit_event_executor_runner(dag_run_id)

    def end(self) -> None:
        """
        Stops all the :class:`DagRunEventExecutorRunner` and wait util all of them terminated.
        """
        self._executor.shutdown(wait=True)

    def terminate(self):
        """
        Stops all the :class:`DagRunEventExecutorRunner` and return immediately.
        """
        self._executor.shutdown(wait=False)

    def is_alive(self) -> bool:
        return True

    def _submit_event_executor_runner(self, dag_run_id):
        self._executor.submit(self._start_event_executor_runner, dag_run_id) \
            .add_done_callback(self._runner_exited)
        self._running_event_executor_runners.add(dag_run_id)

    def _start_event_executor_runner(self, dag_run_id: DagRunId):
        self.log.debug("starting DagRunEventExecutorRunner for {}".format(dag_run_id))
        self._event_executor_runners[dag_run_id].run()
        return dag_run_id

    def _runner_exited(self, dag_run_id: Future):
        dag_run_id = dag_run_id.result()
        self.log.debug("DagRunEventExecutorRunner for {} exit".format(dag_run_id))
        with self._lock:
            if not self._event_executor_runners[dag_run_id].empty_event_queue():
                self.log.debug("DagRunEventExecutorRunner for {} has non empty event queue, resubmitting...")
                self._submit_event_executor_runner(dag_run_id)
                return
            self._running_event_executor_runners.remove(dag_run_id)
            # DagRunEventExecutorRunner finished with empty event queue, release the DagRunEventExecutorRunner
            self._event_executor_runners.pop(dag_run_id)


class DagRunEventExecutorRunner(LoggingMixin):
    """
    :class:`DagRunEventExecutorRunner` use the :class:`DagRunEventExecutor` to run the event handler for events.
    """

    def __init__(self, mailbox: Mailbox,
                 dag_run_id: DagRunId,
                 max_num_event: int,
                 poll_timeout: int = 0) -> None:
        """

        :param mailbox: where the EventHandleResult is send to.
        :type mailbox: Mailbox
        :param dag_run_id: the run id of the dag run
        :type dag_run_id: str
        :param max_num_event: max number of event can be handled before exit
        :type max_num_event: int
        :param poll_timeout: poll timeout in second for event before exit
        :type poll_timeout: int
        """
        super().__init__()
        self._mailbox = mailbox
        self._dag_run_id = dag_run_id
        self._event_queue = Queue()
        self._max_num_event = max_num_event
        self._poll_timeout = poll_timeout

        dag_runs = DagRun.find(dag_id=dag_run_id.dag_id, run_id=dag_run_id.run_id)
        if len(dag_runs) < 1:
            raise RuntimeError("no dag_run found with dag_run_id: {}".format(dag_run_id))
        elif len(dag_runs) > 1:
            raise RuntimeError("more than one dag_run found with dag_run_id: {}".format(dag_run_id))

        self._dag_run = dag_runs[0]
        dag_id = self._dag_run.dag_id
        self._serialized_dag_model = SerializedDagModel.get(dag_id)
        if self._serialized_dag_model is None:
            raise RuntimeError("no serialized dag is found with dag_id: {}".format(dag_id))

    def run(self) -> None:
        """
        Start handling events. It will return in the following conditions:
        1. It doesn't receive any event in some timeout specified by poll_timeout.
        2. It has handled some number of event specified by max_num_event
        """
        try:
            self._run()
            self.log.debug("DagRunEventExecutorRunner for {} exiting...".format(self._dag_run_id))
        except Exception as _:
            self.log.exception("Failed to run event executor for dag run {}: ".format(self._dag_run_id))

    def put_event(self, event: BaseEvent):
        """
        Put the event to be handled by :class:`DagRunEventExecutor`.
        :param event: event to be handled.
        :type event:
        """
        self.log.debug("putting event {} to DagRunEventExecutorRunner {}".format(event, self._dag_run_id))
        self._event_queue.put(event)

    def empty_event_queue(self) -> bool:
        """
        Check whether event queue is empty.
        :return:
        :rtype:
        """
        return self._event_queue.qsize() == 0

    def _run(self):
        executor = DagRunEventExecutor(self._serialized_dag_model)
        event_processed = 0
        while True:
            event = self._get_event()
            self.log.debug("DagRunEventExecutorRunner for {} got event {}".format(self._dag_run_id, event))
            if event is None:
                break
            for task_id, action in executor.execute_event_handler(self._dag_run, event).items():
                self._mailbox.send_message(EventHandleResult(self._dag_run_id, task_id, action).to_event().to_event())
            event_processed = event_processed + 1
            if event_processed >= self._max_num_event:
                self.log.debug("DagRunEventExecutorRunner for {} exceed max_num_event: {}"
                               .format(self._dag_run_id, self._max_num_event))
                break

    def _get_event(self, block: bool = True) -> Optional[BaseEvent]:
        self.log.debug("getting event")
        try:
            return self._event_queue.get(block=block, timeout=self._poll_timeout)
        except Empty as _:
            self.log.debug("no event found")
            return None


class DagRunEventExecutor(LoggingMixin):
    """
    :class:`DagRunEventExecutor` is used to execute the EventHandler for Tasks in one dag.
    """

    def __init__(self, serialized_dag_model: SerializedDagModel):
        """
        :param serialized_dag_model: the dag where the tasks that should run event handler belongs to.
        :type serialized_dag_model: SerializedDagModel
        """
        super().__init__()
        self._dag = serialized_dag_model.dag
        self._dependency: DagEventDependencies = \
            DagEventDependencies.from_json(serialized_dag_model.event_relationships)

    def execute_event_handler(self,
                              dag_run: DagRun,
                              event: BaseEvent) -> Dict[str, SchedulingAction]:
        """
        Execute the task event handler that are interested in the given event for a specific dag run.
        :param dag_run: dag run for which the event handler should execute.
        :type dag_run: DagRun
        :param event: the event to be handled.
        :type event: BaseEvent
        """
        task_ids = self._dependency.find_affected_tasks(EventKey(event.key, event.event_type, event.namespace))
        if task_ids is None:
            return {}
        operators: Set[BaseOperator] = set()
        for task_id in task_ids:
            operator = self._find_operator(task_id)
            if operator is None:
                raise RuntimeError("Operator with task_id: {} not found in dag: {}"
                                   .format(task_id, self._dag.dag_id))
            operators.add(operator)

        scheduling_actions = dict()
        for operator in operators:
            scheduling_actions[operator.task_id] = self._operator_handle_event(event, operator, dag_run.execution_date)

        return scheduling_actions

    @staticmethod
    def _operator_handle_event(event, operator, execution_date) -> SchedulingAction:
        task_state = TaskState.get_task_state(operator.dag_id, operator.task_id, execution_date)
        event_handler = operator.get_events_handler()
        if task_state:
            scheduling_action, state = event_handler.handle_event(event, task_state.task_state)
            task_state.task_state = state
            task_state.update_task_state()
        else:
            scheduling_action, state = event_handler.handle_event(event, None)
        return scheduling_action

    def _find_operator(self, task_id) -> Optional[BaseOperator]:
        if self._dag.has_task(task_id):
            return self._dag.get_task(task_id)
        return None
