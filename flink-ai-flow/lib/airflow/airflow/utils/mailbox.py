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

from airflow.configuration import conf
from airflow.models.message import Message, IdentifiedMessage
from airflow.utils.log.logging_mixin import LoggingMixin


class Mailbox(LoggingMixin):

    def __init__(self) -> None:
        self.queue = queue.Queue()
        self.scheduling_job_id = None

    def send_message(self, message):
        if not self.scheduling_job_id:
            self.log.warning("scheduling_job_id not set, missing messages cannot be recovered.")
        message_obj = Message(message)
        identified_message = message_obj.save_queued_message(self.scheduling_job_id)
        self.queue.put(identified_message)

    def send_identified_message(self, message: IdentifiedMessage):
        self.queue.put(message)

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
