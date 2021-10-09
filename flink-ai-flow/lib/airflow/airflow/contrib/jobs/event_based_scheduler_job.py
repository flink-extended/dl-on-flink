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
import sched
import signal
import sys
import threading
import time
import traceback
from typing import Callable, List, Optional

from airflow.contrib.jobs.periodic_manager import PeriodicManager
from airflow.events.context_extractor import ContextExtractor, EventContext
from airflow.exceptions import SerializedDagNotFound, AirflowException
from airflow.models.dagcode import DagCode
from airflow.models.event_progress import get_event_progress, create_or_update_progress
from airflow.models.message import IdentifiedMessage, MessageState
from sqlalchemy import func, not_, or_, asc, case
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.session import Session
from airflow import models, settings
from airflow.configuration import conf
from airflow.executors.base_executor import BaseExecutor
from airflow.jobs.base_job import BaseJob
from airflow.models import DagModel, BaseOperator
from airflow.models.dag import DagEventDependencies, DAG
from airflow.models.dagbag import DagBag
from airflow.models.dagrun import DagRun
from airflow.models.eventhandler import EventKey
from airflow.models.serialized_dag import SerializedDagModel
from airflow.models.taskinstance import TaskInstanceKey
from airflow.stats import Stats
from airflow.utils import timezone
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.session import create_session, provide_session
from airflow.utils.sqlalchemy import prohibit_commit, skip_locked, with_row_locks
from airflow.utils.state import State
from airflow.utils.types import DagRunType

from airflow.utils.mailbox import Mailbox
from airflow.events.scheduler_events import (
    StopSchedulerEvent, TaskSchedulingEvent, DagExecutableEvent, TaskStateChangedEvent, EventHandleEvent, RequestEvent,
    ResponseEvent, StopDagEvent, ParseDagRequestEvent, ParseDagResponseEvent, SchedulerInnerEventUtil,
    BaseUserDefineMessage, UserDefineMessageType, SCHEDULER_NAMESPACE, DagRunFinishedEvent, PeriodicEvent,
    DagRunCreatedEvent)

from notification_service.base_notification import BaseEvent
from notification_service.client import EventWatcher, NotificationClient
from airflow.contrib.jobs.dag_trigger import DagTrigger
from airflow.contrib.jobs.dagrun_event_manager import DagRunEventManager, DagRunId
from airflow.executors.scheduling_action import SchedulingAction

TI = models.TaskInstance
DR = models.DagRun
DM = models.DagModel
MSG = models.Message


