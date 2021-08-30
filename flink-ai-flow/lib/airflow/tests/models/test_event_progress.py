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
import unittest

from airflow.models.event_progress import create_or_update_progress, get_event_progress
from tests.test_utils import db


class TestEventProgress(unittest.TestCase):

    def tearDown(self) -> None:
        db.clear_db_event_progress()

    def test_create_or_update_progress(self):
        create_or_update_progress(scheduling_job_id=1, last_event_time=2, last_event_version=3)
        progress = get_event_progress(1)
        self.assertEqual(2, progress.last_event_time)
        self.assertEqual(3, progress.last_event_version)

        create_or_update_progress(scheduling_job_id=1, last_event_time=4, last_event_version=None)
        progress = get_event_progress(1)
        self.assertEqual(4, progress.last_event_time)
        self.assertEqual(None, progress.last_event_version)



