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
#
from abc import abstractmethod, ABCMeta
from typing import List, Union, Dict, Text, Optional
from threading import Thread, Lock
import time
import copy
import traceback
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from notification_service.base_notification import BaseEvent

from ai_flow.workflow.workflow import Workflow
from ai_flow.deployer.listener import ListenerManager, SimpleEvent, JobStatusEvent
from ai_flow.deployer.job_submitter import JobSubmitterManager, get_default_job_submitter_manager
from ai_flow.workflow.job import BaseJob
from ai_flow.workflow.job_handler import BaseJobHandler
from ai_flow.graph.edge import JobControlEdge, MetCondition
from ai_flow.meta.job_meta import State
from ai_flow.deployer.kv_store import BaseKVStore, MemoryKVStore
from ai_flow.graph.edge import generate_job_status_key
from ai_flow.endpoint.client.aiflow_client import AIFlowClient
from ai_flow.meta.job_meta import JobMeta
from ai_flow.graph.edge import EventLife, TaskAction, MetValueCondition
from ai_flow.deployer.utils.kubernetes_util import load_kubernetes_config
from ai_flow.common.message_queue import MessageQueue


class BaseScheduler(metaclass=ABCMeta):

    def __init__(self, client: AIFlowClient,
                 workflow: Workflow) -> None:
        self.client = client
        self.job_submitter_manager: JobSubmitterManager = get_default_job_submitter_manager()
        self.workflow: Workflow = workflow

    @abstractmethod
    def schedule(self) -> int:
        pass

    def stop(self) -> int:
        pass


def is_periodic_job(job: BaseJob) -> bool:
    if job.job_config.periodic_config is None:
        return False
    else:
        return True


PERIODIC_EVENT_VALUE = "schedule"


def generate_periodic_key(job: BaseJob) -> Text:
    return "periodic_config_{}_key".format(job.instance_id)


