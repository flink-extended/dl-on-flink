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
import threading
from threading import Thread
from typing import List, Dict, Text
from typing import Set, Tuple
from ai_flow.common.message_queue import MessageQueue
from ai_flow.common.registry import BaseRegistry
from notification_service.base_notification import BaseEvent, EventWatcher, UNDEFINED_EVENT_TYPE
from ai_flow.workflow.job_handler import BaseJobHandler


class SimpleEvent(BaseEvent):

    def __init__(self, key, value, event_type=UNDEFINED_EVENT_TYPE) -> None:
        super().__init__(key, value, event_type=event_type)


class EventListenerWatcher(EventWatcher):
    def __init__(self, message_queue: MessageQueue):
        super().__init__()
        self.message_queue = message_queue

    def process(self, events: List[BaseEvent]):
        for event in events:
            event = SimpleEvent(key=event.key, value=event.value, event_type=event.event_type)
            self.message_queue.send(event)


class EventListener(object):
    def __init__(self, client, watcher) -> None:
        self.client = client
        self.listen_record: Set[Tuple] = set()
        self.watcher = watcher
        self.lock = threading.Lock()

    def start_listen(self, event_type, event_key, event_version=None):
        self.client.start_listen_event(key=event_key, version=event_version, watcher=self.watcher)
        self.lock.acquire()
        try:
            self.listen_record.add((event_type, event_key))
        finally:
            self.lock.release()

    def stop_listen(self, event_type, event_key):
        self.client.stop_listen_event(key=event_key)
        self.lock.acquire()
        try:
            self.listen_record.discard((event_type, event_key))
        finally:
            self.lock.release()

    def stop_listen_all(self):
        self.lock.acquire()
        try:
            for i in self.listen_record:
                self.client.stop_listen_event(key=i[1])
            self.listen_record.clear()
        finally:
            self.lock.release()


class JobStatusEvent(object):

    def __init__(self, workflow_id: int, job_id: Text, status: Text) -> None:
        self.workflow_id = workflow_id
        self.job_id = job_id
        self.status = status


class BaseJobStatusListener(Thread):

    def __init__(self, platform) -> None:
        """

        :param platform:
        """
        super().__init__()
        self.platform = platform
        self.message_queue: MessageQueue = None

    def set_message_queue(self, message_queue: MessageQueue):
        self.message_queue = message_queue

    def start_listen(self):
        """
        """
        pass

    def stop_listen(self):
        pass

    def register_job_listening(self, job_handler: BaseJobHandler):
        """

        :param job_handler:
        """
        pass

    def stop_job_listening(self, job_id: int):
        """

        :param job_id:
        """
        pass


class JobStatusListenerManager(BaseRegistry):
    def __init__(self):
        super().__init__()
        self.object_dict: Dict[Text, BaseJobStatusListener] = {}
        self.listener_threads: Dict[Text, Thread] = {}

    def set_message_queue(self, message_queue: MessageQueue):
        for key in self.object_dict.keys():
            listener: BaseJobStatusListener = self.get_object(key)
            listener.set_message_queue(message_queue)

    def start_all_listeners(self):
        for key in self.object_dict.keys():
            listener: BaseJobStatusListener = self.get_object(key)
            listener.start_listen()
            self.listener_threads[key] = listener

    def stop_all_listeners(self):
        for key in self.object_dict.keys():
            listener: BaseJobStatusListener = self.get_object(key)
            listener.stop_listen()


_default_job_status_manager = JobStatusListenerManager()


def register_job_status_listener(listener: BaseJobStatusListener):
    _default_job_status_manager.register(listener.platform, listener)


