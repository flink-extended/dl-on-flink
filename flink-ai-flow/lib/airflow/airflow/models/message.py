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
import pickle
import dill
from sqlalchemy import Column, Index, Integer, String, PickleType
from airflow.models.base import ID_LEN, Base
from airflow.utils import timezone
from airflow.utils.session import provide_session
from airflow.utils.sqlalchemy import UtcDateTime


class MessageState:
    QUEUED = "queued"
    COMPLETED = "complete"


class IdentifiedMessage(object):
    def __init__(self, serialized_message, msg_id, queue_time):
        self.serialized_message = serialized_message
        self.msg_id = msg_id
        self.queue_time = queue_time

    def deserialize(self):
        return pickle.loads(self.serialized_message)

    @provide_session
    def remove_handled_message(self, session):
        # TODO this function could be asynchronous
        session.query(Message).filter(Message.id == self.msg_id).delete(synchronize_session=False)
        session.commit()


class Message(Base):
    """the class to save all messages that scheduler handles."""

    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    message_type = Column(String(ID_LEN), nullable=False)
    data = Column(PickleType(pickler=dill))
    state = Column(String(ID_LEN), nullable=False)
    scheduling_job_id = Column(Integer, nullable=True)
    queue_time = Column(UtcDateTime, default=timezone.utcnow)
    complete_time = Column(UtcDateTime, nullable=True)

    __table_args__ = (
        Index('ti_queue_time', queue_time),
        Index('ti_state', state)
    )

    def __init__(self, obj):
        self.message_type = self.get_message_type(obj)
        self.data = pickle.dumps(obj)

    @property
    def serialized_data(self):
        return self.data

    @staticmethod
    def get_message_type(obj):
        return type(obj).__name__
