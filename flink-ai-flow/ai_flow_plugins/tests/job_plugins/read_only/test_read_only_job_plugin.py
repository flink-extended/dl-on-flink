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
from threading import Thread
from unittest import mock

from ai_flow.workflow.job import Job

from ai_flow.workflow.status import Status

from ai_flow import DatasetMeta
from ai_flow.ai_graph.ai_node import AINode, ReadDatasetNode, WriteDatasetNode

from ai_flow.workflow.job_config import JobConfig

from ai_flow.ai_graph.ai_graph import AISubGraph
from ai_flow_plugins.job_plugins.bash import BashProcessor
from ai_flow_plugins.job_plugins.read_only import ReadOnlyProcessor, ReadOnlyJobGenerator, ReadOnlyJob, \
    ReadOnlyJobController, ReadOnlyJobHandle


class TestReadOnlyJobGenerator(unittest.TestCase):

    def test_generate_throw_unknown_type_exception(self):
        sub_graph = AISubGraph(JobConfig())
        ai_node = AINode(processor=BashProcessor('hello'))
        sub_graph.add_node(ai_node)
        sub_graph.add_node(AINode(processor=ReadOnlyProcessor()))
        job_generator = ReadOnlyJobGenerator()

        with self.assertRaises(TypeError):
            job_generator.generate(sub_graph)

    def test_generate(self):
        sub_graph = AISubGraph(JobConfig())
        sub_graph.add_node(ReadDatasetNode(dataset=DatasetMeta("test"), processor=ReadOnlyProcessor()))
        sub_graph.add_node(AINode(processor=ReadOnlyProcessor()))
        sub_graph.add_node(WriteDatasetNode(dataset=DatasetMeta("test"), processor=ReadOnlyProcessor()))
        job_generator = ReadOnlyJobGenerator()

        job = job_generator.generate(sub_graph)
        self.assertIsInstance(job, ReadOnlyJob)

    def test_generate_with_required_configs(self):
        job_config = JobConfig()
        sub_graph = AISubGraph(job_config)
        sub_graph.add_node(ReadDatasetNode(dataset=DatasetMeta("test"), processor=ReadOnlyProcessor()))
        sub_graph.add_node(AINode(processor=ReadOnlyProcessor()))
        sub_graph.add_node(WriteDatasetNode(dataset=DatasetMeta("test"), processor=ReadOnlyProcessor()))
        job_generator = ReadOnlyJobGenerator(required_properties={'required_key'})

        with self.assertRaises(RuntimeError):
            job_generator.generate(sub_graph)

        job_config.properties['required_key'] = 'value'
        job = job_generator.generate(sub_graph)
        self.assertIsInstance(job, ReadOnlyJob)


class TestReadOnlyJobController(unittest.TestCase):

    def setUp(self) -> None:
        self.job_controller = ReadOnlyJobController()
        self.job = ReadOnlyJob(JobConfig("test_job"))

    def test_submit_job(self):
        job_runtime_env = mock.Mock()
        job_execution_info = mock.Mock()
        job_runtime_env.job_execution_info = job_execution_info
        handle = self.job_controller.submit_job(self.job, job_runtime_env)
        self.assertIsInstance(handle, ReadOnlyJobHandle)
        self.assertEqual(self.job, handle.job)
        self.assertEqual(job_execution_info, handle.job_execution)

    def test_stop_job(self):
        job_runtime_env = mock.Mock()
        job_execution_info = mock.Mock()
        job_runtime_env.job_execution_info = job_execution_info
        with self.assertRaises(RuntimeError):
            self.job_controller.stop_job(ReadOnlyJobHandle(mock.Mock(), job_execution_info), job_runtime_env)

        handle = self.job_controller.submit_job(self.job, job_runtime_env)
        self.assertFalse(self.job_controller._job_stop_events[handle.job].is_set())
        self.job_controller.stop_job(handle, job_runtime_env)
        self.assertTrue(self.job_controller._job_stop_events[handle.job].is_set())

    def test_get_result(self):
        job_runtime_env = mock.Mock()
        job_execution_info = mock.Mock()
        job_runtime_env.job_execution_info = job_execution_info
        with self.assertRaises(RuntimeError):
            self.job_controller.get_result(ReadOnlyJobHandle(mock.Mock(), job_execution_info), job_runtime_env)

        handle = self.job_controller.submit_job(self.job, job_runtime_env)
        self.assertIsNone(self.job_controller.get_result(handle, False))

        def get_result():
            result = self.job_controller.get_result(handle, True)
            self.assertIsNone(result)
            self.assertTrue(self.job_controller._job_stop_events[handle.job].is_set())

        t = Thread(target=get_result)
        t.start()

        time.sleep(0.5)
        self.job_controller.stop_job(handle, job_runtime_env)
        t.join()

    def test_get_job_status(self):
        job_runtime_env = mock.Mock()
        job_execution_info = mock.Mock()
        job_runtime_env.job_execution_info = job_execution_info
        with self.assertRaises(RuntimeError):
            self.job_controller.get_job_status(ReadOnlyJobHandle(mock.Mock(), job_execution_info))
        handle = self.job_controller.submit_job(self.job, job_runtime_env)
        self.assertEqual(Status.RUNNING, self.job_controller.get_job_status(handle))

    def test_obtain_job_label(self):
        job_runtime_env = mock.Mock()
        job_execution_info = mock.Mock()
        job_runtime_env.job_execution_info = job_execution_info
        with self.assertRaises(RuntimeError):
            self.job_controller.obtain_job_label(ReadOnlyJobHandle(mock.Mock(), job_execution_info))

        handle = self.job_controller.submit_job(self.job, job_runtime_env)
        self.assertEqual("", self.job_controller.obtain_job_label(handle))

    def test_obtain_job_label_check_job_type(self):
        job_runtime_env = mock.Mock()
        job_execution_info = mock.Mock()
        job_runtime_env.job_execution_info = job_execution_info

        job = Job(mock.Mock())
        handle = self.job_controller.submit_job(job, job_runtime_env)
        with self.assertRaises(TypeError):
            self.job_controller.obtain_job_label(handle)