class EventScheduler(BaseScheduler):

    def __init__(self, client: AIFlowClient, listener_manager: ListenerManager, workflow: Workflow) -> None:
        super().__init__(client, workflow)
        self.kv_store: BaseKVStore = MemoryKVStore()
        self.listener_manager: ListenerManager = listener_manager
        self.finished_jobs = set()
        self.running_jobs = set()
        self.starting_jobs = set()
        self.init_jobs = set()
        self.failed_jobs = set()
        self.job_size = len(workflow.jobs)
        self.no_dependent_job_size = self.job_size - len(workflow.edges)
        for job_id in workflow.jobs.keys():
            self.init_jobs.add(job_id)
        # key = job instance_id
        self.listen_job_handlers: Dict[Text, BaseJobHandler] = {}
        self.job_periodic_trigger: BackgroundScheduler = BackgroundScheduler()
        self.schedule_job_time = {}
        # job stat change lock
        self.stat_lock = Lock()
        self.running_lock = Lock()
        self.message_queue: MessageQueue = MessageQueue()
        self.running = True
        self.log = logging.getLogger()

    def can_finish(self) -> bool:
        res = True
        for job in self.workflow.jobs.values():
            if is_periodic_job(job):
                res = False
                break
        return res

    def get_event(self):
        return self.message_queue.get()

    def get_event_with_timeout(self, timeout):
        return self.message_queue.get_with_timeout(timeout=timeout)

    def have_event(self)->bool:
        return self.message_queue.length() > 0

    def send_event(self, message):
        self.message_queue.send(message)

    def can_schedule(self, job: BaseJob) -> bool:
        if job.instance_id in self.workflow.edges:
            edges: List[JobControlEdge] = self.workflow.edges[job.instance_id]
            has_necessary_edge = False
            for e in edges:
                if e.met_config.condition == MetCondition.SUFFICIENT:
                    key = e.met_config.event_key
                    value = e.met_config.event_value
                    if not self.kv_store.in_store(key):
                        continue
                    v, event_time = self.kv_store.get_value_and_time(key)
                    if e.met_config.life == EventLife.ONCE:
                        if e.met_config.value_condition == MetValueCondition.EQUAL:
                            if v == value and event_time > self.schedule_job_time[job.instance_id]:
                                return True
                        else:
                            if event_time > self.schedule_job_time[job.instance_id]:
                                return True
                    else:
                        if e.met_config.value_condition == MetValueCondition.EQUAL:
                            if v == value:
                                return True
                        else:
                            return True
                else:
                    has_necessary_edge = True
                    key = e.met_config.event_key
                    value = e.met_config.event_value
                    if not self.kv_store.in_store(key):
                        return False
                    v, event_time = self.kv_store.get_value_and_time(key)
                    if e.met_config.life == EventLife.ONCE:
                        if e.met_config.value_condition == MetValueCondition.EQUAL:
                            if self.schedule_job_time[job.instance_id] > event_time:
                                return False
                            else:
                                if v != value:
                                    return False
                        else:
                            if self.schedule_job_time[job.instance_id] > event_time:
                                return False

                    else:
                        if e.met_config.value_condition == MetValueCondition.EQUAL:
                            if v != value:
                                return False

                        else:
                            if v is None:
                                return False
            if has_necessary_edge:
                return True
            else:
                return False

        else:
            if is_periodic_job(job):
                if self.kv_store.get(generate_periodic_key(job)) == PERIODIC_EVENT_VALUE:
                    return True
                else:
                    return False
            else:
                return True

    def register_job_meta(self, workflow_id: int, job: BaseJob):
        start_time = time.time()
        if job.job_config.job_name is None:
            name = job.instance_id
        else:
            name = job.job_config.job_name
        job_name = str(workflow_id) + '_' + name + '_' + str(start_time)
        job_meta: JobMeta = self.client.register_job(name=job_name,
                                                     job_id=job.instance_id,
                                                     workflow_execution_id=workflow_id,
                                                     start_time=round(start_time))
        job.uuid = job_meta.uuid
        job.job_name = job_name
        # fill job context
        job.job_context.job_uuid = job.uuid
        job.job_context.job_name = job.job_name
        job.job_context.job_instance_id = job.instance_id

    def set_restart_stop_jobs(self):
        self.stat_lock.acquire()
        try:
            restart_set = set()
            for job_id in self.running_jobs:
                job = self.workflow.jobs[job_id]
                if job_id in self.workflow.edges:
                    edges: List[JobControlEdge] = self.workflow.edges[job.instance_id]
                    for e in edges:
                        if e.met_config.action == TaskAction.RESTART:
                            if self.can_schedule(job):
                                restart_set.add(job_id)

            # set restart job
            for job_id in restart_set:
                job = self.workflow.jobs[job_id]
                if job.instance_id in self.listen_job_handlers:
                    self.listener_manager.stop_job_handler_listening(self.listen_job_handlers[job_id])
                    del self.listen_job_handlers[job_id]
                self.job_submitter_manager.stop_job(job)
                self.client.update_job(job_name=job.job_name, job_state=State.FINISHED)
                self.running_jobs.remove(job_id)
                self.init_jobs.add(job_id)

            # set stop job
            stop_set = set()
            for job_id in (self.running_jobs | self.init_jobs | self.starting_jobs):
                job = self.workflow.jobs[job_id]
                if job_id in self.workflow.edges:
                    edges: List[JobControlEdge] = self.workflow.edges[job.instance_id]
                    for e in edges:
                        if e.met_config.action == TaskAction.STOP:
                            if self.can_schedule(job):
                                stop_set.add(job_id)
            for job_id in stop_set:
                job = self.workflow.jobs[job_id]
                if job.instance_id in self.listen_job_handlers:
                    self.listener_manager.stop_job_handler_listening(self.listen_job_handlers[job_id])
                    del self.listen_job_handlers[job_id]
                self.job_submitter_manager.stop_job(job)
                self.client.update_job(job_name=job.job_name, job_state=State.FINISHED)
                self.running_jobs.discard(job_id)
                self.init_jobs.discard(job_id)
                self.starting_jobs.discard(job_id)
                self.finished_jobs.add(job_id)

        finally:
            self.stat_lock.release()

    def do_schedule(self):
        self.running_lock.acquire()
        try:
            self.set_restart_stop_jobs()
            current_init_job_set = copy.deepcopy(self.init_jobs)
            for job_id in current_init_job_set:
                job = self.workflow.jobs[job_id]
                if self.can_schedule(job=job):
                    self.register_job_meta(self.workflow.workflow_id, job)

                    self.send_event(JobStatusEvent(workflow_id=job.job_context.workflow_execution_id,
                                                   job_id=job.instance_id,
                                                   status=State.INIT.value))
                    job.status = State.INIT
                    self.client.update_job(job_name=job.job_name, job_state=State.INIT)
                    self.schedule_job_time[job.instance_id] = time.time()
                    job_handler = self.job_submitter_manager.submit_job(job)
                    self.send_event(JobStatusEvent(workflow_id=job.job_context.workflow_execution_id,
                                                   job_id=job.instance_id,
                                                   status=State.STARTING.value))
                    job.status = State.STARTING
                    self.stat_lock.acquire()
                    try:
                        self.init_jobs.remove(job_id)
                        self.starting_jobs.add(job_id)
                    finally:
                        self.stat_lock.release()

                    # reset periodic job in kv store
                    if is_periodic_job(job):
                        self.kv_store.update(generate_periodic_key(job), None)

                    self.client.update_job(job_name=job.job_name, job_state=State.STARTING)
                    self.listener_manager.register_job_handler_listening(job_handler)

                    self.listen_job_handlers[job_handler.job_instance_id] = job_handler

        except Exception as e:
            traceback.print_exc()
            raise e
        finally:
            self.running_lock.release()

    def set_repeated_jobs(self):
        self.stat_lock.acquire()
        try:
            repeatable_jobs = set()
            for job_id in self.finished_jobs:
                if is_periodic_job(self.workflow.jobs[job_id]):
                    repeatable_jobs.add(job_id)
                if job_id in self.workflow.edges:
                    repeatable_jobs.add(job_id)

            for jid in repeatable_jobs:
                self.job_submitter_manager.stop_job(self.workflow.jobs[jid])
                self.finished_jobs.remove(jid)
                self.init_jobs.add(jid)
        finally:
            self.stat_lock.release()

    # needed ?
    def register_listener(self):
        for edges in self.workflow.edges.values():
            for edge in edges:
                event_type = edge.met_config.event_type
                event_key = edge.met_config.event_key
                if event_type is not None:
                    notifications = self.client.list_events(key=event_key)
                    if 0 == len(notifications):
                        event_version = None
                    else:
                        event_version = notifications[-1].version
                    self.listener_manager.start_listen_event(event_type=event_type,
                                                             event_key=event_key,
                                                             event_version=event_version)
                    self.listener_manager.message_dispatcher\
                        .listen_event_key(self.workflow.workflow_id, event_key, event_type)

    def init_schedule_time(self):
        for job in self.workflow.jobs.values():
            self.schedule_job_time[job.instance_id] = 0.0

    def init_kv_store(self):
        # periodic job
        for job in self.workflow.jobs.values():
            if is_periodic_job(job):
                self.kv_store.update(generate_periodic_key(job), None)

    def register_periodic_job(self):
        def set_periodic_event(job: BaseJob):
            self.send_event(SimpleEvent(key=generate_periodic_key(job),
                                        value=PERIODIC_EVENT_VALUE))

        for job in self.workflow.jobs.values():
            if is_periodic_job(job):
                periodic_config = job.job_config.periodic_config
                if periodic_config.periodic_type == 'cron':
                    self.job_periodic_trigger.add_job(set_periodic_event, 'cron', **periodic_config.args,
                                                      args=[job])
                elif periodic_config.periodic_type == 'interval':
                    set_periodic_event(job)
                    self.job_periodic_trigger.add_job(set_periodic_event, 'interval', **periodic_config.args,
                                                      args=[job])
                else:
                    raise Exception("do not support periodic config type {}".format(periodic_config.periodic_type))
        self.job_periodic_trigger.start()

    def schedule_is_finish(self) -> bool:
        if len(self.failed_jobs) > 0:
            return True

        if self.can_finish():
            if len(self.finished_jobs) == self.no_dependent_job_size \
                    and len(self.running_jobs) == 0 \
                    and len(self.starting_jobs) == 0 \
                    and self.message_queue.length() == 0:
                return True
            else:
                return False
        else:
            return False

    def update_kv_store(self, event: Union[BaseEvent, JobStatusEvent]):
        if isinstance(event, BaseEvent):
            self.kv_store.update(event.key, event.value)
        elif isinstance(event, JobStatusEvent):
            if event.job_id not in self.workflow.jobs:
                return
            job = self.workflow.jobs[event.job_id]
            self.log.info("workflow_id {} job_name {} status {}".format(event.workflow_id, job.job_name, event.status))
            key = generate_job_status_key(event.job_id)
            self.kv_store.update(key, event.status)
            job = self.workflow.jobs[event.job_id]
            if State.RUNNING == State(event.status):
                self.stat_lock.acquire()
                try:
                    self.starting_jobs.discard(event.job_id)
                    self.running_jobs.add(event.job_id)
                    job.status = State.RUNNING
                    self.client.update_job(job_name=job.job_name, job_state=State.RUNNING)
                finally:
                    self.stat_lock.release()

            elif State.FINISHED == State(event.status):
                self.stat_lock.acquire()
                try:
                    self.finished_jobs.add(event.job_id)
                    self.starting_jobs.discard(event.job_id)
                    self.running_jobs.discard(event.job_id)
                    job.status = State.FINISHED
                    end_time = round(time.time())
                    job.end_time = end_time
                    self.client.update_job(job_name=job.job_name, job_state=State.FINISHED)
                    self.client.update_job(job_name=job.job_name, end_time=end_time)
                    if job.instance_id in self.listen_job_handlers:
                        self.listener_manager.stop_job_handler_listening(self.listen_job_handlers[job.instance_id])
                        del self.listen_job_handlers[job.instance_id]
                finally:
                    self.stat_lock.release()
            elif State.FAILED == State(event.status):
                self.stat_lock.acquire()
                try:
                    self.failed_jobs.add(event.job_id)
                    self.running_jobs.discard(event.job_id)
                    self.starting_jobs.discard(event.job_id)
                    job.status = State.FAILED
                    end_time = round(time.time())
                    job.end_time = end_time
                    self.client.update_job(job_name=job.job_name, job_state=State.FAILED)
                    self.client.update_job(job_name=job.job_name, end_time=end_time)
                    if job.instance_id in self.listen_job_handlers:
                        self.listener_manager.stop_job_handler_listening(self.listen_job_handlers[job.instance_id])
                        del self.listen_job_handlers[job.instance_id]
                finally:
                    self.stat_lock.release()

            else:
                pass

    def clean_resource(self):
        # stop listen event
        for edges in self.workflow.edges.values():
            for edge in edges:
                event_type = edge.met_config.event_type
                event_key = edge.met_config.event_key
                if event_type is not None:
                    self.listener_manager.stop_listen_event(event_type=event_type,
                                                            event_key=event_key)
                    self.listener_manager.message_dispatcher\
                        .release_event_key(self.workflow.workflow_id, event_key, event_type)

        # stop listen job
        for job_handler in self.listen_job_handlers.values():
            self.listener_manager.stop_job_handler_listening(job_handler)

        # deregister message queue
        self.listener_manager.deregister_message_queue(self.workflow.workflow_id)

        # job submitter clean up job resource
        for job in self.workflow.jobs.values():
            self.job_submitter_manager.cleanup_job(job)

        # periodic job clean up
        if self.job_periodic_trigger.running:
            self.job_periodic_trigger.shutdown()

    def schedule(self) -> int:
        """
        :return: success 0, failed 1
        """
        if self.workflow.workflow_id is None or not isinstance(self.workflow.workflow_id, int):
            return 1
        self.listener_manager.register_message_queue(self.workflow.workflow_id, self.message_queue)

        # update workflow execution state
        self.client.update_workflow_execution(execution_name=self.workflow.execution_name,
                                              execution_state=State.RUNNING)
        res = 0

        # register listener
        self.register_listener()

        # init schedule job time
        self.init_schedule_time()

        # init kv store
        self.init_kv_store()

        # register periodic job
        self.register_periodic_job()

        self.do_schedule()
        # get event and do schedule
        while not self.schedule_is_finish():
            event = self.get_event()
            if isinstance(event, StopSchedulerEvent):
                break

            self.update_kv_store(event)
            self.do_schedule()
            self.set_repeated_jobs()
        if len(self.failed_jobs) > 0:
            self.log.info("failed job {}".format(str(self.failed_jobs)))
            self.stop()
            res = 1
        else:
            self.log.info("schedule finish {}".format(self.workflow.execution_name))
            self.client.update_workflow_execution(execution_name=self.workflow.execution_name,
                                                  execution_state=State.FINISHED)

        # clean resource
        self.clean_resource()
        self.running = False
        return res

    def stop(self):
        self.running_lock.acquire()
        try:
            for job in self.workflow.jobs.values():
                if job.status == State.RUNNING or job.status == State.STARTING:
                    self.job_submitter_manager.stop_job(job)
                    job.status = State.FINISHED
        finally:
            self.running_lock.release()
        self.clean_resource()
        self.client.update_workflow_execution(execution_name=self.workflow.execution_name,
                                              execution_state=State.FINISHED)
        self.send_event(StopSchedulerEvent())
        self.running = False


