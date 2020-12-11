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

from airflow.jobs.event_scheduler_job import EventSchedulerJob
from airflow.models.taskexecution import TaskExecution
from tests.test_utils.db import clear_db_event_model, clear_db_dags, clear_db_dag_pickle, \
    clear_db_task_instance, clear_db_runs
import unittest
import os
from tests.test_utils import db

TEST_DAG_FOLDER = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, 'dags')


class EventSchedulerJobTest(unittest.TestCase):
    def setUp(self):
        clear_db_event_model()
        clear_db_dag_pickle()
        clear_db_dags()
        clear_db_task_instance()
        clear_db_runs()

    def test_event_scheduler_run(self):
        sc = EventSchedulerJob(subdir=TEST_DAG_FOLDER + "/test_event_scheduler_dags.py")
        sc.run()
        with db.create_session() as session:
            res = session.query(TaskExecution).filter(TaskExecution.task_id == "dummy_4").all()
        self.assertEqual(1, len(res))

    def test_stream_scheduler_run(self):
        sc = EventSchedulerJob(subdir=TEST_DAG_FOLDER + "/test_stream_scheduler_dags.py")
        sc.run()
        with db.create_session() as session:
            res = session.query(TaskExecution).filter(TaskExecution.task_id == "dummy_2").all()
        self.assertEqual(2, len(res))

    def test_stop_job_scheduler_run(self):
        sc = EventSchedulerJob(subdir=TEST_DAG_FOLDER + "/test_stop_job_dag.py")
        sc.run()

    def test_restart_job_scheduler_run(self):
        sc = EventSchedulerJob(subdir=TEST_DAG_FOLDER + "/test_restart_job_dag.py")
        sc.run()

    def test_ai_flow_run(self):
        sc = EventSchedulerJob(subdir=TEST_DAG_FOLDER + "/test_dummy_dag.py")
        sc.run()

    def test_ai_flow_bash_run(self):
        sc = EventSchedulerJob(subdir=TEST_DAG_FOLDER + "/test_aiflow_bash_dag.py")
        sc.run()

    def test_ai_flow_python_run(self):
        sc = EventSchedulerJob(subdir=TEST_DAG_FOLDER + "/test_aiflow_python_dag.py")
        sc.run()

    def test_ai_flow_flink_2_run(self):
        sc = EventSchedulerJob(subdir='/tmp/test_airflow/')
        sc.run()

    def test_ai_flow_k8s_cmd(self):
        sc = EventSchedulerJob(subdir=TEST_DAG_FOLDER + "/test_aiflow_k8s_cmd_dag.py")
        sc.run()
