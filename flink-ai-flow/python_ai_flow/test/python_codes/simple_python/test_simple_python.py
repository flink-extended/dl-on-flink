#
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
#
import os
import unittest
from typing import List
from ai_flow.application_master.master import AIFlowMaster
from ai_flow.udf.function_context import FunctionContext
from python_ai_flow import Executor
from python_ai_flow.local_python_job import LocalPythonJobConfig
from python_ai_flow.test import test_util
import ai_flow as af


class SimpleExecutor(Executor):
    def execute(self, function_context: FunctionContext, input_list: List) -> List:
        print("hello world!")
        return []


class TestSimplePython(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config_file = test_util.get_master_config_file()
        cls.master = AIFlowMaster(config_file=config_file)
        cls.master.start()
        test_util.set_project_config(__file__)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.master.stop()
        af.unset_project_config()

    def tearDown(self):
        TestSimplePython.master._clear_db()

    def test_deploy_airflow(self):
        airflow_path = af.project_config().get_airflow_deploy_path()
        if not os.path.exists(airflow_path):
            os.makedirs(airflow_path)
        with af.config(LocalPythonJobConfig(job_name="simple")):
            op = af.user_define_operation(af.PythonObjectExecutor(SimpleExecutor()))
        res = af.run(test_util.get_project_path())
        af.wait_workflow_execution_finished(res)