class StopSchedulerEvent(object):
    pass


class SchedulerThread(Thread):
    def __init__(self, scheduler: BaseScheduler) -> None:
        super().__init__()
        self.scheduler = scheduler
        self.schedule_code = None
        self.log = logging.getLogger()

    def run(self):
        state = State.FAILED
        error_message = ''
        try:
            self.schedule_code = self.scheduler.schedule()
            if 0 == self.schedule_code:
                state = State.FINISHED
            else:
                state = State.FAILED
                error_message = 'have failed job'
        except Exception as e:
            self.log.info(e)
            traceback.print_exc()
            error_message = traceback.format_exc()
            state = State.FAILED

        finally:
            self.scheduler.client.update_workflow_execution(execution_name=self.scheduler.workflow.execution_name,
                                                            execution_state=state,
                                                            end_time=round(time.time()),
                                                            properties={'error_message': error_message})


class SchedulerPool(Thread):
    def __init__(self,
                 client: AIFlowClient,
                 listener_manager: ListenerManager) -> None:
        super().__init__()
        self.client: AIFlowClient = client
        self.listener_manager: ListenerManager = listener_manager
        self.scheduler_threads: Dict[int, Thread] = {}
        self.scheduler_instances: Dict[int, BaseScheduler] = {}
        self.running = True
        self.lock = Lock()

    def run(self):
        while self.running:
            self.lock.acquire()
            try:
                finished_threads = set()
                for k, v in self.scheduler_threads.items():
                    if not v.is_alive():
                        finished_threads.add(k)
                for workflow_id in finished_threads:
                    del self.scheduler_threads[workflow_id]
                    del self.scheduler_instances[workflow_id]
            finally:
                self.lock.release()
            time.sleep(5)

    def set_stop(self):
        self.running = False

    def start_scheduler(self, workflow: Workflow):

        def start_scheduler(scheduler: BaseScheduler) -> Thread:
            thread = SchedulerThread(scheduler=scheduler)
            thread.setDaemon(True)
            thread.setName("scheduler-" + str(scheduler.workflow.workflow_id))
            thread.start()
            scheduler.client.update_workflow_execution(execution_name=scheduler.workflow.execution_name,
                                                       execution_state=State.STARTING)
            return thread

        scheduler_instance = EventScheduler(client=self.client,
                                            listener_manager=self.listener_manager,
                                            workflow=workflow)
        self.lock.acquire()
        try:
            self.scheduler_instances[workflow.workflow_id] = scheduler_instance
            self.scheduler_threads[workflow.workflow_id] = start_scheduler(scheduler_instance)
        finally:
            self.lock.release()

    def stop_scheduler_by_workflow_id(self, workflow_id: int):
        if workflow_id in self.scheduler_instances:
            scheduler_thread = self.scheduler_threads[workflow_id]
            if scheduler_thread.is_alive():
                scheduler = self.scheduler_instances[workflow_id]
                scheduler.stop()
        else:
            raise Exception("{} workflow do not running".format(workflow_id))

    def get_schedule_result(self, workflow_id: int) -> Optional[int]:
        if workflow_id in self.scheduler_instances:
            scheduler_thread: SchedulerThread = self.scheduler_threads[workflow_id]
            if scheduler_thread.is_alive():
                return None
            else:
                return scheduler_thread.schedule_code
        else:
            execution_meta = self.client.get_workflow_execution_by_id(execution_id=workflow_id)
            if execution_meta is None:
                raise Exception("{} workflow do not exist".format(workflow_id))
            else:
                if State.FINISHED == execution_meta.execution_state:
                    return 0
                elif State.FAILED == execution_meta.execution_state:
                    return 1
                else:
                    return None

    def workflow_is_alive(self, workflow_id: int) -> Optional[bool]:
        if workflow_id in self.scheduler_threads:
            return self.scheduler_threads[workflow_id].scheduler.running
        else:
            return False

    def wait_finished(self, workflow_id: int):
        if workflow_id in self.scheduler_threads:
            self.scheduler_threads[workflow_id].join()

    def stop_all_scheduler(self):
        self.lock.acquire()
        try:
            for sc in self.scheduler_instances.values():
                sc.stop()
            self.scheduler_instances.clear()
            self.scheduler_threads.clear()
        finally:
            self.lock.release()

    def get_scheduler_count(self):
        return len(self.scheduler_threads)


