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

from ai_flow.runtime.job_runtime_env import JobRuntimeEnv
from ai_flow.workflow.job import Job
from ai_flow.workflow.job_config import JobConfig

from ai_flow.workflow.workflow import Workflow, WorkflowPropertyKeys

from ai_flow.workflow.status import Status

from ai_flow.plugin_interface.job_plugin_interface import JobController, JobHandle
from ai_flow_plugins.job_plugins.read_only import ReadOnlyJob
from airflow import AirflowException

from airflow.models.taskexecution import TaskExecution

from ai_flow_plugins.scheduler_plugins.airflow.ai_flow_operator import ExecutionLabelReportThread, AIFlowOperator


class TestingJobController(JobController):

    def submit_job(self, job: Job, job_runtime_env: JobRuntimeEnv) -> JobHandle:
        pass

    def stop_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv):
        pass

    def cleanup_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv):
        pass

    def get_result(self, job_handle: JobHandle, blocking: bool = True) -> object:
        pass

    def get_job_status(self, job_handle: JobHandle) -> Status:
        pass


class TestAIFlowOperator(unittest.TestCase):

    def setUp(self) -> None:
        workflow = mock.MagicMock()
        workflow.properties = dict()
        workflow.properties[WorkflowPropertyKeys.JOB_PLUGINS] = \
            {'test_job': (TestingJobController.__module__, TestingJobController.__name__)}
        job_config = JobConfig()
        job_config.job_type = 'test_job'
        job = ReadOnlyJob(job_config)
        self.op = AIFlowOperator(workflow=workflow, job=job, task_id='1')

    def test_execute(self):
        with mock.patch.object(self.op, 'job_controller', wraps=self.op.job_controller) as job_controller:
            job_controller.get_result.return_value = 'result'
            mock_handle = mock.MagicMock()
            job_controller.submit_job.return_value = mock_handle
            self.assertEqual('result', self.op.execute({}))
            job_controller.submit_job.assert_called_once()
            job_controller.stop_job.assert_not_called()
            job_controller.get_result.assert_called_once_with(job_handle=mock_handle, blocking=True)
            job_controller.cleanup_job.assert_called_once_with(mock_handle, mock.ANY)

    def test_execute_raise_AirflowException(self):
        with mock.patch.object(self.op, 'job_controller', wraps=self.op.job_controller) as job_controller:
            job_controller.get_result.side_effect = AirflowException("Boom! Shakalaka!")
            mock_handle = mock.MagicMock()
            job_controller.submit_job.return_value = mock_handle

            with self.assertRaises(AirflowException):
                self.assertEqual(None, self.op.execute({}))
                job_controller.submit_job.assert_called_once()
                job_controller.get_result.assert_called_once_with(job_handle=mock_handle, blocking=True)
                job_controller.stop_job.assert_called_once_with(mock_handle, mock.ANY)
                job_controller.cleanup_job.assert_called_once_with(mock_handle, mock.ANY)

    def test_execute_raise_unexpected_exception(self):
        with mock.patch.object(self.op, 'job_controller', wraps=self.op.job_controller) as job_controller:
            job_controller.get_result.side_effect = RuntimeError("Boom! Shakalaka!")
            mock_handle = mock.MagicMock()
            job_controller.submit_job.return_value = mock_handle

            with self.assertRaises(RuntimeError):
                self.assertEqual(None, self.op.execute({}))
                job_controller.submit_job.assert_called_once()
                job_controller.get_result.assert_called_once_with(job_handle=mock_handle, blocking=True)
                job_controller.stop_job.assert_called_once_with(mock_handle, mock.ANY)
                job_controller.cleanup_job.assert_called_once_with(mock_handle, mock.ANY)


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
