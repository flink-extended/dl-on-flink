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
import pickle
import queue
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from notification_service.base_notification import BaseEvent

from airflow.models.event_progress import EventProgress
from airflow.utils import timezone
from airflow.utils.session import provide_session
from airflow.models.message import Message, IdentifiedMessage, MessageState
from airflow.utils.log.logging_mixin import LoggingMixin


def put_message_to_queue(queue, message):
    queue.put(message)


class Mailbox(LoggingMixin):

    def __init__(self) -> None:
        super().__init__()
        self.queue = queue.Queue()
        self.scheduling_job_id = None
        self.sc = BackgroundScheduler()

    def start(self):
        self.sc.start()

    def stop(self):
        self.sc.shutdown()

    @provide_session
    def _save_message_to_db(self, message, queue_time, session=None) -> IdentifiedMessage:
        """ 1. save message to db
            2. update the event progress
        """
        try:
            if isinstance(message, BaseEvent) and message.version is not None and message.create_time is not None:
                progress = EventProgress(scheduling_job_id=self.scheduling_job_id,
                                         last_event_time=message.create_time,
                                         last_event_version=message.version)
                session.merge(progress)

            message_obj = Message(message)
            message_obj.state = MessageState.QUEUED
            message_obj.scheduling_job_id = self.scheduling_job_id
            message_obj.queue_time = queue_time
            session.add(message_obj)
            session.commit()
            return IdentifiedMessage(serialized_message=message_obj.data,
                                     msg_id=message_obj.id,
                                     queue_time=message_obj.queue_time)
        except Exception as e:
            session.rollback()
            raise e

    def send_message(self, message, queue_time=timezone.utcnow()):
        if not self.scheduling_job_id:
            self.log.warning("scheduling_job_id not set, missing messages cannot be recovered.")
        identified_message = self._save_message_to_db(message, queue_time)
        current_time = timezone.utcnow()
        if current_time >= queue_time:
            self.queue.put(identified_message)
        else:
            self.sc.add_job(func=put_message_to_queue,
                            args=(self.queue, identified_message),
                            trigger=DateTrigger(run_date=queue_time,
                                                timezone=pytz.timezone('UTC')))

    def get_message(self):
        identified_message: IdentifiedMessage = self.queue.get()
        try:
            return pickle.loads(identified_message.serialized_message)
        except Exception as e:
            self.log.error("Error occurred when load message from database, %s", e)
            return None

    def get_identified_message(self) -> IdentifiedMessage:
        return self.get_message_with_timeout(timeout=1)

    def length(self):
        return self.queue.qsize()

    def get_message_with_timeout(self, timeout=1):
        try:
            return self.queue.get(timeout=timeout)
        except Exception as e:
            return None

    def set_scheduling_job_id(self, scheduling_job_id):
        self.scheduling_job_id = scheduling_job_id
