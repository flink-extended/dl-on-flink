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
from multiprocessing import Queue
from typing import Text, List

from ai_flow.plugin_interface.scheduler_interface import Scheduler
from ai_flow.scheduler_service.service.workflow_event_processor import WorkflowEventProcessor
from ai_flow.store.abstract_store import AbstractStore
from notification_service.base_notification import EventWatcher, BaseEvent
from notification_service.client import NotificationClient


class WorkflowEventWatcher(EventWatcher):
    def __init__(self, event_queue: Queue):
        self._event_queue = event_queue

    def process(self, events: List[BaseEvent]):
        for event in events:
            self._event_queue.put(event)


class WorkflowEventManager(object):
    """
    WorkflowEventManager
    """

    def __init__(self, notification_uri: Text, store: AbstractStore, scheduler: Scheduler):
        """

        :param notification_uri:
        :param store:
        :param scheduler:
        """
        self.notification_client = NotificationClient(server_uri=notification_uri)

        self.event_queue: Queue = Queue()
        self.event_watcher = WorkflowEventWatcher(self.event_queue)
        self.listen_event_handler = None
        self.event_processor = WorkflowEventProcessor(self.event_queue, store, scheduler)

    def start(self):
        logging.info("WorkflowEventManager start listening event")
        self.listen_event_handler = self.notification_client.start_listen_events(self.event_watcher)
        self.event_processor.start()

    def stop(self):
        if self.listen_event_handler:
            self.listen_event_handler.stop()
        self.event_queue.close()
        self.event_processor.stop()
        self.event_processor.join()