class MessageDispatcher(Thread):
    def __init__(self, main_message_queue: MessageQueue) -> None:
        super().__init__()
        self.main_message_queue = main_message_queue
        # key: workflow_id value: scheduler message_queue
        self.message_queue_map: Dict[int, MessageQueue] = {}
        # key: event_key
        self.event_key_map: Dict[(Text, Text), Set[int]] = {}
        self.running_flag = True
        self.setDaemon(True)
        self.setName("message-dispatcher")
        self.mq_lock = threading.Lock()
        self.sg_lock = threading.Lock()

    def register_message_queue(self, workflow_id: int, mq: MessageQueue):
        self.mq_lock.acquire()
        try:
            self.message_queue_map[workflow_id] = mq
        finally:
            self.mq_lock.release()

    def deregister_message_queue(self, workflow_id: int):
        self.mq_lock.acquire()
        try:
            if workflow_id in self.message_queue_map:
                del self.message_queue_map[workflow_id]
        finally:
            self.mq_lock.release()

    def listen_event_key(self, workflow_id: int, event_key: Text, event_type: Text = UNDEFINED_EVENT_TYPE):
        self.sg_lock.acquire()
        try:
            if (event_key, event_type) not in self.event_key_map:
                self.event_key_map[(event_key, event_type)] = set()
            self.event_key_map[(event_key, event_type)].add(workflow_id)
        finally:
            self.sg_lock.release()

    def release_event_key(self, workflow_id: int, event_key: Text, event_type: Text = UNDEFINED_EVENT_TYPE):
        self.sg_lock.acquire()
        try:
            if (event_key, event_type) in self.event_key_map:
                self.event_key_map[(event_key, event_type)].discard(workflow_id)
                if 0 == len(self.event_key_map[(event_key, event_type)]):
                    del self.event_key_map[(event_key, event_type)]
        finally:
            self.sg_lock.release()

    def run(self):
        while self.running_flag:
            event = self.main_message_queue.get_with_timeout(timeout=2)
            if event is None:
                # no event
                continue
            else:
                self.mq_lock.acquire()
                try:
                    if isinstance(event, BaseEvent):
                        event_key = event.key
                        event_type = event.event_type
                        self.sg_lock.acquire()
                        try:
                            if (event_key, event_type) in self.event_key_map:
                                for w_id in self.event_key_map[(event_key, event_type)]:
                                    if w_id in self.message_queue_map:
                                        self.message_queue_map[w_id].send(event)
                        finally:
                            self.sg_lock.release()
                    elif isinstance(event, JobStatusEvent):
                        workflow_id = event.workflow_id
                        if workflow_id in self.message_queue_map:
                            self.message_queue_map[workflow_id].send(event)
                finally:
                    self.mq_lock.release()

    def stop_dispatcher(self):
        self.running_flag = False
        self.join()


class ListenerManager(object):
    def __init__(self, client):
        self.message_queue = MessageQueue()
        watcher = EventListenerWatcher(self.message_queue)
        self.event_listener: EventListener = EventListener(client=client, watcher=watcher)
        self.job_status_listener_manager = _default_job_status_manager
        self.job_status_listener_manager.set_message_queue(self.message_queue)
        # key workflow_id; value scheduler message queue
        self.message_dispatcher: MessageDispatcher = MessageDispatcher(main_message_queue=self.message_queue)

    def start_dispatcher(self):
        self.message_dispatcher.start()

    def stop_dispatcher(self):
        self.message_dispatcher.stop_dispatcher()
        if self.message_dispatcher.is_alive():
            self.message_dispatcher.join()

    def get_event(self):
        return self.message_queue.get()

    def send_event(self, event):
        self.message_queue.send(event)

    def register_message_queue(self, workflow_id: int, mq: MessageQueue):
        self.message_dispatcher.register_message_queue(workflow_id, mq)

    def deregister_message_queue(self, workflow_id: int):
        self.message_dispatcher.deregister_message_queue(workflow_id)

    def start_job_status_listener(self):
        self.job_status_listener_manager.start_all_listeners()

    def stop_job_status_listener(self):
        self.job_status_listener_manager.stop_all_listeners()

    def register_job_handler_listening(self, job_handler: BaseJobHandler):
        job_listener: BaseJobStatusListener = self.job_status_listener_manager.get_object(job_handler.platform)
        job_listener.register_job_listening(job_handler)

    def stop_job_handler_listening(self, job_handler: BaseJobHandler):
        job_listener: BaseJobStatusListener = self.job_status_listener_manager.get_object(job_handler.platform)
        job_listener.stop_job_listening(job_handler.job_uuid)

    def start_listen_event(self, event_type, event_key, event_version=None):
        self.event_listener.start_listen(event_type=event_type, event_key=event_key, event_version=event_version)

    def stop_listen_event(self, event_type, event_key):
        self.event_listener.stop_listen(event_type=event_type, event_key=event_key)

    def stop_listen_all_events(self):
        self.event_listener.stop_listen_all()
