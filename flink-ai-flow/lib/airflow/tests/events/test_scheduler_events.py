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

import unittest
from notification_service.base_notification import BaseEvent
from airflow.executors.scheduling_action import SchedulingAction

from airflow.utils import timezone
from airflow.events.scheduler_events import SchedulerInnerEventType, TaskStateChangedEvent, TaskSchedulingEvent, \
    SchedulerInnerEventUtil, StopSchedulerEvent


class TestSchedulerEvents(unittest.TestCase):

    def test_event_type(self):
        event_type = SchedulerInnerEventType.STOP_SCHEDULER
        self.assertEqual('STOP_SCHEDULER', event_type.value)

    def test_to_event(self):
        e_date = timezone.utcnow()
        task_changed_event = TaskStateChangedEvent(task_id='a', dag_id='b',
                                                   execution_date=e_date, state='running', try_number=1)
        event = task_changed_event.to_event()
        self.assertEqual('b', event.key)

    def test_task_status_changed(self):
        e_date = timezone.utcnow()
        task_changed_event = TaskStateChangedEvent(task_id='a', dag_id='b',
                                                   execution_date=e_date, state='running', try_number=1)
        event = TaskStateChangedEvent.to_base_event(task_changed_event)
        task_changed_event_2 = TaskStateChangedEvent.from_base_event(event)
        self.assertEqual(e_date, task_changed_event_2.execution_date)

    def test_scheduling_task(self):
        e_date = timezone.utcnow()
        scheduling_task = TaskSchedulingEvent(task_id='a',
                                              dag_id='b',
                                              execution_date=e_date,
                                              try_number=1,
                                              action=SchedulingAction.START)
        event = TaskSchedulingEvent.to_base_event(scheduling_task)
        scheduling_task_2 = TaskSchedulingEvent.from_base_event(event)
        self.assertEqual(e_date, scheduling_task_2.execution_date)
        self.assertEqual(SchedulingAction.START, scheduling_task_2.action)

    def test_inner_event(self):
        self.assertTrue(SchedulerInnerEventUtil.is_inner_event(BaseEvent('', '', 'STOP_SCHEDULER')))
        self.assertFalse(SchedulerInnerEventUtil.is_inner_event(BaseEvent('', '', 'TEST')))
        self.assertEqual(SchedulerInnerEventUtil.event_type(BaseEvent('', '', 'STOP_SCHEDULER')),
                         SchedulerInnerEventType.STOP_SCHEDULER)
        event = SchedulerInnerEventUtil.to_inner_event(BaseEvent('1', '', 'STOP_SCHEDULER'))
        self.assertTrue(isinstance(event, StopSchedulerEvent))
