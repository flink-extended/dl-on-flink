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
import signal
import unittest
import time
import os
import shutil
from subprocess import Popen
from airflow.contrib.jobs.scheduler_client import EventSchedulerClient
from airflow.events.scheduler_events import StopSchedulerEvent
from airflow.utils.state import State
from notification_service.client import NotificationClient
from ai_flow.util.process_utils import get_all_children_pids
from ai_flow.endpoint.server.server_runner import AIFlowServerRunner
from ai_flow_plugins.scheduler_plugins.airflow.airflow_restful_util import AirFlowRestfulUtil
from ai_flow_plugins.tests import airflow_db_utils
from ai_flow_plugins.tests.airflow_scheduler_utils import start_airflow_scheduler_server, start_airflow_web_server


project_path = os.path.dirname(__file__)


class TestAirFlowRestfulUtil(unittest.TestCase):
    master = None
    web_process = None
    sc_process = None

    @classmethod
    def setUpClass(cls) -> None:
        airflow_db_utils.clear_all()
        config_file = project_path + '/master.yaml'
        cls.master = AIFlowServerRunner(config_file=config_file)
        cls.master.start()
        airflow_path = '/tmp/airflow_deploy'
        if os.path.exists(airflow_path):
            shutil.rmtree(airflow_path)
        os.makedirs(airflow_path)
        dag_dir = os.path.dirname(os.path.abspath(__file__))
        shutil.copyfile(dag_dir + '/dags/bash_1_dag.py', airflow_path + '/bash_1_dag.py')
        cls.sc_process = start_airflow_scheduler_server(file_path=airflow_path)
        cls.web_process: Popen = start_airflow_web_server()
        time.sleep(10)
        client = EventSchedulerClient(server_uri='localhost:50051', namespace='default')
        client.trigger_parse_dag('bash_1')
        for i in range(3):
            client.schedule_dag('bash_1', '')
            time.sleep(5)
        time.sleep(10)

    @classmethod
    def tearDownClass(cls) -> None:
        sub_pids = get_all_children_pids(cls.web_process.pid)
        try:
            for pid in sub_pids:
                os.kill(pid, signal.SIGKILL)
        except Exception:
            pass
        cls.web_process.kill()
        client = NotificationClient(server_uri="localhost:50051",
                                    default_namespace="default")
        client.send_event(StopSchedulerEvent(job_id=0).to_event())
        sub_pids = get_all_children_pids(cls.sc_process.pid)
        cls.sc_process.join()
        try:
            for pid in sub_pids:
                os.kill(pid, signal.SIGKILL)
        except Exception:
            pass
        cls.master.stop()

    def setUp(self):
        self.airflow_util = AirFlowRestfulUtil(endpoint_url='http://localhost:8080',
                                               user_name='admin',
                                               password='admin')

    def tearDown(self):
        self.master._clear_db()

    def test_list_dags(self):
        result = self.airflow_util.list_dags()
        self.assertEqual(1, len(result))

    def test_get_dag(self):
        result = self.airflow_util.get_dag('bash_1')
        self.assertTrue(result is not None)

    def test_pause_dag(self):
        result = self.airflow_util.set_dag_is_paused('bash_1', True)
        self.assertTrue(result.get('is_paused'))
        result = self.airflow_util.set_dag_is_paused('bash_1', False)
        self.assertFalse(result.get('is_paused'))

    def test_list_dagruns(self):
        result = self.airflow_util.list_dagruns('bash_1')
        self.assertEqual(3, len(result))

    def test_get_dagrun(self):
        result = self.airflow_util.list_dagruns('bash_1')
        result = self.airflow_util.get_dagrun(result[0].get('dag_id'), result[0].get('dag_run_id'))
        self.assertEqual(State.SUCCESS, result.get('state'))

    def test_list_taskInstances(self):
        result = self.airflow_util.list_dagruns('bash_1')
        result = self.airflow_util.list_task_instance(result[0].get('dag_id'), result[0].get('dag_run_id'))
        self.assertEqual(1, len(result))

    def test_get_taskInstances(self):
        result = self.airflow_util.list_dagruns('bash_1')
        result = self.airflow_util.get_task_instance(result[0].get('dag_id'),
                                                     result[0].get('dag_run_id'),
                                                     task_id='task_1')
        self.assertEqual(State.SUCCESS, result.get('state'))

    def test_list_taskExecutions(self):
        result = self.airflow_util.list_dagruns('bash_1')
        result = self.airflow_util.list_task_execution(result[0].get('dag_id'), result[0].get('dag_run_id'))
        self.assertEqual(1, len(result))

    def test_list_taskExecution_by_task_id(self):
        result = self.airflow_util.list_dagruns('bash_1')
        result = self.airflow_util.list_task_execution_by_task_id(result[0].get('dag_id'),
                                                                  result[0].get('dag_run_id'),
                                                                  'task_1')
        self.assertEqual(1, len(result))
