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
from typing import List, Text, Optional
import queue
import time
from airflow.contrib.jobs.event_based_scheduler_job import SCHEDULER_NAMESPACE
from airflow.events.scheduler_events import RequestEvent, SchedulerInnerEventType, \
    ResponseEvent, RunDagMessage, ExecuteTaskMessage, StopDagRunMessage
from airflow.executors.scheduling_action import SchedulingAction
from notification_service.base_notification import BaseEvent, EventWatcher
from notification_service.client import NotificationClient, ThreadEventWatcherHandle


class ExecutionContext(object):
    def __init__(self, dagrun_id):
        self.dagrun_id = dagrun_id


class ResponseWatcher(EventWatcher):
    def __init__(self):
        self.queue: queue.Queue = queue.Queue(1)

    def process(self, events: List[BaseEvent]):
        self.queue.put(events[0])

    def get_result(self, timeout: Optional[int] = None) -> object:
        if timeout is None:
            return self.queue.get()
        else:
            try:
                return self.queue.get(timeout=timeout)
            except queue.Empty:
                raise TimeoutError('Get response timeout({})'.format(timeout))


class EventSchedulerClient(object):
    def __init__(self, server_uri=None, namespace=None, ns_client=None):
        if ns_client is None:
            self.ns_client = NotificationClient(server_uri, namespace)
        else:
            self.ns_client = ns_client

    @staticmethod
    def generate_id(id):
        return '{}_{}'.format(id, time.time_ns())

    def trigger_parse_dag(self, file_path, timeout: Optional[int] = None) -> bool:
        id = self.generate_id('')
        watcher: ResponseWatcher = ResponseWatcher()
        handler: ThreadEventWatcherHandle \
            = self.ns_client.start_listen_event(key=id,
                                                event_type=SchedulerInnerEventType.PARSE_DAG_RESPONSE.value,
                                                namespace=SCHEDULER_NAMESPACE, watcher=watcher)

        self.ns_client.send_event(BaseEvent(key=id,
                                            event_type=SchedulerInnerEventType.PARSE_DAG_REQUEST.value,
                                            value=file_path))
        try:
            result = watcher.get_result(timeout=timeout)
        finally:
            handler.stop()
        return True

    def schedule_dag(self, dag_id, context: Text = None, timeout: Optional[int] = None) -> ExecutionContext:
        id = self.generate_id(dag_id)
        watcher: ResponseWatcher = ResponseWatcher()
        handler: ThreadEventWatcherHandle \
            = self.ns_client.start_listen_event(key=id,
                                                event_type=SchedulerInnerEventType.RESPONSE.value,
                                                namespace=SCHEDULER_NAMESPACE, watcher=watcher)
        self.ns_client.send_event(RequestEvent(request_id=id, body=RunDagMessage(dag_id, context).to_json()).to_event())
        try:
            result: ResponseEvent = ResponseEvent.from_base_event(watcher.get_result(timeout))
        finally:
            handler.stop()
        return ExecutionContext(dagrun_id=result.body)

    def stop_dag_run(self, dag_id, context: ExecutionContext, timeout: Optional[int] = None) -> ExecutionContext:
        id = self.generate_id(str(dag_id) + str(context.dagrun_id))
        watcher: ResponseWatcher = ResponseWatcher()
        handler: ThreadEventWatcherHandle \
            = self.ns_client.start_listen_event(key=id,
                                                event_type=SchedulerInnerEventType.RESPONSE.value,
                                                namespace=SCHEDULER_NAMESPACE, watcher=watcher)
        self.ns_client.send_event(RequestEvent(request_id=id,
                                               body=StopDagRunMessage(dag_id=dag_id,
                                                                      dagrun_id=context.dagrun_id)
                                               .to_json()).to_event())
        try:
            result: ResponseEvent = ResponseEvent.from_base_event(watcher.get_result(timeout))
        finally:
            handler.stop()
        return ExecutionContext(dagrun_id=result.body)

    def schedule_task(self, dag_id: str, task_id: str,
                      action: SchedulingAction, context: ExecutionContext,
                      timeout: Optional[int] = None) -> ExecutionContext:
        id = self.generate_id(context.dagrun_id)
        watcher: ResponseWatcher = ResponseWatcher()
        handler: ThreadEventWatcherHandle \
            = self.ns_client.start_listen_event(key=id,
                                                event_type=SchedulerInnerEventType.RESPONSE.value,
                                                namespace=SCHEDULER_NAMESPACE, watcher=watcher)
        self.ns_client.send_event(RequestEvent(request_id=id,
                                               body=ExecuteTaskMessage(dag_id=dag_id,
                                                                       task_id=task_id,
                                                                       dagrun_id=context.dagrun_id,
                                                                       action=action.value)
                                               .to_json()).to_event())
        try:
            result: ResponseEvent = ResponseEvent.from_base_event(watcher.get_result(timeout))
        finally:
            handler.stop()
        return ExecutionContext(dagrun_id=result.body)
