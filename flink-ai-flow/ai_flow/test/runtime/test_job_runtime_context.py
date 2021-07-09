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
import unittest
import os

from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo

from ai_flow.context.job_context import current_job_name
from ai_flow.context.project_context import current_project_config
from ai_flow.context.workflow_config_loader import current_workflow_config
from ai_flow.runtime.job_runtime_env import JobRuntimeEnv
from ai_flow.runtime.job_runtime_context import init_job_runtime_context


class TestJobRuntimeContext(unittest.TestCase):

    def test_init_job_runtime_context(self):
        working_dir = os.path.dirname(__file__)
        job_runtime_env = JobRuntimeEnv(working_dir=working_dir, workflow_name='workflow_1',
                                        job_execution_info=JobExecutionInfo(job_name='task_1'))
        init_job_runtime_context(job_runtime_env)
        self.assertEqual('workflow_1', current_workflow_config().workflow_name)
        self.assertEqual('task_1', current_workflow_config().job_configs[current_job_name()].job_name)
        self.assertEqual('test_project', current_project_config().get_project_name())


if __name__ == '__main__':
    unittest.main()
