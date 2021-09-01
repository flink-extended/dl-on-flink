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
import datetime
import time
import unittest

from airflow.utils import timezone
from notification_service.base_notification import BaseEvent

from airflow.models.event_progress import get_event_progress
from airflow.utils.mailbox import Mailbox
from airflow.events.scheduler_events import StopDagEvent, SchedulerInnerEventUtil
from tests.test_utils import db


class TestMailbox(unittest.TestCase):

    def tearDown(self) -> None:
        db.clear_db_event_progress()

    def test_send_inner_event(self):
        mailbox = Mailbox()
        mailbox.scheduling_job_id = 1
        mailbox.send_message(StopDagEvent.to_base_event(StopDagEvent('q')))
        message = mailbox.get_identified_message()
        event = message.deserialize()
        result = SchedulerInnerEventUtil.is_inner_event(event)
        self.assertEqual(True, result)
        progress = get_event_progress(1)
        self.assertIsNone(progress)

    def test_send_event(self):
        mailbox = Mailbox()
        mailbox.scheduling_job_id = 1
        event = BaseEvent(key='1', value='1', version=1, create_time=2)
        mailbox.send_message(event)
        message = mailbox.get_identified_message()
        event = message.deserialize()
        result = SchedulerInnerEventUtil.is_inner_event(event)
        self.assertEqual(False, result)
        progress = get_event_progress(1)
        self.assertEqual(2, progress.last_event_time)
        self.assertEqual(1, progress.last_event_version)

        event = BaseEvent(key='1', value='1', version=2, create_time=3)
        mailbox.send_message(event)
        progress = get_event_progress(1)
        self.assertEqual(3, progress.last_event_time)
        self.assertEqual(2, progress.last_event_version)

    def test_send_delay_event(self):
        mailbox = Mailbox()
        mailbox.start()
        mailbox.scheduling_job_id = 1
        event = BaseEvent(key='1', value='1', version=1, create_time=2)
        mailbox.send_message(event, timezone.utcnow()+datetime.timedelta(seconds=2))
        message = mailbox.get_identified_message()
        self.assertIsNone(message)
        time.sleep(5)
        message = mailbox.get_identified_message()
        event = message.deserialize()
        result = SchedulerInnerEventUtil.is_inner_event(event)
        self.assertEqual(False, result)
        progress = get_event_progress(1)
        self.assertEqual(2, progress.last_event_time)
        self.assertEqual(1, progress.last_event_version)
        mailbox.stop()


if __name__ == '__main__':
    unittest.main()
