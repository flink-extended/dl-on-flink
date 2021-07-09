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
from typing import Text

from ai_flow.ai_graph.ai_graph import AISubGraph
from ai_flow.plugin_interface.job_plugin_interface import JobPluginFactory, \
    register_job_plugin_factory, get_registered_job_plugin_factory_list, JobHandle, JobRuntimeEnv, JobController
from ai_flow.translator.translator import JobGenerator
from ai_flow.workflow.job import Job
from ai_flow.workflow.status import Status


class MockJobPluginFactory1(JobPluginFactory, JobGenerator, JobController):

    def get_result(self, job_handle: JobHandle, blocking: bool = True):
        pass

    def get_job_status(self, job_handle: JobHandle) -> Status:
        pass

    def get_job_generator(self) -> JobGenerator:
        return self

    def get_job_controller(self) -> JobController:
        return self

    def job_type(self) -> Text:
        return "mock1"

    def generate(self, sub_graph: AISubGraph, resource_dir: Text = None) -> Job:
        pass

    def submit_job(self, job: Job, job_runtime_env: JobRuntimeEnv) -> JobHandle:
        pass

    def stop_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv):
        pass

    def cleanup_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv):
        pass


class MockJobPluginFactory2(JobPluginFactory, JobGenerator, JobController):

    def get_result(self, job_handle: JobHandle, blocking: bool = True):
        pass

    def get_job_status(self, job_handle: JobHandle) -> Status:
        pass

    def get_job_generator(self) -> JobGenerator:
        return self

    def get_job_controller(self) -> JobController:
        return self

    def job_type(self) -> Text:
        return "mock2"

    def generate(self, sub_graph: AISubGraph, resource_dir: Text = None) -> Job:
        pass

    def submit_job(self, job: Job, job_runtime_env: JobRuntimeEnv) -> JobHandle:
        pass

    def stop_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv):
        pass

    def cleanup_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv):
        pass


class TestJobPlugin(unittest.TestCase):

    def test_register_job_plugin(self):
        register_job_plugin_factory(MockJobPluginFactory1())
        register_job_plugin_factory(MockJobPluginFactory2())
        self.assertEqual(2, len(get_registered_job_plugin_factory_list()))
        self.assertTrue('mock1' in get_registered_job_plugin_factory_list())
        self.assertTrue('mock2' in get_registered_job_plugin_factory_list())


if __name__ == '__main__':
    unittest.main()
