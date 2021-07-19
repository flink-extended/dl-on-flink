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


class PyProcessor3(python.PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        af.get_ai_flow_client().send_event(BaseEvent(key='k_1', value='v_1'))
        return []


class PyProcessor4(python.PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        af.get_ai_flow_client().send_event(BaseEvent(key='k_2', value='v_2'))
        return []


class PyProcessor5(python.PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        print('hello world!')
        return []


class TestActionOnEvent(unittest.TestCase):
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

    def test_action_on_status_finished(self):
        def run_workflow(client: NotificationClient):
            with af.job_config('task_1'):
                af.user_define_operation(processor=bash.BashProcessor(bash_command='echo "Xiao ming hello world!"'))
            with af.job_config('task_2'):
                af.user_define_operation(processor=bash.BashProcessor(bash_command='echo "Xiao li hello world!"'))
            af.action_on_job_status('task_2', 'task_1', Status.FINISHED, JobAction.START)
            workflow_info = af.workflow_operation.submit_workflow(
                workflow_name=af.current_workflow_config().workflow_name)
            workflow_execution = af.workflow_operation.start_new_workflow_execution(
                workflow_name=af.current_workflow_config().workflow_name)
            while True:
                with create_session() as session:
                    ti = session.query(TaskInstance)\
                        .filter(TaskInstance.dag_id ==
                                'test_project.{}'.format(af.current_workflow_config().workflow_name),
                                TaskInstance.task_id == 'task_2')\
                        .first()
                    if ti is not None and ti.state == State.SUCCESS:
                        break
                    else:
                        time.sleep(1)

        run_ai_flow_workflow(dag_id=get_dag_id(af.current_project_config().get_project_name(),
                                               af.current_workflow_config().workflow_name),
                             test_function=run_workflow)

    def test_action_on_event(self):
        def run_workflow(client: NotificationClient):
            with af.job_config('task_3'):
                af.user_define_operation(processor=PyProcessor3())
            with af.job_config('task_4'):
                af.user_define_operation(processor=PyProcessor4())
            with af.job_config('task_5'):
                af.user_define_operation(processor=PyProcessor5())
            event_condition = af.MeetAllEventCondition()
            event_condition.add_event(event_key='k_1', event_value='v_1', namespace='*', sender='*')
            event_condition.add_event(event_key='k_2', event_value='v_2', namespace='*', sender='*')
            af.action_on_events(job_name='task_5', event_condition=event_condition, action=af.JobAction.START)

            workflow_info = af.workflow_operation.submit_workflow(
                workflow_name=af.current_workflow_config().workflow_name)
            workflow_execution = af.workflow_operation.start_new_workflow_execution(
                workflow_name=af.current_workflow_config().workflow_name)
            while True:
                with create_session() as session:
                    dag_run = session.query(DagRun)\
                        .filter(DagRun.dag_id == 'test_project.{}'.format(af.current_workflow_config().workflow_name))\
                        .first()
                    if dag_run is not None:
                        ti = session.query(TaskInstance).filter(TaskInstance.task_id == 'task_5').first()
                        if ti.state == State.SUCCESS:
                            break
                    else:
                        time.sleep(1)

        run_ai_flow_workflow(dag_id=get_dag_id(af.current_project_config().get_project_name(),
                                               af.current_workflow_config().workflow_name),
                             test_function=run_workflow)


if __name__ == '__main__':
    unittest.main()
