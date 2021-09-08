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
from unittest import mock

from ai_flow.workflow.status import Status

from ai_flow.plugin_interface.job_plugin_interface import JobController

from airflow.models.taskexecution import TaskExecution

from ai_flow_plugins.scheduler_plugins.airflow.ai_flow_operator import ExecutionLabelReportThread


class TestExecutionLabelReportThread(unittest.TestCase):

    def test_run(self):
        task_execution: TaskExecution = mock.Mock()
        job_controller: JobController = mock.Mock()
        job_controller.obtain_job_label.return_value = 'test_label'
        job_controller.get_job_status.return_value = Status.RUNNING
        job_handle = mock.Mock()

        t = ExecutionLabelReportThread(task_execution, 5.0, job_controller, job_handle)

        try:
            t.start()
            time.sleep(1)
            task_execution.update_task_execution_label.assert_called_with('test_label')
        finally:
            t.stop()
            t.join()
