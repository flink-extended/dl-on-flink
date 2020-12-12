# -*- coding: utf-8 -*-
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
import time

from airflow.utils.mailbox import Mailbox

from airflow.jobs.event_scheduler_job import DagTrigger
import os
from tests.test_utils.db import (
    clear_db_dags, clear_db_errors, clear_db_pools, clear_db_runs, clear_db_sla_miss, clear_db_event_model
)

TEST_DAG_FOLDER = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, 'dags')


class DagTriggerTest(unittest.TestCase):

    def setUp(self):
        clear_db_runs()
        clear_db_pools()
        clear_db_dags()
        clear_db_sla_miss()
        clear_db_errors()
        clear_db_event_model()

    def test_proccess_dag_file(self):
        mailbox = Mailbox()
        test_dag_path = os.path.join(TEST_DAG_FOLDER, 'test_event_scheduler_dags.py')
        dag_trigger = DagTrigger(subdir=test_dag_path, mailbox=mailbox,  using_sqlite=True, num_runs=-1)
        dag_trigger.start()
        time.sleep(5)
        self.assertEqual(1, mailbox.length())
        dag_trigger.stop()

