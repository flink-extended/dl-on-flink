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
import os
from typing import List

from ai_flow.model_center.entity.model_version_stage import ModelVersionEventType

from ai_flow.udf.function_context import FunctionContext
from python_ai_flow.user_define_funcs import Executor
from notification_service.client import NotificationClient
from notification_service.base_notification import BaseEvent
from airflow.models import DagRun
from airflow.utils.state import State
from airflow.models.taskexecution import TaskExecution
from airflow.utils.session import create_session
from base_ete_test import BaseETETest, workflow_config_file, master_port
import ai_flow as af
import flink_ai_flow as faf


class SimpleExecutor(Executor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("hello world!")
        return []


class SendExecutor(Executor):
    def __init__(self, sender, key, value, event_type, port):
        super().__init__()
        self.sender = sender
        self.key = key
        self.value = value
        self.event_type = event_type
        self.port = port

    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        from notification_service.client import NotificationClient
        client = NotificationClient(server_uri="localhost:{}".format(self.port),
                                    default_namespace="default", sender=self.sender)
        client.send_event(BaseEvent(key=self.key, value=self.value, event_type=self.event_type))
        return []


class TestRunAIFlowJobs(BaseETETest):

    def test_run_model_version_job(self):
        project_name = 'test_project'
        workflow_name = 'test_workflow'
        dag_id = '{}.{}'.format(project_name, workflow_name)
        train_model = af.register_model(model_name='model_1',
                                        model_type=af.ModelType.SAVED_MODEL,
                                        model_desc='test model')

        def run_task_function(client: NotificationClient):
            with af.global_config_file(workflow_config_file()):
                with af.config('task_2'):
                    executor_1 = af.user_define_operation(af.PythonObjectExecutor(SimpleExecutor()))
                with af.config('task_3'):
                    executor_2 = af.user_define_operation(af.PythonObjectExecutor(SimpleExecutor()))
                af.model_version_control_dependency(src=executor_2,
                                                    dependency=executor_1,
                                                    model_name='model_1',
                                                    model_version_event_type=ModelVersionEventType.MODEL_GENERATED)
                workflow_info = af.workflow_operation.submit_workflow(workflow_name)

            af.workflow_operation.start_new_workflow_execution(workflow_name)
            r_flag = True
            while True:
                with create_session() as session:
                    tes2 = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                               TaskExecution.task_id == 'task_2').all()
                    if len(tes2) == 1 and r_flag:
                        af.register_model_version(model='model_1', model_path='/tmp/model/v1',
                                                  current_stage=af.ModelVersionStage.GENERATED)
                        r_flag = False

                    dag_run = session.query(DagRun).filter(DagRun.dag_id == 'test_project.test_workflow').first()
                    if dag_run is not None and dag_run.state in State.finished:
                        break
                    else:
                        time.sleep(1)

        self.run_ai_flow(dag_id, run_task_function)
        with create_session() as session:
            tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                      TaskExecution.task_id == 'task_2').all()
            self.assertEqual(1, len(tes))

    def test_two_jobs(self):
        project_name = 'test_project'
        workflow_name = 'test_workflow'
        dag_id = '{}.{}'.format(project_name, workflow_name)

        def run_task_function(client: NotificationClient):
            with af.global_config_file(workflow_config_file()):
                with af.config('task_2'):
                    executor_1 = af.user_define_operation(af.PythonObjectExecutor(
                        SendExecutor(sender='task_2',
                                     key='key_1',
                                     value='value_1',
                                     event_type='UNDEFINED',
                                     port=master_port())
                    ))
                with af.config('task_5'):
                    executor_2 = af.user_define_operation(af.PythonObjectExecutor(SimpleExecutor()))
                af.user_define_control_dependency(src=executor_2,
                                                  dependency=executor_1,
                                                  event_key='key_1',
                                                  event_value='value_1')
                workflow_info = af.workflow_operation.submit_workflow(workflow_name)

            af.workflow_operation.start_new_workflow_execution(workflow_name)
            while True:
                with create_session() as session:

                    dag_run = session.query(DagRun).filter(DagRun.dag_id == 'test_project.test_workflow').first()
                    if dag_run is not None and dag_run.state in State.finished:
                        break
                    else:
                        time.sleep(1)

        self.run_ai_flow(dag_id, run_task_function)
        with create_session() as session:
            tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                      TaskExecution.task_id == 'task_2').all()
            self.assertEqual(1, len(tes))

            tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                      TaskExecution.task_id == 'task_5').all()
            self.assertEqual(1, len(tes))

    def test_two_jobs_2(self):
        project_name = 'test_project'
        workflow_name = 'test_workflow'
        dag_id = '{}.{}'.format(project_name, workflow_name)

        def run_task_function(client: NotificationClient):
            with af.global_config_file(workflow_config_file()):
                with af.config('task_2'):
                    executor_1 = af.user_define_operation(af.PythonObjectExecutor(SimpleExecutor()))
                with af.config('task_5'):
                    executor_2 = af.user_define_operation(af.PythonObjectExecutor(SimpleExecutor()))
                af.user_define_control_dependency(src=executor_2,
                                                  dependency=executor_1,
                                                  namespace='test',
                                                  event_key='key_1',
                                                  event_value='value_1',
                                                  sender='*')
                workflow_info = af.workflow_operation.submit_workflow(workflow_name)

            af.workflow_operation.start_new_workflow_execution(workflow_name)
            flag = True
            while True:
                with create_session() as session:
                    tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                              TaskExecution.task_id == 'task_2').all()
                    if 1 == len(tes) and flag:
                        client.send_event(BaseEvent(key='key_1', value='value_1'))
                        flag = False
                    dag_run = session.query(DagRun).filter(DagRun.dag_id == 'test_project.test_workflow').first()
                    if dag_run is not None and dag_run.state in State.finished:
                        break
                    else:
                        time.sleep(1)

        self.run_ai_flow(dag_id, run_task_function)
        with create_session() as session:
            tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                      TaskExecution.task_id == 'task_2').all()
            self.assertEqual(1, len(tes))

            tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                      TaskExecution.task_id == 'task_5').all()
            self.assertEqual(1, len(tes))

    def test_three_jobs(self):
        project_name = 'test_project'
        workflow_name = 'test_workflow'
        dag_id = '{}.{}'.format(project_name, workflow_name)

        def run_task_function(client: NotificationClient):
            with af.global_config_file(workflow_config_file()):
                with af.config('task_2'):
                    executor_1 = af.user_define_operation(af.PythonObjectExecutor(
                        SendExecutor(sender='task_2',
                                     key='key_1',
                                     value='value_1',
                                     event_type='UNDEFINED',
                                     port=master_port())
                    ))
                with af.config('task_5'):
                    executor_2 = af.user_define_operation(af.PythonObjectExecutor(
                        SendExecutor(sender='task_5555',
                                     key='key_2',
                                     value='value_2',
                                     event_type='UNDEFINED',
                                     port=master_port())
                    ))

                with af.config('task_6'):
                    executor_3 = af.user_define_operation(af.PythonObjectExecutor(SimpleExecutor()))

                af.user_define_control_dependency(src=executor_3,
                                                  dependency=executor_1,
                                                  event_key='key_1',
                                                  event_value='value_1')
                af.user_define_control_dependency(src=executor_3,
                                                  dependency=executor_2,
                                                  event_key='key_2',
                                                  event_value='value_2',
                                                  sender='*')

                workflow_info = af.workflow_operation.submit_workflow(workflow_name)

            af.workflow_operation.start_new_workflow_execution(workflow_name)
            while True:
                with create_session() as session:

                    dag_run = session.query(DagRun).filter(DagRun.dag_id == 'test_project.test_workflow').first()
                    if dag_run is not None and dag_run.state in State.finished:
                        break
                    else:
                        time.sleep(1)

        self.run_ai_flow(dag_id, run_task_function)
        with create_session() as session:
            tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                      TaskExecution.task_id == 'task_2').all()
            self.assertEqual(1, len(tes))

            tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                      TaskExecution.task_id == 'task_5').all()
            self.assertEqual(1, len(tes))

            tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                      TaskExecution.task_id == 'task_6').all()
            self.assertEqual(1, len(tes))