class EventBasedScheduler(LoggingMixin):
    def __init__(self, id,
                 mailbox: Mailbox,
                 task_event_manager: DagRunEventManager,
                 executor: BaseExecutor,
                 notification_client: NotificationClient,
                 server_uri: str,
                 context=None,
                 periodic_manager: PeriodicManager = None):
        super().__init__(context)
        self.id = id
        self.mailbox = mailbox
        self.task_event_manager: DagRunEventManager = task_event_manager
        self.executor = executor
        self.notification_client = notification_client
        self.dagbag = DagBag(read_dags_from_db=True)
        self._timer_handler = None
        self.timers = sched.scheduler()
        self.periodic_manager = periodic_manager
        self.server_uri = server_uri

    def sync(self):

        def call_regular_interval(
            delay: float,
            action: Callable,
            arguments=(),
            kwargs={},
        ):  # pylint: disable=dangerous-default-value
            def repeat(*args, **kwargs):
                action(*args, **kwargs)
                # This is not perfect. If we want a timer every 60s, but action
                # takes 10s to run, this will run it every 70s.
                # Good enough for now
                self._timer_handler = self.timers.enter(delay, 1, repeat, args, kwargs)

            self._timer_handler = self.timers.enter(delay, 1, repeat, arguments, kwargs)

        call_regular_interval(
            delay=conf.getfloat('scheduler', 'scheduler_heartbeat_sec', fallback='5.0'),
            action=self.executor.sync
        )
        self.timers.run()

    def stop_timer(self):
        if self.timers and self._timer_handler:
            self.timers.cancel(self._timer_handler)

    def submit_sync_thread(self):
        threading.Thread(target=self.sync).start()

    def schedule(self) -> bool:
        identified_message = self.mailbox.get_identified_message()
        if not identified_message:
            return True
        origin_event = identified_message.deserialize()
        self.log.debug("Event: {}".format(origin_event))
        if SchedulerInnerEventUtil.is_inner_event(origin_event):
            event = SchedulerInnerEventUtil.to_inner_event(origin_event)
        else:
            event = origin_event
        with create_session() as session:
            if isinstance(event, BaseEvent):
                dagruns = self._find_dagruns_by_event(event, session)
                for dagrun in dagruns:
                    dag_run_id = DagRunId(dagrun.dag_id, dagrun.run_id)
                    self.task_event_manager.handle_event(dag_run_id, event)
            elif isinstance(event, RequestEvent):
                self._process_request_event(event)
            elif isinstance(event, TaskSchedulingEvent):
                self._schedule_task(event)
            elif isinstance(event, TaskStateChangedEvent):
                dagrun = self._find_dagrun(event.dag_id, event.execution_date, session)
                if dagrun is not None:
                    self._handle_task_status_changed(dagrun, event, session)
                    dag_run_id = DagRunId(dagrun.dag_id, dagrun.run_id)
                    self.task_event_manager.handle_event(dag_run_id, origin_event)
                    tasks = self._find_downstream_tasks(event.task_id, dagrun, session)
                    self._send_scheduling_task_events(tasks, SchedulingAction.START)
                    if dagrun.state in State.finished:
                        self.mailbox.send_message(DagRunFinishedEvent(dagrun.dag_id, dagrun.execution_date).to_event())
                else:
                    self.log.warning("dagrun is None for dag_id:{} execution_date: {}".format(event.dag_id,
                                                                                              event.execution_date))
            elif isinstance(event, DagRunCreatedEvent):
                dagrun = self._find_dagrun(event.dag_id, event.execution_date, session)
                if dagrun is not None:
                    tasks = self._find_scheduled_tasks(dagrun, session)
                    self._send_scheduling_task_events(tasks, SchedulingAction.START)
                else:
                    self.log.warning("dagrun is None for dag_id:{} execution_date: {}".format(
                        event.dag_id, event.execution_date))
            elif isinstance(event, DagExecutableEvent):
                dagrun = self._create_dag_run(event.dag_id, session=session)
                tasks = self._find_scheduled_tasks(dagrun, session)
                self._send_scheduling_task_events(tasks, SchedulingAction.START)
            elif isinstance(event, EventHandleEvent):
                dag_runs = DagRun.find(dag_id=event.dag_id, run_id=event.dag_run_id)
                assert len(dag_runs) == 1
                ti = dag_runs[0].get_task_instance(event.task_id)
                self._send_scheduling_task_event(ti, event.action)
            elif isinstance(event, StopDagEvent):
                self._stop_dag(event.dag_id, session)
            elif isinstance(event, DagRunFinishedEvent):
                self._remove_periodic_events(event.dag_id, event.execution_date)
            elif isinstance(event, PeriodicEvent):
                dag_runs = DagRun.find(dag_id=event.dag_id, execution_date=event.execution_date)
                assert len(dag_runs) == 1
                ti = dag_runs[0].get_task_instance(event.task_id)
                self._send_scheduling_task_event(ti, SchedulingAction.RESTART)
            elif isinstance(event, StopSchedulerEvent):
                self.log.info("{} {}".format(self.id, event.job_id))
                if self.id == event.job_id or 0 == event.job_id:
                    self.log.info("break the scheduler event loop.")
                    identified_message.remove_handled_message()
                    session.expunge_all()
                    return False
            elif isinstance(event, ParseDagRequestEvent) or isinstance(event, ParseDagResponseEvent):
                pass
            elif isinstance(event, ResponseEvent):
                pass
            else:
                self.log.error("can not handler the event {}".format(event))
            identified_message.remove_handled_message()
            session.expunge_all()
            return True

    def _handle_task_status_changed(self, dagrun: DagRun, event: TaskStateChangedEvent, session):
        ti = dagrun.get_task_instance(task_id=event.task_id)
        if event.try_number == ti.try_number:
            if State.UP_FOR_RETRY == event.state:
                dag = self.dagbag.get_dag(dagrun.dag_id, session=session)
                ti.task = dag.get_task(ti.task_id)
                next_retry_datetime = ti.next_retry_datetime()
                self.mailbox.send_message(message=TaskSchedulingEvent(dag_id=event.dag_id,
                                                                      task_id=event.task_id,
                                                                      execution_date=event.execution_date,
                                                                      try_number=event.try_number,
                                                                      action=SchedulingAction.START).to_event(),
                                          queue_time=next_retry_datetime)

            ti.update_latest_task_execution(session=session)

    def stop(self) -> None:
        self.mailbox.send_message(StopSchedulerEvent(self.id).to_event())
        self.log.info("Send stop event to the scheduler.")

    def recover(self, last_scheduling_id):
        lost_dag_codes = DagCode.recover_lost_dag_code()
        self.log.info("Found %s dags not exists in DAG folder, recovered from DB. Dags' path: %s",
                      len(lost_dag_codes), lost_dag_codes)
        self.log.info("Waiting for executor recovery...")
        self.executor.recover_state()
        unprocessed_messages = self.get_unprocessed_message(last_scheduling_id)
        self.log.info("Recovering %s messages of last scheduler job with id: %s",
                      len(unprocessed_messages), last_scheduling_id)
        for msg in unprocessed_messages:
            self.mailbox.send_message(msg.deserialize(), msg.queue_time)

    @staticmethod
    def get_unprocessed_message(last_scheduling_id: int) -> List[IdentifiedMessage]:
        with create_session() as session:
            results: List[MSG] = session.query(MSG).filter(
                MSG.scheduling_job_id == last_scheduling_id,
                MSG.state == MessageState.QUEUED
            ).order_by(asc(MSG.id)).all()
        unprocessed: List[IdentifiedMessage] = []
        for msg in results:
            unprocessed.append(IdentifiedMessage(msg.data, msg.id, msg.queue_time))
        return unprocessed

    def _find_dagrun(self, dag_id, execution_date, session) -> DagRun:
        dagrun = session.query(DagRun).filter(
            DagRun.dag_id == dag_id,
            DagRun.execution_date == execution_date
        ).first()
        return dagrun

    def _register_periodic_events(self, execution_date, dag, session=None):
        self.periodic_manager.store.set_session(session)
        for task in dag.tasks:
            if task.executor_config is not None and 'periodic_config' in task.executor_config:
                self.log.debug('register periodic task {} {} {}'.format(dag.dag_id, execution_date, task.task_id))
                self.periodic_manager.add_task(dag_id=dag.dag_id,
                                               execution_date=execution_date,
                                               task_id=task.task_id,
                                               periodic_config=task.executor_config['periodic_config'])
        self.periodic_manager.store.unset_session()

    @provide_session
    def _remove_periodic_events(self, dag_id, execution_date, session=None):
        dagruns = DagRun.find(dag_id=dag_id, execution_date=execution_date)
        dag = self.dagbag.get_dag(dag_id=dagruns[0].dag_id, session=session)
        for task in dag.tasks:
            if task.executor_config is not None and 'periodic_config' in task.executor_config:
                self.log.debug('remove periodic task {} {} {}'.format(dag_id, execution_date, task.task_id))
                self.periodic_manager.remove_task(dag_id, execution_date, task.task_id)

    def _create_dag_run(self, dag_id, session, run_type=DagRunType.SCHEDULED, context=None) -> DagRun:
        with prohibit_commit(session) as guard:
            if settings.USE_JOB_SCHEDULE:
                """
                Unconditionally create a DAG run for the given DAG, and update the dag_model's fields to control
                if/when the next DAGRun should be created
                """
                try:
                    dag = self.dagbag.get_dag(dag_id, session=session)
                    dag_model = session \
                        .query(DagModel).filter(DagModel.dag_id == dag_id).first()
                    if dag_model is None:
                        return None
                    next_dagrun = dag_model.next_dagrun
                    dag_hash = self.dagbag.dags_hash.get(dag.dag_id)
                    external_trigger = False
                    # register periodic task
                    if run_type == DagRunType.MANUAL:
                        next_dagrun = timezone.utcnow()
                        external_trigger = True

                    # Explicitly check if the DagRun already exists. This is an edge case
                    # where a Dag Run is created but `DagModel.next_dagrun` and `DagModel.next_dagrun_create_after`
                    # are not updated.
                    active_dagrun = session.query(DagRun)\
                        .filter(DagRun.dag_id == dag_model.dag_id,
                                DagRun.execution_date == dag_model.next_dagrun).first()
                    if active_dagrun is not None:
                        self.log.info("Dagrun already created, %s", active_dagrun)
                        return active_dagrun
                    dag_run = dag.create_dagrun(
                        run_type=run_type,
                        execution_date=next_dagrun,
                        start_date=timezone.utcnow(),
                        state=State.RUNNING,
                        external_trigger=external_trigger,
                        session=session,
                        dag_hash=dag_hash,
                        creating_job_id=self.id,
                        context=context
                    )
                    if run_type == DagRunType.SCHEDULED:
                        self._update_dag_next_dagrun(dag_id, session)
                    self._register_periodic_events(dag_run.execution_date, dag, session)
                    # commit the session - Release the write lock on DagModel table.
                    guard.commit()
                    # END: create dagrun
                    return dag_run
                except SerializedDagNotFound:
                    self.log.exception("DAG '%s' not found in serialized_dag table", dag_id)
                    return None
                except Exception:
                    self.log.exception("Error occurred when create dag_run of dag: %s", dag_id)
                    return None

    def _update_dag_next_dagrun(self, dag_id, session):
        """
                Bulk update the next_dagrun and next_dagrun_create_after for all the dags.

                We batch the select queries to get info about all the dags at once
                """
        active_runs_of_dag = session \
            .query(func.count('*')).filter(
            DagRun.dag_id == dag_id,
            DagRun.state == State.RUNNING,
            DagRun.external_trigger.is_(False),
        ).scalar()
        dag_model = session \
            .query(DagModel).filter(DagModel.dag_id == dag_id).first()

        dag = self.dagbag.get_dag(dag_id, session=session)
        if dag.max_active_runs and active_runs_of_dag >= dag.max_active_runs:
            self.log.info(
                "DAG %s is at (or above) max_active_runs (%d of %d), not creating any more runs",
                dag.dag_id,
                active_runs_of_dag,
                dag.max_active_runs,
            )
            dag_model.next_dagrun_create_after = None
        else:
            dag_model.next_dagrun, dag_model.next_dagrun_create_after = dag.next_dagrun_info(
                dag_model.next_dagrun
            )

    def _schedule_task(self, scheduling_event: TaskSchedulingEvent):
        task_key = TaskInstanceKey(
            scheduling_event.dag_id,
            scheduling_event.task_id,
            scheduling_event.execution_date,
            scheduling_event.try_number
        )
        self.executor.schedule_task(task_key, scheduling_event.action)

    def _find_dagruns_by_event(self, event, session) -> Optional[List[DagRun]]:
        affect_dag_runs = []
        event_key = EventKey(event.key, event.event_type, event.namespace, event.sender)
        dag_runs = session \
            .query(DagRun).filter(DagRun.state == State.RUNNING).all()
        self.log.debug('dag_runs {}'.format(len(dag_runs)))

        if dag_runs is None or len(dag_runs) == 0:
            return affect_dag_runs
        dags = session.query(SerializedDagModel).filter(
            SerializedDagModel.dag_id.in_(dag_run.dag_id for dag_run in dag_runs)
        ).all()
        self.log.debug('dags {}'.format(len(dags)))

        affect_dags = {}
        for dag in dags:
            self.log.debug('dag config {}'.format(dag.event_relationships))
            self.log.debug('event key {} {} {}'.format(event.key, event.event_type, event.namespace))

            dep: DagEventDependencies = DagEventDependencies.from_json(dag.event_relationships)
            if dep.is_affect(event_key):
                context_extractor: ContextExtractor = dag.context_extractor
                try:
                    event_context: EventContext = context_extractor.extract_context(event)
                except Exception as e:
                    self.log.error(
                        "Failed to call context extractor, dag {} skips event {}".format(dag.dag_id, event),
                        exc_info=e)
                    continue
                if event_context is not None:
                    affect_dags[dag.dag_id] = event_context
        if len(affect_dags) == 0:
            return affect_dag_runs
        for dag_run in dag_runs:
            if dag_run.dag_id in affect_dags:
                event_context: EventContext = affect_dags[dag_run.dag_id]
                if event_context.is_broadcast() or dag_run.context in event_context.get_contexts():
                    affect_dag_runs.append(dag_run)
        return affect_dag_runs

    def _find_scheduled_tasks(
        self,
        dag_run: DagRun,
        session: Session,
        check_execution_date=False
    ) -> Optional[List[TI]]:
        """
        Make scheduling decisions about an individual dag run

        ``currently_active_runs`` is passed in so that a batch query can be
        used to ask this for all dag runs in the batch, to avoid an n+1 query.

        :param dag_run: The DagRun to schedule
        :return: scheduled tasks
        """
        if not dag_run or dag_run.get_state() in State.finished:
            return
        try:
            dag = dag_run.dag = self.dagbag.get_dag(dag_run.dag_id, session=session)
        except SerializedDagNotFound:
            self.log.exception("DAG '%s' not found in serialized_dag table", dag_run.dag_id)
            return None

        if not dag:
            self.log.error("Couldn't find dag %s in DagBag/DB!", dag_run.dag_id)
            return None

        currently_active_runs = session.query(
            TI.execution_date,
        ).filter(
            TI.dag_id == dag_run.dag_id,
            TI.state.notin_(list(State.finished)),
        ).distinct().all()

        if check_execution_date and dag_run.execution_date > timezone.utcnow() and not dag.allow_future_exec_dates:
            self.log.warning("Execution date is in future: %s", dag_run.execution_date)
            return None

        if dag.max_active_runs and not dag.is_long_running_dag():
            if (
                len(currently_active_runs) >= dag.max_active_runs
                and dag_run.execution_date not in currently_active_runs
            ):
                self.log.warning(
                    "DAG %s already has %d active runs, not queuing any tasks for run %s",
                    dag.dag_id,
                    len(currently_active_runs),
                    dag_run.execution_date,
                )

        self._verify_integrity_if_dag_changed(dag_run=dag_run, session=session)

        schedulable_tis, callback_to_run = dag_run.update_state(session=session, execute_callbacks=False)
        dag_run.schedule_tis(schedulable_tis, session)
        session.commit()

        query = (session.query(TI)
                 .outerjoin(TI.dag_run)
                 .filter(DR.run_id == dag_run.run_id)
                 .join(TI.dag_model)
                 .filter(not_(DM.is_paused))
                 .filter(TI.state == State.SCHEDULED)
                 .options(selectinload('dag_model')))
        scheduled_tis: List[TI] = with_row_locks(
            query,
            of=TI,
            **skip_locked(session=session),
        ).all()
        return scheduled_tis

    def _find_downstream_tasks(self, task_id, dag_run, session) -> Optional[List[TI]]:
        tasks = self._find_scheduled_tasks(dag_run, session)
        if not tasks or len(tasks) == 0:
            return None
        dag = self.dagbag.get_dag(dag_run.dag_id, session=session)
        downstream_task_ids = dag.task_dict.get(task_id).downstream_task_ids
        res = []
        for task in tasks:
            if task.task_id in downstream_task_ids:
                res.append(task)
        return res

    @provide_session
    def _verify_integrity_if_dag_changed(self, dag_run: DagRun, session=None):
        """Only run DagRun.verify integrity if Serialized DAG has changed since it is slow"""
        latest_version = SerializedDagModel.get_latest_version_hash(dag_run.dag_id, session=session)
        if dag_run.dag_hash == latest_version:
            self.log.debug("DAG %s not changed structure, skipping dagrun.verify_integrity", dag_run.dag_id)
            return

        dag_run.dag_hash = latest_version

        # Refresh the DAG
        dag_run.dag = self.dagbag.get_dag(dag_id=dag_run.dag_id, session=session)

        # Verify integrity also takes care of session.flush
        dag_run.verify_integrity(session=session)

    def _send_scheduling_task_event(self, ti: Optional[TI], action: SchedulingAction):
        if ti is None or action == SchedulingAction.NONE:
            return
        with create_session() as session:
            ti.state = State.QUEUED
            session.commit()
        task_scheduling_event = TaskSchedulingEvent(
            ti.task_id,
            ti.dag_id,
            ti.execution_date,
            ti.try_number,
            action
        )
        self.mailbox.send_message(task_scheduling_event.to_event())

    def _send_scheduling_task_events(self, tis: Optional[List[TI]], action: SchedulingAction):
        if tis is None:
            return
        for ti in tis:
            self._send_scheduling_task_event(ti, action)

    @provide_session
    def _emit_pool_metrics(self, session: Session = None) -> None:
        pools = models.Pool.slots_stats(session=session)
        for pool_name, slot_stats in pools.items():
            Stats.gauge(f'pool.open_slots.{pool_name}', slot_stats["open"])
            Stats.gauge(f'pool.queued_slots.{pool_name}', slot_stats[State.QUEUED])
            Stats.gauge(f'pool.running_slots.{pool_name}', slot_stats[State.RUNNING])

    @staticmethod
    def _reset_unfinished_task_state(dag_run):
        with create_session() as session:
            to_be_reset = [s for s in State.unfinished if s not in [State.RUNNING, State.QUEUED]]
            tis = dag_run.get_task_instances(to_be_reset, session)
            for ti in tis:
                ti.state = State.NONE
            session.commit()

    @provide_session
    def restore_unfinished_dag_run(self, session):
        dag_runs = DagRun.next_dagruns_to_examine(session, max_number=sys.maxsize).all()
        if not dag_runs or len(dag_runs) == 0:
            return
        for dag_run in dag_runs:
            self._reset_unfinished_task_state(dag_run)
            tasks = self._find_scheduled_tasks(dag_run, session)
            self._send_scheduling_task_events(tasks, SchedulingAction.START)

    @provide_session
    def heartbeat_callback(self, session: Session = None) -> None:
        Stats.incr('scheduler_heartbeat', 1, 1)

    @provide_session
    def _process_request_event(self, event: RequestEvent, session: Session = None):
        try:
            message = BaseUserDefineMessage()
            message.from_json(event.body)
            if message.message_type == UserDefineMessageType.RUN_DAG:
                # todo make sure dag file is parsed.
                dagrun = self._create_dag_run(message.dag_id, session=session, run_type=DagRunType.MANUAL,
                                              context=message.context)
                if not dagrun:
                    self.log.error("Failed to create dag_run.")
                    # TODO Need to add ret_code and errro_msg in ExecutionContext in case of exception
                    self.notification_client.send_event(ResponseEvent(event.request_id, None).to_event())
                    return
                tasks = self._find_scheduled_tasks(dagrun, session, False)
                self._send_scheduling_task_events(tasks, SchedulingAction.START)
                self.notification_client.send_event(ResponseEvent(event.request_id, dagrun.run_id).to_event())
            elif message.message_type == UserDefineMessageType.STOP_DAG_RUN:
                dag_run = DagRun.get_run_by_id(session=session, dag_id=message.dag_id, run_id=message.dagrun_id)
                self._stop_dag_run(dag_run)
                self.notification_client.send_event(ResponseEvent(event.request_id, dag_run.run_id).to_event())
            elif message.message_type == UserDefineMessageType.EXECUTE_TASK:
                dagrun = DagRun.get_run_by_id(session=session, dag_id=message.dag_id, run_id=message.dagrun_id)
                ti: TI = dagrun.get_task_instance(task_id=message.task_id)
                self.mailbox.send_message(TaskSchedulingEvent(
                    task_id=ti.task_id,
                    dag_id=ti.dag_id,
                    execution_date=ti.execution_date,
                    try_number=ti.try_number,
                    action=SchedulingAction(message.action)
                ).to_event())
                self.notification_client.send_event(ResponseEvent(event.request_id, dagrun.run_id).to_event())
        except Exception:
            self.log.exception("Error occurred when processing request event.")

    def _stop_dag(self, dag_id, session: Session):
        """
        Stop the dag. Pause the dag and cancel all running dag_runs and task_instances.
        """
        DagModel.get_dagmodel(dag_id, session)\
            .set_is_paused(is_paused=True, including_subdags=True, session=session)
        active_runs = DagRun.find(dag_id=dag_id, state=State.RUNNING)
        for dag_run in active_runs:
            self._stop_dag_run(dag_run)

    def _stop_dag_run(self, dag_run: DagRun):
        dag_run.stop_dag_run()
        for ti in dag_run.get_task_instances():
            if ti.state in State.unfinished:
                self.executor.schedule_task(ti.key, SchedulingAction.STOP)
        self.mailbox.send_message(DagRunFinishedEvent(dag_id=dag_run.dag_id,
                                                      execution_date=dag_run.execution_date).to_event())


