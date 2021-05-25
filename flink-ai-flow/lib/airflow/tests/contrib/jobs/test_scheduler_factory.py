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

from airflow.configuration import conf
from airflow.contrib.jobs.event_based_scheduler_job import EventBasedSchedulerJob
from airflow.contrib.jobs.scheduler_factory import SchedulerFactory
from airflow.jobs.scheduler_job import SchedulerJob


class TestSchedulerFactory(unittest.TestCase):
    def test_get_default_scheduler(self):
        conf.set('core', 'scheduler', SchedulerFactory.DEFAULT_SCHEDULER)
        scheduler_class = SchedulerFactory.get_default_scheduler()
        self.assertEqual(scheduler_class, SchedulerJob)

        conf.set('core', 'scheduler', SchedulerFactory.EVENT_BASED_SCHEDULER)
        scheduler_class = SchedulerFactory.get_default_scheduler()
        self.assertEqual(scheduler_class, EventBasedSchedulerJob)
