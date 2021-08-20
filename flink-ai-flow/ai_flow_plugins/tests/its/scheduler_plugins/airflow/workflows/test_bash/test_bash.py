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
import time
import unittest
import os
import shutil
from subprocess import Popen

from airflow.models.dagrun import DagRun
from airflow.models.taskinstance import TaskInstance
from airflow.utils.session import create_session
from airflow.utils.state import State
from notification_service.client import NotificationClient
from notification_service.base_notification import BaseEvent
from ai_flow import AIFlowServerRunner, init_ai_flow_context
from ai_flow.util.process_utils import get_all_children_pids
from ai_flow.workflow.status import Status
from ai_flow_plugins.job_plugins import bash
from ai_flow_plugins.tests.airflow_scheduler_utils import run_ai_flow_workflow, get_dag_id, \
    get_workflow_execution_info, set_workflow_execution_info, start_airflow_web_server
from ai_flow_plugins.tests import airflow_db_utils
import ai_flow as af

project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def run_batch_workflow(client: NotificationClient):
    with af.job_config('task_1'):
        af.user_define_operation(processor=bash.BashProcessor(bash_command='echo "Xiao ming hello world!"'))
    workflow_info = af.workflow_operation.submit_workflow(
        workflow_name=af.current_workflow_config().workflow_name)
    wei = af.workflow_operation.start_new_workflow_execution(
        workflow_name=af.current_workflow_config().workflow_name)
    set_workflow_execution_info(wei)
    while True:
        with create_session() as session:
            dag_run = session.query(DagRun) \
                .filter(DagRun.dag_id == 'test_project.{}'
                        .format(af.current_workflow_config().workflow_name)).first()
            if dag_run is not None and dag_run.state == State.SUCCESS:
                break
            else:
                time.sleep(1)


def run_event_workflow(client: NotificationClient):
    with af.job_config('task_1'):
        af.user_define_operation(processor=bash.BashProcessor(bash_command='echo "Xiao ming hello world!"'))
    af.action_on_event(job_name='task_1',
                       event_key='test_key',
                       event_type='test_type',
                       event_value='test_value',
                       sender='*',
                       namespace='*',
                       action=af.JobAction.RESTART)
    workflow_info = af.workflow_operation.submit_workflow(
        workflow_name=af.current_workflow_config().workflow_name)
    wei = af.workflow_operation.start_new_workflow_execution(
        workflow_name=af.current_workflow_config().workflow_name)
    set_workflow_execution_info(wei)
    result = af.workflow_operation.start_job_execution(
        job_name='task_1',
        execution_id=get_workflow_execution_info().workflow_execution_id)

    while True:
        with create_session() as session:
            task_instance = session.query(TaskInstance) \
                .filter(TaskInstance.dag_id == 'test_project.{}'
                        .format(af.current_workflow_config().workflow_name),
                        TaskInstance.task_id == 'task_1'
                        ).first()
            if task_instance is not None and task_instance.state == State.SUCCESS:
                break
            else:
                time.sleep(1)

    af.workflow_operation.stop_workflow_execution(wei.workflow_execution_id)

    while True:
        with create_session() as session:

            dag_run = session.query(DagRun) \
                .filter(DagRun.dag_id == 'test_project.{}'
                        .format(af.current_workflow_config().workflow_name),
                        ).first()
            if dag_run is not None and dag_run.state == State.KILLED:
                break
            else:
                time.sleep(1)


class TestBash(unittest.TestCase):
    master = None
    web_process = None

    @classmethod
    def setUpClass(cls) -> None:
        airflow_path = '/tmp/airflow_deploy'
        if os.path.exists(airflow_path):
            shutil.rmtree(airflow_path)
        os.makedirs(airflow_path)

        config_file = project_path + '/master.yaml'
        cls.master = AIFlowServerRunner(config_file=config_file)
        cls.master.start()

        cls.web_process: Popen = start_airflow_web_server()

    @classmethod
    def tearDownClass(cls) -> None:
        sub_pids = get_all_children_pids(cls.web_process.pid)
        print(sub_pids)
        for pid in sub_pids:
            os.kill(pid, signal.SIGKILL)
        cls.web_process.kill()
        time.sleep(5)
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

    def test_workflow_apis(self):
        run_ai_flow_workflow(dag_id=get_dag_id(af.current_project_config().get_project_name(),
                                               af.current_workflow_config().workflow_name),
                             test_function=run_batch_workflow)

        result = af.workflow_operation.list_workflows(offset=0, page_size=5)
        self.assertEqual(1, len(result))

        result = af.workflow_operation.get_workflow(workflow_name='test_bash')
        self.assertTrue(result is not None)

        result = af.workflow_operation.list_workflow_executions(workflow_name='test_bash')
        self.assertEqual(1, len(result))

        result = af.workflow_operation.get_workflow_execution(
            execution_id=get_workflow_execution_info().workflow_execution_id)
        self.assertTrue(result is not None)
        self.assertEqual(Status.FINISHED, result.status)

        job_execution_info = af.workflow_operation.get_job_execution(job_name='task_1',
                                                                     execution_id=get_workflow_execution_info().
                                                                     workflow_execution_id)
        self.assertEqual(Status.FINISHED, job_execution_info.status)

    def test_event_workflow_apis(self):
        run_ai_flow_workflow(dag_id=get_dag_id(af.current_project_config().get_project_name(),
                                               af.current_workflow_config().workflow_name),
                             test_function=run_event_workflow)

        result = af.workflow_operation.get_workflow_execution(
            execution_id=get_workflow_execution_info().workflow_execution_id)
        self.assertTrue(result is not None)
        self.assertEqual(Status.KILLED, result.status)


if __name__ == '__main__':
    unittest.main()
