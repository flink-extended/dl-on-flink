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
import os
import shutil
import time
import unittest
from typing import List

from airflow.models.dagrun import DagRun
from airflow.models.taskexecution import TaskExecution
from airflow.models.taskinstance import TaskInstance
from airflow.utils.session import create_session
from airflow.utils.state import State
from notification_service.base_notification import BaseEvent
from notification_service.client import NotificationClient

import ai_flow as af
from ai_flow import AIFlowServerRunner, init_ai_flow_context
from ai_flow.workflow.control_edge import JobAction
from ai_flow.workflow.status import Status
from ai_flow_plugins.job_plugins import bash
from ai_flow_plugins.job_plugins import python
from ai_flow_plugins.job_plugins.python.python_processor import ExecutionContext
from ai_flow_plugins.tests import airflow_db_utils
from ai_flow_plugins.tests.airflow_scheduler_utils import run_ai_flow_workflow, get_dag_id

project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class TestPeriodicJob(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config_file = project_path + '/master.yaml'
        cls.master = AIFlowServerRunner(config_file=config_file)
        cls.master.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.master.stop()

    def setUp(self):
        airflow_db_utils.clear_all()
        self.master._clear_db()
        af.current_graph().clear_graph()
        init_ai_flow_context()

    def tearDown(self):
        self.master._clear_db()
        generated = '{}/generated'.format(project_path)
        if os.path.exists(generated):
            shutil.rmtree(generated)
        temp = '{}/temp'.format(project_path)
        if os.path.exists(temp):
            shutil.rmtree(temp)

    def run_periodic_job(self, task_name):
        def run_workflow(client: NotificationClient):
            with af.job_config(task_name):
                af.user_define_operation(processor=bash.BashProcessor(bash_command='echo "Xiao ming hello world!"'))

            workflow_info = af.workflow_operation.submit_workflow(
                workflow_name=af.current_workflow_config().workflow_name)
            workflow_execution = af.workflow_operation.start_new_workflow_execution(
                workflow_name=af.current_workflow_config().workflow_name)
            while True:
                with create_session() as session:
                    tes = session.query(TaskExecution)\
                        .filter(TaskExecution.dag_id == 'test_project.{}'
                                .format(af.current_workflow_config().workflow_name),
                                TaskExecution.task_id == task_name).all()
                    if len(tes) == 2:
                        break
                    else:
                        time.sleep(1)

        run_ai_flow_workflow(dag_id=get_dag_id(af.current_project_config().get_project_name(),
                                               af.current_workflow_config().workflow_name),
                             test_function=run_workflow)

    def test_periodic_cron_task(self):
        self.run_periodic_job('task_1')

    def test_periodic_interval_task(self):
        self.run_periodic_job('task_2')


if __name__ == '__main__':
    unittest.main()