class SchedulerEventWatcher(EventWatcher):
    def __init__(self, mailbox):
        self.mailbox = mailbox

    def process(self, events: List[BaseEvent]):
        for e in events:
            self.mailbox.send_message(e)


class EventBasedSchedulerJob(BaseJob):
    """
    1. todo self heartbeat
    """
    __mapper_args__ = {'polymorphic_identity': 'EventBasedSchedulerJob'}

    def __init__(self, dag_directory,
                 server_uri=None,
                 event_start_time=None,
                 max_runs=-1,
                 refresh_dag_dir_interval=conf.getint('scheduler', 'refresh_dag_dir_interval', fallback=1),
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log.info("Starting event based scheduler with notification server uri: {}".format(server_uri))
        self.mailbox: Mailbox = Mailbox()
        self.dag_trigger: DagTrigger = DagTrigger(
            dag_directory=dag_directory,
            max_runs=max_runs,
            dag_ids=None,
            pickle_dags=False,
            mailbox=self.mailbox,
            refresh_dag_dir_interval=refresh_dag_dir_interval,
            notification_service_uri=server_uri
        )
        self.task_event_manager = DagRunEventManager(self.mailbox)
        self.executor.set_mailbox(self.mailbox)
        self.executor.set_server_uri(server_uri)
        self.notification_client: NotificationClient = NotificationClient(server_uri=server_uri,
                                                                          default_namespace=SCHEDULER_NAMESPACE)
        self.periodic_manager = PeriodicManager(self.mailbox)
        self.scheduler: EventBasedScheduler = EventBasedScheduler(
            self.id,
            self.mailbox,
            self.task_event_manager,
            self.executor,
            self.notification_client,
            server_uri,
            None,
            self.periodic_manager
        )
        self.last_scheduling_id = self._last_scheduler_job_id()
        self.need_recover_state = False
        self.last_event_version = None
        if event_start_time is None:
            if self.last_scheduling_id is None:
                self.start_time = int(time.time() * 1000)
            else:
                # need recover the state of the scheduler
                self.start_time, self.last_event_version = self._get_progress(self.last_scheduling_id)
                self.need_recover_state = True
        else:
            self.start_time = event_start_time
        self.log.info('Progress {} {}'.format(self.start_time, self.last_event_version))

    @staticmethod
    def _last_scheduler_job_id():
        last_run = EventBasedSchedulerJob.most_recent_job()
        if not last_run:
            return None
        else:
            return last_run.id

    @staticmethod
    def _get_progress(scheduling_job_id):
        progress = get_event_progress(scheduling_job_id)
        if progress is None:
            return int(time.time() * 1000), None
        else:
            return progress.last_event_time, progress.last_event_version

    def _execute(self):
        # faulthandler.enable()
        self.log.info("Starting the scheduler Job")

        # DAGs can be pickled for easier remote execution by some executors
        # pickle_dags = self.do_pickle and self.executor_class not in UNPICKLEABLE_EXECUTORS

        try:
            self.mailbox.set_scheduling_job_id(self.id)
            self.mailbox.start()
            self.scheduler.id = self.id
            self.dag_trigger.start()
            self.task_event_manager.start()
            self.executor.job_id = self.id
            self.periodic_manager.start()

            self.register_signals()

            # Start after resetting orphaned tasks to avoid stressing out DB.

            execute_start_time = timezone.utcnow()

            self.scheduler.submit_sync_thread()
            if self.need_recover_state:
                self.scheduler.recover(self.last_scheduling_id)

            self._set_event_progress()

            self._start_listen_events()
            self.executor.start()

            self._run_scheduler_loop()

            self._stop_listen_events()
            self.periodic_manager.shutdown()
            self.dag_trigger.end()
            self.task_event_manager.end()
            self.executor.end()
            self.mailbox.stop()

            settings.Session.remove()  # type: ignore
        except Exception as e:  # pylint: disable=broad-except
            self.log.exception("Exception when executing scheduler, %s", e)
        finally:
            self.log.info("Exited execute loop")

    def _run_scheduler_loop(self) -> None:
        self.log.info("Starting the scheduler loop.")
        self.scheduler.restore_unfinished_dag_run()
        should_continue = True
        while should_continue:
            try:
                should_continue = self.scheduler.schedule()
                self.heartbeat(only_if_necessary=True)
            except Exception as e:
                traceback.print_exc()
                self.log.error('Scheduler error [%s]', traceback.format_exc())
                time.sleep(1)
        self.scheduler.stop_timer()

    def _set_event_progress(self):
        create_or_update_progress(scheduling_job_id=self.id,
                                  last_event_time=self.start_time,
                                  last_event_version=self.last_event_version)

    def _start_listen_events(self):
        watcher = SchedulerEventWatcher(self.mailbox)
        self.notification_client.start_listen_events(
            watcher=watcher,
            start_time=self.start_time,
            version=self.last_event_version
        )

    def _stop_listen_events(self):
        self.notification_client.stop_listen_events()

    def register_signals(self) -> None:
        """Register signals that stop child processes"""
        signal.signal(signal.SIGINT, self._exit_gracefully)
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        signal.signal(signal.SIGUSR2, self._debug_dump)

    def _exit_gracefully(self, signum, frame) -> None:  # pylint: disable=unused-argument
        """Helper method to clean up processor_agent to avoid leaving orphan processes."""
        self.log.info("Exiting gracefully upon receiving signal %s", signum)
        sys.exit(os.EX_OK)

    def _debug_dump(self, signum, frame):  # pylint: disable=unused-argument
        try:
            sig_name = signal.Signals(signum).name  # pylint: disable=no-member
        except Exception:  # pylint: disable=broad-except
            sig_name = str(signum)

        self.log.info("%s\n%s received, printing debug\n%s", "-" * 80, sig_name, "-" * 80)

        self.executor.debug_dump()
        self.log.info("-" * 80)

    def is_alive(self, grace_multiplier: Optional[float] = None) -> bool:
        """
        Is this SchedulerJob alive?

        We define alive as in a state of running and a heartbeat within the
        threshold defined in the ``scheduler_health_check_threshold`` config
        setting.

        ``grace_multiplier`` is accepted for compatibility with the parent class.

        :rtype: boolean
        """
        if grace_multiplier is not None:
            # Accept the same behaviour as superclass
            return super().is_alive(grace_multiplier=grace_multiplier)
        scheduler_health_check_threshold: int = conf.getint('scheduler', 'scheduler_health_check_threshold')
        return (
            self.state == State.RUNNING
            and (timezone.utcnow() - self.latest_heartbeat).total_seconds() < scheduler_health_check_threshold
        )
