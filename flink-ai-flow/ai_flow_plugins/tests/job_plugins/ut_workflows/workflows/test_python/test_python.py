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
import unittest
import os
import time
import shutil
from typing import List

from ai_flow import AIFlowServerRunner, init_ai_flow_context
from ai_flow.workflow.status import Status
from ai_flow_plugins.job_plugins import python
import ai_flow as af
from ai_flow_plugins.job_plugins.python.python_processor import ExecutionContext

project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class PyProcessor1(python.PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        print("Zhang san hello world!")
        return []


class PyProcessor2(python.PythonProcessor):

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        print("Li si hello world!")
        time.sleep(100)
        return []


class TestPython(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config_file = project_path + '/master.yaml'
        cls.master = AIFlowServerRunner(config_file=config_file)
        cls.master.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.master.stop()
        generated = '{}/generated'.format(project_path)
        if os.path.exists(generated):
            shutil.rmtree(generated)
        temp = '{}/temp'.format(project_path)
        if os.path.exists(temp):
            shutil.rmtree(temp)

    def setUp(self):
        self.master._clear_db()
        af.current_graph().clear_graph()
        init_ai_flow_context()

    def tearDown(self):
        self.master._clear_db()

    def test_python_task(self):
        with af.job_config('task_1'):
            af.user_define_operation(processor=PyProcessor1())
        w = af.workflow_operation.submit_workflow(workflow_name=af.current_workflow_config().workflow_name)
        je = af.workflow_operation.start_job_execution(job_name='task_1', execution_id='1')
        je = af.workflow_operation.get_job_execution(job_name='task_1', execution_id='1')
        self.assertEqual(Status.FINISHED, je.status)

    def test_stop_python_task(self):
        time.sleep(1)
        with af.job_config('task_1'):
            af.user_define_operation(processor=PyProcessor2())
        w = af.workflow_operation.submit_workflow(workflow_name='test_python')
        je = af.workflow_operation.start_job_execution(job_name='task_1', execution_id='1')
        time.sleep(2)
        af.workflow_operation.stop_job_execution(job_name='task_1', execution_id='1')
        je = af.workflow_operation.get_job_execution(job_name='task_1', execution_id='1')
        self.assertEqual(Status.FAILED, je.status)
        self.assertTrue('err' in je.properties)


if __name__ == '__main__':
    unittest.main()