class SchedulerManager(object):

    def __init__(self, server_uri: Text) -> None:
        load_kubernetes_config(None)
        self.server_uri = server_uri
        self.listener_manager: ListenerManager = None
        self.client: AIFlowClient = None
        self.scheduler_pool: SchedulerPool = None

    def schedule_workflow(self, workflow: Workflow) -> Optional[int]:
        self.scheduler_pool.start_scheduler(workflow)
        return workflow.workflow_id

    def stop_schedule_workflow(self, workflow_id: int):
        self.scheduler_pool.stop_scheduler_by_workflow_id(workflow_id)

    def get_schedule_result(self, workflow_id: int) -> Optional[int]:
        return self.scheduler_pool.get_schedule_result(workflow_id)

    def workflow_is_alive(self, workflow_id: int) -> Optional[bool]:
        return self.scheduler_pool.workflow_is_alive(workflow_id)

    def wait_finished(self, workflow_id: int):
        self.scheduler_pool.wait_finished(workflow_id)

    def get_scheduler_count(self):
        return self.scheduler_pool.get_scheduler_count()

    def start(self):
        self.client = AIFlowClient(server_uri=self.server_uri)
        self.listener_manager = ListenerManager(client=self.client)
        self.listener_manager.start_dispatcher()
        self.listener_manager.start_job_status_listener()
        self.scheduler_pool = SchedulerPool(client=self.client,
                                            listener_manager=self.listener_manager)
        self.scheduler_pool.setDaemon(True)
        self.scheduler_pool.setName("scheduler-pool")
        self.scheduler_pool.start()

    def stop(self):
        self.listener_manager.stop_dispatcher()
        self.listener_manager.stop_listen_all_events()
        self.listener_manager.stop_job_status_listener()
        self.scheduler_pool.stop_all_scheduler()
        self.scheduler_pool.set_stop()
