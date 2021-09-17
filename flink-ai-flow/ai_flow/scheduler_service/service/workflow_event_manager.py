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
import logging
import multiprocessing as mp
import threading
import time
from typing import Text, List

from ai_flow.endpoint.server.server_config import DBType
from ai_flow.plugin_interface.scheduler_interface import SchedulerFactory
from ai_flow.scheduler_service.service.config import SchedulerServiceConfig
from ai_flow.scheduler_service.service.workflow_event_processor import Poison, WorkflowEventProcessor
from ai_flow.store.db.db_util import extract_db_engine_from_uri, parse_mongo_uri
from ai_flow.store.mongo_store import MongoStore
from ai_flow.store.sqlalchemy_store import SqlAlchemyStore
from notification_service.base_notification import EventWatcher, BaseEvent
from notification_service.client import NotificationClient

# Method to start the WorkflowEventProcessor
_MP_START_METHOD = 'spawn'


def _start_workflow_event_processor_process(conn, db_uri: Text, scheduler_service_config: SchedulerServiceConfig):
    db_engine = extract_db_engine_from_uri(db_uri)
    if DBType.value_of(db_engine) == DBType.MONGODB:
        username, password, host, port, db = parse_mongo_uri(db_uri)
        store = MongoStore(host=host,
                           port=int(port),
                           username=username,
                           password=password,
                           db=db)
    else:
        store = SqlAlchemyStore(db_uri)

    scheduler = SchedulerFactory.create_scheduler(scheduler_service_config.scheduler().scheduler_class(),
                                                  scheduler_service_config.scheduler().scheduler_config())
    processor = WorkflowEventProcessor(conn=conn, store=store, scheduler=scheduler)
    processor.run()


class WorkflowEventManager(object):
    """
    WorkflowEventManager
    """

    def __init__(self, notification_uri: Text,
                 db_uri: Text,
                 scheduler_service_config: SchedulerServiceConfig):
        self.db_uri = db_uri
        self.scheduler_service_config = scheduler_service_config
        self.notification_client = NotificationClient(server_uri=notification_uri)
        self.listen_event_handler = None

        self._stop = False
        self.event_processor_process = self._create_event_processor_process()
        self.process_watcher_thread = threading.Thread(target=self._watch_process)
        self.event_watcher = WorkflowEventWatcher(self.conn)

    def _create_event_processor_process(self):
        # We use spawn to start the process to avoid problem of running grpc in multiple processes.
        # As we only spawn the new process once when the Scheduler service start, the performance drawback of spawn is
        # acceptable.
        ctx = mp.get_context(_MP_START_METHOD)
        self.processor_conn, self.conn = ctx.Pipe(False)
        return ctx.Process(target=_start_workflow_event_processor_process,
                           args=(self.processor_conn, self.db_uri, self.scheduler_service_config),
                           name="WorkflowEventProcessor")

    def start(self):
        logging.info("WorkflowEventManager start listening event")
        self.listen_event_handler = self.notification_client.start_listen_events(self.event_watcher)
        self.event_processor_process.start()
        self.process_watcher_thread.start()

    def stop(self):
        logging.info("stopping WorkflowEventManager...")
        self._stop = True
        self.process_watcher_thread.join()
        if self.listen_event_handler:
            self.listen_event_handler.stop()
        if self.event_processor_process.is_alive():
            self.conn.send(Poison())
        self.event_processor_process.join()
        logging.info("WorkflowEventManager stopped...")

    def notify_event_arrived(self, event: BaseEvent):
        for i in range(10):
            try:
                self.conn.send(event)
                break
            except Exception as e:
                logging.warning("Error sending event to connection, retrying ({}/10)...".format(i),
                                exc_info=e)
                time.sleep(1)

    def _watch_process(self):
        while not self._stop:
            if self.event_processor_process.is_alive():
                time.sleep(1.)
                continue

            self.event_processor_process.join()
            logging.info("WorkflowEventProcessor pid: {} exited with code: {}".format(
                self.event_processor_process.pid,
                self.event_processor_process.exitcode))
            if self._stop:
                break
            logging.info("Restarting process")
            self.event_processor_process = self._create_event_processor_process()
            self.event_processor_process.start()
            logging.info("Process restarted with pid: {}".format(self.event_processor_process.pid))
        logging.info("Stop watching process")


class WorkflowEventWatcher(EventWatcher):
    def __init__(self, workflow_event_manager: WorkflowEventManager):
        self._workflow_event_manager = workflow_event_manager

    def process(self, events: List[BaseEvent]):
        for event in events:
            self._workflow_event_manager.notify_event_arrived(event)
