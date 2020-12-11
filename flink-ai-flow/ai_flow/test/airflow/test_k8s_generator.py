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
import sys
import unittest
import os
import ai_flow as af
from ai_flow import AIFlowMaster
from ai_flow.executor.executor import CmdExecutor
from ai_flow.test import test_util


class TestProject(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config_file = test_util.get_master_config_file()
        cls.master = AIFlowMaster(config_file=config_file)
        cls.master.start()
        test_util.set_project_config(__file__)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.master.stop()

    def setUp(self):
        TestProject.master._clear_db()
        af.default_graph().clear_graph()

    def tearDown(self):
        TestProject.master._clear_db()

    def test_k8s_cmd(self):
        print(sys._getframe().f_code.co_name)
        project_path = os.path.dirname(__file__) + '/../'
        job_config = af.KubernetesCMDJobConfig()
        job_config.job_name = 'test_cmd'
        with af.config(job_config):
            cmd_executor = af.user_define_operation(output_num=0,
                                                    executor=CmdExecutor(
                                                        cmd_line="echo 'hello world' && sleep {}".format(1)))
        code_text = af.generate_airflow_file_text(project_path, "hh")
        print(code_text)
