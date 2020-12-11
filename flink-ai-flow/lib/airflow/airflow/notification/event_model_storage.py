# -*- coding: utf-8 -*-
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

from notification_service.event_storage import BaseEventStorage
from airflow.models import EventModel
from airflow.models.event import Event


class EventModelStorage(BaseEventStorage):
    def add_event(self, event: Event):
        return EventModel.add_event(event)

    def list_events(self, key: str, version: int):
        return EventModel.list_events(key, version)

    def list_all_events(self, start_time: int):
        return EventModel.list_all_events(start_time)

    def list_all_events_from_id(self, id: int):
        return EventModel.list_all_events_from_id(id)
