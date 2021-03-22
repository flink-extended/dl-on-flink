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
import faulthandler
from typing import Callable, List, Optional

from airflow.exceptions import SerializedDagNotFound, AirflowException
from airflow.models.message import IdentifiedMessage, MessageState
from sqlalchemy import func, not_, or_, asc
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.session import Session
from airflow import models, settings
from airflow.configuration import conf
from airflow.executors.base_executor import BaseExecutor
from airflow.jobs.base_job import BaseJob
from airflow.models import DagModel
from airflow.models.dag import DagEventDependencies
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
    StopSchedulerEvent, TaskSchedulingEvent, DagExecutableEvent, TaskStatusChangedEvent, EventHandleEvent,
    SchedulerInnerEventUtil
)
from notification_service.base_notification import BaseEvent
from notification_service.client import EventWatcher, NotificationClient
from airflow.contrib.jobs.dag_trigger import DagTrigger
from airflow.contrib.jobs.dagrun_event_manager import DagRunEventManager, DagRunId
from airflow.executors.scheduling_action import SchedulingAction

TI = models.TaskInstance
DR = models.DagRun
DM = models.DagModel
MSG = models.Message

faulthandler.enable()


class EventBasedScheduler(LoggingMixin):
    def __init__(self, id, mailbox: Mailbox, task_event_manager: DagRunEventManager, executor: BaseExecutor, context=None):
        super().__init__(context)
        self.id = id
        self.mailbox = mailbox
        self.task_event_manager: DagRunEventManager = task_event_manager
        self.executor = executor
        self.dagbag = DagBag(read_dags_from_db=True)

    def sync(self):
        timers = sched.scheduler()

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
                timers.enter(delay, 1, repeat, args, kwargs)
            timers.enter(delay, 1, repeat, arguments, kwargs)

        call_regular_interval(
            delay=1.0,
            action=self.executor.sync
        )
        timers.run()

    def submit_sync_thread(self):
        threading.Thread(target=self.sync).start()

    def schedule(self):
        self.log.info("Starting the scheduler.")
        self._restore_unfinished_dag_run()
        while True:
            identified_message = self.mailbox.get_identified_message()
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
                elif isinstance(event, TaskSchedulingEvent):
                    self._schedule_task(event)
                elif isinstance(event, TaskStatusChangedEvent):
                    dagrun = self._find_dagrun(event.dag_id, event.execution_date, session)
                    tasks = self._find_schedulable_tasks(dagrun, session)
                    self._send_scheduling_task_events(tasks, SchedulingAction.START)
                elif isinstance(event, DagExecutableEvent):
                    dagrun = self._create_dag_run(event.dag_id, session=session)
                    tasks = self._find_schedulable_tasks(dagrun, session)
                    self._send_scheduling_task_events(tasks, SchedulingAction.START)
                elif isinstance(event, EventHandleEvent):
                    dag_runs = DagRun.find(dag_id=event.dag_id, run_id=event.dag_run_id)
                    assert len(dag_runs) == 1
                    ti = dag_runs[0].get_task_instance(event.task_id)
                    self._send_scheduling_task_event(ti, event.action)
                elif isinstance(event, StopSchedulerEvent):
                    if self.id == event.job_id:
                        self.log.info("break the scheduler event loop.")
                        break
                    else:
                        continue
                else:
                    self.log.error("can not handler the event {}".format(event))
                identified_message.remove_handled_message()
                session.expunge_all()

    def stop(self) -> None:
        self.mailbox.send_message(StopSchedulerEvent(self.id).to_event())
        self.log.info("Send stop event to the scheduler.")

    def recover(self, last_scheduling_id):
        self.log.info("Waiting for executor recovery...")
        self.executor.recover_state()
        unprocessed_messages = self.get_unprocessed_message(last_scheduling_id)
        self.log.info("Recovering %s messages of last scheduler job with id: %s",
                      len(unprocessed_messages), last_scheduling_id)
        for msg in unprocessed_messages:
            self.mailbox.send_identified_message(msg)

    @staticmethod
    def get_unprocessed_message(last_scheduling_id: int) -> List[IdentifiedMessage]:
        with create_session() as session:
            results: List[MSG] = session.query(MSG).filter(
                MSG.scheduling_job_id == last_scheduling_id,
                MSG.state == MessageState.QUEUED
            ).order_by(asc(MSG.id)).all()
        unprocessed: List[IdentifiedMessage] = []
        for msg in results:
            unprocessed.append(IdentifiedMessage(msg.data, msg.id))
        return unprocessed

    def _find_dagrun(self, dag_id, execution_date, session)->DagRun:
        dagrun = session.query(DagRun).filter(
            DagRun.dag_id == dag_id,
            DagRun.execution_date == execution_date
        ).first()
        return dagrun

    def _create_dag_run(self, dag_id, session)->DagRun:
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
                    next_dagrun = dag_model.next_dagrun
                    dag_hash = self.dagbag.dags_hash.get(dag.dag_id)
                    dag_run = dag.create_dagrun(
                        run_type=DagRunType.SCHEDULED,
                        execution_date=next_dagrun,
                        start_date=timezone.utcnow(),
                        state=State.RUNNING,
                        external_trigger=False,
                        session=session,
                        dag_hash=dag_hash,
                        creating_job_id=self.id,
                    )
                    self._update_dag_next_dagrun(dag_id, session)

                    # commit the session - Release the write lock on DagModel table.
                    guard.commit()
                    # END: create dagrun
                    return dag_run
                except SerializedDagNotFound:
                    self.log.exception("DAG '%s' not found in serialized_dag table", dag_id)
                    return None
                except Exception:
                    self.log.exception("Error occurred when create dag_run of dag: %s", dag_id)


    def _update_dag_next_dagrun(self, dag_id, session):
        """
                Bulk update the next_dagrun and next_dagrun_create_after for all the dags.

                We batch the select queries to get info about all the dags at once
                """
        active_runs_of_dag = session\
            .query(func.count('*')).filter(
                DagRun.dag_id == dag_id,
                DagRun.state == State.RUNNING,
                DagRun.external_trigger.is_(False),
            ).scalar()
        dag_model = session\
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

    def _find_dagruns_by_event(self, event, session)->Optional[List[DagRun]]:
        affect_dag_runs = []
        event_key = EventKey(event.key, event.event_type, event.namespace)
        dag_runs = session \
            .query(DagRun).filter(DagRun.state == State.RUNNING).all()
        if dag_runs is None or len(dag_runs) == 0:
            return affect_dag_runs
        dags = session.query(SerializedDagModel).filter(
            SerializedDagModel.dag_id.in_(dag_run.dag_id for dag_run in dag_runs)
        ).all()
        affect_dags = set()
        for dag in dags:
            dep: DagEventDependencies = DagEventDependencies.from_json(dag.event_relationships)
            if dep.is_affect(event_key):
                affect_dags.add(dag.dag_id)
        if len(affect_dags) == 0:
            return affect_dag_runs
        for dag_run in dag_runs:
            if dag_run.dag_id in affect_dags:
                affect_dag_runs.append(dag_run)
        return affect_dag_runs

    def _find_schedulable_tasks(
        self,
        dag_run: DagRun,
        session: Session,
    ) -> Optional[List[TI]]:
        """
        Make scheduling decisions about an individual dag run

        ``currently_active_runs`` is passed in so that a batch query can be
        used to ask this for all dag runs in the batch, to avoid an n+1 query.

        :param dag_run: The DagRun to schedule
        :return: scheduled tasks
        """
        if not dag_run:
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
        ).all()

        if dag_run.execution_date > timezone.utcnow() and not dag.allow_future_exec_dates:
            self.log.error("Execution date is in future: %s", dag_run.execution_date)
            return None

        if dag.max_active_runs:
            if (
                len(currently_active_runs) >= dag.max_active_runs
                and dag_run.execution_date not in currently_active_runs
            ):
                self.log.info(
                    "DAG %s already has %d active runs, not queuing any tasks for run %s",
                    dag.dag_id,
                    len(currently_active_runs),
                    dag_run.execution_date,
                )
                return None

        self._verify_integrity_if_dag_changed(dag_run=dag_run, session=session)

        schedulable_tis, callback_to_run = dag_run.update_state(session=session, execute_callbacks=False)
        dag_run.schedule_tis(schedulable_tis, session)

        query = (session.query(TI)
                 .outerjoin(TI.dag_run)
                 .filter(or_(DR.run_id.is_(None), DR.run_type != DagRunType.BACKFILL_JOB))
                 .join(TI.dag_model)
                 .filter(not_(DM.is_paused))
                 .filter(TI.state == State.SCHEDULED)
                 .options(selectinload('dag_model')))
        scheduled_tis: List[TI] = with_row_locks(
            query,
            of=TI,
            **skip_locked(session=session),
        ).all()

        # todo self._send_dag_callbacks_to_processor(dag_run, callback_to_run)

        # This will do one query per dag run. We "could" build up a complex
        # query to update all the TIs across all the execution dates and dag
        # IDs in a single query, but it turns out that can be _very very slow_
        # see #11147/commit ee90807ac for more details
        return scheduled_tis

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
        if ti is None:
            return
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
    def _restore_unfinished_dag_run(self, session):
        dag_runs = DagRun.next_dagruns_to_examine(session, max_number=sys.maxsize).all()
        if not dag_runs or len(dag_runs) == 0:
            return
        for dag_run in dag_runs:
            self._reset_unfinished_task_state(dag_run)
            tasks = self._find_schedulable_tasks(dag_run, session)
            self._send_scheduling_task_events(tasks, SchedulingAction.START)

    @provide_session
    def heartbeat_callback(self, session: Session = None) -> None:
        Stats.incr('scheduler_heartbeat', 1, 1)


