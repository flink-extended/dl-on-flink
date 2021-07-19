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
import time
import unittest
import os
import shutil

from airflow.models.dagrun import DagRun
from airflow.utils.session import create_session
from notification_service.client import NotificationClient
from ai_flow import AIFlowServerRunner, init_ai_flow_context
from ai_flow_plugins.job_plugins import bash
from ai_flow_plugins.tests.airflow_scheduler_utils import run_ai_flow_workflow, get_dag_id
from ai_flow_plugins.tests import airflow_db_utils

import ai_flow as af

project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class TestPeriodicWorkflow(unittest.TestCase):
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

    def tearDown(self):
        self.master._clear_db()
        generated = '{}/generated'.format(project_path)
        if os.path.exists(generated):
            shutil.rmtree(generated)
        temp = '{}/temp'.format(project_path)
        if os.path.exists(temp):
            shutil.rmtree(temp)

    def generate_workflow_config_file(self, pc):
        text = """
periodic_config:
  {}
task_1:
  job_type: bash""".format(pc)
        self.file_path = os.path.join(os.path.dirname(__file__), 'test_periodic_workflow.yaml')
        with open(file=self.file_path, mode='w') as f:
            f.write(text)

    def run_periodic_workflow(self, config):
        self.generate_workflow_config_file(config)
        init_ai_flow_context()

        def run_workflow(client: NotificationClient):
            with af.job_config('task_1'):
                af.user_define_operation(processor=bash.BashProcessor(bash_command='echo "Xiao ming hello world!"'))

            workflow_info = af.workflow_operation.submit_workflow(
                workflow_name=af.current_workflow_config().workflow_name)
            while True:
                with create_session() as session:
                    dagruns = session.query(DagRun)\
                        .filter(DagRun.dag_id == 'test_project.{}'
                                .format(af.current_workflow_config().workflow_name)).all()
                    if len(dagruns) >= 2:
                        break
                    else:
                        time.sleep(1)
                    session.expunge_all()

        run_ai_flow_workflow(dag_id=get_dag_id(af.current_project_config().get_project_name(),
                                               af.current_workflow_config().workflow_name),
                             test_function=run_workflow)
        if self.file_path is not None and os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_periodic_cron_workflow(self):
        self.run_periodic_workflow("cron: '*/10 * * * * * *'")

    def test_periodic_interval_workflow(self):
        self.run_periodic_workflow("interval: '0,0,0,10'")


if __name__ == '__main__':
    unittest.main()
