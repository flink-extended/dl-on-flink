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
from airflow.utils.state import State
from notification_service.client import NotificationClient
from ai_flow import AIFlowServerRunner, init_ai_flow_context
from ai_flow.workflow.status import Status
from ai_flow_plugins.job_plugins import bash
from ai_flow_plugins.tests.airflow_scheduler_utils import run_ai_flow_workflow, get_dag_id, \
    get_workflow_execution_info, set_workflow_execution_info
from ai_flow_plugins.tests import airflow_db_utils
import ai_flow as af

project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class TestBash(unittest.TestCase):
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

    def test_bash_task(self):
        def run_workflow(client: NotificationClient):
            with af.job_config('task_1'):
                af.user_define_operation(processor=bash.BashProcessor(bash_command='echo "Xiao ming hello world!"'))
            workflow_info = af.workflow_operation.submit_workflow(
                workflow_name=af.current_workflow_config().workflow_name)
            wei = af.workflow_operation.start_new_workflow_execution(
                workflow_name=af.current_workflow_config().workflow_name)
            set_workflow_execution_info(wei)
            while True:
                with create_session() as session:
                    dag_run = session.query(DagRun)\
                        .filter(DagRun.dag_id == 'test_project.{}'
                                .format(af.current_workflow_config().workflow_name)).first()
                    if dag_run is not None and dag_run.state == State.SUCCESS:
                        break
                    else:
                        time.sleep(1)

        run_ai_flow_workflow(dag_id=get_dag_id(af.current_project_config().get_project_name(),
                                               af.current_workflow_config().workflow_name),
                             test_function=run_workflow)
        workflow_execution_info = af.workflow_operation.get_workflow_execution(
            execution_id=get_workflow_execution_info().workflow_execution_id)
        self.assertEqual(Status.FINISHED, workflow_execution_info.status)

        job_execution_info = af.workflow_operation.get_job_execution(job_name='task_1',
                                                                     execution_id=get_workflow_execution_info().
                                                                     workflow_execution_id)
        self.assertEqual(Status.FINISHED, job_execution_info.status)


if __name__ == '__main__':
    unittest.main()