class SchedulerEventWatcher(EventWatcher):
    def __init__(self, mailbox):
        self.mailbox = mailbox

    def process(self, events: List[BaseEvent]):
        for e in events:
            self.mailbox.send_message(e)


class EventBasedSchedulerJob(BaseJob):
    """
    1. todo self heartbeat
    2. todo check other scheduler failed
    3. todo timeout dagrun
    """
    __mapper_args__ = {'polymorphic_identity': 'EventBasedSchedulerJob'}

    def __init__(self, dag_directory, server_uri=None, max_runs=-1, refresh_dag_dir_interval=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mailbox: Mailbox = Mailbox()
        self.dag_trigger: DagTrigger = DagTrigger(
            dag_directory=dag_directory,
            max_runs=max_runs,
            dag_ids=None,
            pickle_dags=False,
            mailbox=self.mailbox,
            refresh_dag_dir_interval= refresh_dag_dir_interval
        )
        self.task_event_manager = DagRunEventManager(self.mailbox)
        self.executor.set_mailbox(self.mailbox)
        self.scheduler: EventBasedScheduler = EventBasedScheduler(
            self.id,
            self.mailbox,
            self.task_event_manager,
            self.executor
        )
        self.notification_client: NotificationClient = NotificationClient(server_uri=server_uri)
        self.last_scheduling_id = self._last_scheduler_job_id()

    @staticmethod
    def _last_scheduler_job_id():
        last_run = EventBasedSchedulerJob.most_recent_job()
        if not last_run:
            return None
        else:
            return last_run.id

    def _execute(self):
        self.log.info("Starting the scheduler Job")

        # DAGs can be pickled for easier remote execution by some executors
        #pickle_dags = self.do_pickle and self.executor_class not in UNPICKLEABLE_EXECUTORS

        try:
            self.mailbox.set_scheduling_job_id(self.id)
            self._start_listen_events()
            self.dag_trigger.start()
            self.task_event_manager.start()
            self.executor.job_id = self.id
            self.executor.start()

            self.register_signals()

            # Start after resetting orphaned tasks to avoid stressing out DB.

            execute_start_time = timezone.utcnow()

            self.scheduler.submit_sync_thread()
            self.scheduler.recover(self.last_scheduling_id)
            self.scheduler.schedule()

            self.executor.end()
            self.dag_trigger.end()
            self.task_event_manager.end()
            self._stop_listen_events()

            settings.Session.remove()  # type: ignore
        except Exception as e:  # pylint: disable=broad-except
            self.log.exception("Exception when executing scheduler, %s", e)
        finally:
            self.log.info("Exited execute loop")

    def _start_listen_events(self):
        watcher = SchedulerEventWatcher(self.mailbox)
        self.notification_client.start_listen_events(
            watcher=watcher,
            start_time=int(time.time() * 1000),
            version=None
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
