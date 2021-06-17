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

import sys
import time
import unittest
import os.path
from airflow.contrib.jobs.event_based_scheduler_job import EventBasedSchedulerJob
from airflow.events.scheduler_events import StopSchedulerEvent
from airflow.executors.local_executor import LocalExecutor
from notification_service.client import NotificationClient
from notification_service.event_storage import MemoryEventStorage
from notification_service.master import NotificationMaster
from notification_service.service import NotificationService

from ai_flow.common.scheduler_type import SchedulerType

import ai_flow as af
from ai_flow import AIFlowServerRunner
from ai_flow.executor.executor import CmdExecutor
from ai_flow.graph.graph import EmptyGraphException
from ai_flow.test import test_util


class TestAirflowProject(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.notification_server = NotificationMaster(NotificationService(MemoryEventStorage()), port=50052)
        cls.notification_server.run()
        config_file = test_util.get_master_config_file()
        cls.server_runner = AIFlowServerRunner(config_file=config_file)
        cls.server_runner.start()
        test_util.set_project_config(__file__)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server_runner.stop()
        cls.notification_server.stop()

    def setUp(self):
        TestAirflowProject.server_runner._clear_db()
        af.default_graph().clear_graph()

    def tearDown(self):
        TestAirflowProject.server_runner._clear_db()

    def run_airflow_dag_function(self):
        # waiting parsed dag file done
        from datetime import datetime
        ns_client = NotificationClient(server_uri='localhost:50052')
        with af.global_config_file(test_util.get_workflow_config_file()):
            with af.config('task_1'):
                cmd_executor = af.user_define_operation(output_num=0,
                                                        executor=CmdExecutor(
                                                            cmd_line=['echo "hello world!"']))
        af.deploy_to_airflow(test_util.get_project_path(),
                             dag_id='test_dag_111',
                             default_args={
                                 'schedule_interval': None,
                                 'start_date': datetime(2025, 12, 1),
                             })
        context = af.run(project_path=test_util.get_project_path(),
                         dag_id='test_dag_111',
                         scheduler_type=SchedulerType.AIRFLOW)
        print(context.dagrun_id)
        time.sleep(5)
        ns_client.send_event(StopSchedulerEvent(job_id=0).to_event())

    def test_submit_twice_in_row(self):
        with af.global_config_file(test_util.get_workflow_config_file()):
            with af.config('task_1'):
                cmd_executor = af.user_define_operation(output_num=0,
                                                        executor=CmdExecutor(
                                                            cmd_line=['echo "hello world!"']))
        self.assertFalse(af.default_graph().is_empty())
        af.submit(test_util.get_project_path(), dag_id='test_dag')
        self.assertTrue(af.default_graph().is_empty())
        expected_workflow_path = af.project_config().get_airflow_deploy_path() + '/test_dag.py'
        self.assertTrue(os.path.exists(expected_workflow_path))
        self.assertRaises(EmptyGraphException, af.submit, test_util.get_project_path(), dag_id='test_dag')

    def test_submit_empty_graph(self):
        self.assertRaises(EmptyGraphException, af.submit, test_util.get_project_path(), dag_id='test_dag')

    # def test_airflow_workflow(self):
    #     import multiprocessing
    #     p = multiprocessing.Process(target=self.run_airflow_dag_function, args=())
    #     p.start()
    #     scheduler = EventBasedSchedulerJob(
    #         dag_directory='/tmp/airflow',
    #         server_uri=af.project_config().get_notification_service_uri(),
    #         executor=LocalExecutor(3),
    #         max_runs=-1,
    #         refresh_dag_dir_interval=30
    #     )
    #     print("scheduler starting")
    #     scheduler.run()
