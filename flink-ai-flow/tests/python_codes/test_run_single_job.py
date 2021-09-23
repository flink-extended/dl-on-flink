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

from ai_flow.udf.function_context import FunctionContext
from python_ai_flow.user_define_funcs import Executor
from notification_service.client import NotificationClient
from ai_flow.executor.executor import CmdExecutor

from airflow.models import DagRun
from airflow.utils.state import State
from airflow.models.taskexecution import TaskExecution
from airflow.utils.session import create_session
from base_ete_test import BaseETETest, workflow_config_file, project_path
import ai_flow as af
import flink_ai_flow as faf
from test_executors import HelloExecutor, Source, Sink, Transformer


class SimpleExecutor(Executor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("hello world!")
        return []


class TestRunAIFlowJobs(BaseETETest):

    def test_run_cmd_job(self):
        def build_and_submit_ai_flow():
            with af.global_config_file(workflow_config_file()):
                with af.config('task_1'):
                    cmd_executor = af.user_define_operation(output_num=0,
                                                            executor=CmdExecutor(
                                                                cmd_line='echo "hello world"'.format(1)))
                workflow_info = af.workflow_operation.submit_workflow('test_workflow')
            return workflow_info.workflow_name

        def run_task_function(client: NotificationClient):
            af.workflow_operation.start_new_workflow_execution('test_workflow')
            while True:
                with create_session() as session:
                    dag_run = session.query(DagRun).filter(DagRun.dag_id == 'test_project.test_workflow').first()
                    if dag_run is not None and dag_run.state == State.SUCCESS:
                        break
                    else:
                        time.sleep(1)

        self.run_ai_flow(build_and_submit_ai_flow, run_task_function)
        with create_session() as session:
            tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                      TaskExecution.task_id == 'task_1').all()
            self.assertEqual(1, len(tes))

    def test_run_python_job(self):

        def build_and_submit_ai_flow():
            with af.global_config_file(workflow_config_file()):
                with af.config('task_2'):
                    executor = af.user_define_operation(af.PythonObjectExecutor(SimpleExecutor()))
                workflow_info = af.workflow_operation.submit_workflow('test_workflow')
            return workflow_info.workflow_name

        def run_task_function(client: NotificationClient):
            af.workflow_operation.start_new_workflow_execution('test_workflow')
            while True:
                with create_session() as session:
                    dag_run = session.query(DagRun).filter(DagRun.dag_id == 'test_project.test_workflow').first()
                    if dag_run is not None and dag_run.state in State.finished:
                        break
                    else:
                        time.sleep(1)

        self.run_ai_flow(build_and_submit_ai_flow, run_task_function)
        with create_session() as session:
            tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                      TaskExecution.task_id == 'task_2').all()
            self.assertEqual(1, len(tes))

    def test_run_python_job_2(self):

        def build_and_submit_ai_flow():
            with af.global_config_file(workflow_config_file()):
                with af.config('task_2'):
                    executor = af.user_define_operation(af.PythonObjectExecutor(HelloExecutor()))
                workflow_info = af.workflow_operation.submit_workflow('test_workflow')
            return workflow_info.workflow_name

        def run_task_function(client: NotificationClient):
            af.workflow_operation.start_new_workflow_execution('test_workflow')
            while True:
                with create_session() as session:
                    dag_run = session.query(DagRun).filter(DagRun.dag_id == 'test_project.test_workflow').first()
                    if dag_run is not None and dag_run.state in State.finished:
                        break
                    else:
                        time.sleep(1)

        self.run_ai_flow(build_and_submit_ai_flow, run_task_function)
        with create_session() as session:
            tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                      TaskExecution.task_id == 'task_2').all()
            self.assertEqual(1, len(tes))

    def test_run_local_flink_job(self):
        input_file = project_path() + '/resources/word_count.txt'
        output_file = project_path() + '/resources/word_count_output.csv'
        if os.path.exists(output_file):
            os.remove(output_file)

        example_1 = af.create_example(name="example_1",
                                      support_type=af.ExampleSupportType.EXAMPLE_BOTH,
                                      batch_uri=input_file,
                                      stream_uri=input_file,
                                      data_format="csv")

        example_2 = af.create_example(name="example_2",
                                      support_type=af.ExampleSupportType.EXAMPLE_BOTH,
                                      batch_uri=output_file,
                                      stream_uri=output_file,
                                      data_format="csv")
        if 'test_run_mode' in os.environ and 'cluster' == os.environ['test_run_mode']:
            task_config = 'task_4'
        else:
            task_config = 'task_3'

        def build_and_submit_ai_flow():
            with af.global_config_file(workflow_config_file()):
                with af.config(task_config):
                    input_example = af.read_example(example_info=example_1,
                                                    executor=faf.flink_executor.FlinkPythonExecutor(
                                                        python_object=Source())
                                                    )
                    processed = af.transform(input_data_list=[input_example],
                                             executor=faf.flink_executor.FlinkPythonExecutor(
                                                 python_object=Transformer()))

                    af.write_example(input_data=processed,
                                     example_info=example_2,
                                     executor=faf.flink_executor.FlinkPythonExecutor(python_object=Sink())
                                     )
                workflow_info = af.workflow_operation.submit_workflow('test_workflow')
            return workflow_info.workflow_name

        def run_task_function(client: NotificationClient):
            af.workflow_operation.start_new_workflow_execution('test_workflow')
            while True:
                with create_session() as session:
                    dag_run = session.query(DagRun).filter(DagRun.dag_id == 'test_project.test_workflow').first()
                    if dag_run is not None and dag_run.state in State.finished:
                        break
                    else:
                        time.sleep(1)

        self.run_ai_flow(build_and_submit_ai_flow, run_task_function)
        with create_session() as session:
            tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_project.test_workflow',
                                                      TaskExecution.task_id == task_config).all()
            self.assertEqual(1, len(tes))


