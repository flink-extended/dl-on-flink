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
from sqlalchemy import Column, Index, Integer, BigInteger
from sqlalchemy.orm import Session

from airflow.models.base import Base
from airflow.utils.session import provide_session


class EventProgress(Base):
    """the class to save the progress of the event."""

    __tablename__ = "event_progress"

    scheduling_job_id = Column(Integer, primary_key=True)
    last_event_time = Column(BigInteger, nullable=True)
    last_event_version = Column(BigInteger, nullable=True)

    def __init__(self, scheduling_job_id, last_event_time=None, last_event_version=None):
        self.scheduling_job_id = scheduling_job_id
        self.last_event_time = last_event_time
        self.last_event_version = last_event_version

    @provide_session
    def update_progress(self, scheduling_job_id: int,
                        last_event_time: int,
                        last_event_version: int,
                        session: Session = None):
        self.scheduling_job_id = scheduling_job_id
        self.last_event_time = last_event_time
        self.last_event_version = last_event_version
        session.merge(self)
        session.commit()


@provide_session
def create_or_update_progress(scheduling_job_id: int,
                              last_event_time: int,
                              last_event_version: int,
                              session: Session = None):
    progress = EventProgress(scheduling_job_id, last_event_time, last_event_version)
    session.merge(progress)
    session.commit()


@provide_session
def get_event_progress(scheduling_job_id: int,
                       session: Session = None):
    return session.query(EventProgress).filter(EventProgress.scheduling_job_id == scheduling_job_id).first()
