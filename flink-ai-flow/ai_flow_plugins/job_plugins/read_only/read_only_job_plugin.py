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
import threading
from abc import ABC, abstractmethod
from typing import Text, Set

import typing

from ai_flow.ai_graph.ai_node import ReadDatasetNode, WriteDatasetNode

from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo

from ai_flow.workflow.job_config import JobConfig

from ai_flow.ai_graph.ai_graph import AISubGraph
from ai_flow.runtime.job_runtime_env import JobRuntimeEnv
from ai_flow.translator.translator import JobGenerator

from ai_flow.plugin_interface.job_plugin_interface import JobHandle, JobController, JobPluginFactory

from ai_flow.workflow.job import Job
from ai_flow.workflow.status import Status
from ai_flow_plugins.job_plugins.read_only.read_only_processor import ReadOnlyProcessor


class ReadOnlyJob(Job, ABC):
    def __init__(self, job_config: JobConfig):
        super().__init__(job_config)


class ReadOnlyJobHandle(JobHandle):
    def __init__(self, job: Job, job_execution_info: JobExecutionInfo):
        super().__init__(job, job_execution_info)


class ReadOnlyJobGenerator(JobGenerator):
    def __init__(self, required_properties=None):

        if required_properties is None:
            required_properties = set()
        self._required_properties = required_properties

    def generate(self, sub_graph: AISubGraph, resource_dir: Text = None) -> Job:
        for node_name, node in sub_graph.nodes.items():
            if isinstance(node, ReadDatasetNode) or isinstance(node, WriteDatasetNode):
                continue
            processor = node.get_processor()
            if not isinstance(processor, ReadOnlyProcessor):
                raise TypeError("Getting unknown processor type {} for node {}".format(type(processor), node_name))
        job_config = sub_graph.config
        self._validate_job_config(job_config)
        return ReadOnlyJob(job_config)

    def _validate_job_config(self, job_config: JobConfig):
        missing_properties = []
        for required_properties in self._required_properties:
            if required_properties not in job_config.properties:
                missing_properties.append(required_properties)

        if len(missing_properties) != 0:
            raise RuntimeError("Missing required properties: {}".format(missing_properties))


class ReadOnlyJobController(JobController):
    """
    ReadOnlyJobController implement JobController to manage the life cycle of a ReadOnlyJob. The ReadOnlyJobController
    is used to register a job to the workflow without actually submitting the job. It can report some runtime
    status of the job, if its get_job_label method is overwritten.

    This is useful when you want to register a job to the workflow so that you can capture the job's runtime status.
    And you don't want the workflow to actually run and stop a job.
    """

    def __init__(self):
        super().__init__()
        self._job_stop_events: typing.Dict[Job, threading.Event] = {}

    def submit_job(self, job: Job, job_runtime_env: JobRuntimeEnv) -> JobHandle:
        # submit job do not actually submit a job, it only return the JobHandle
        self._job_stop_events[job] = threading.Event()
        return ReadOnlyJobHandle(job, job_runtime_env.job_execution_info)

    def stop_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv):
        self._check_job_exists(job_handle)
        self._job_stop_events[job_handle.job].set()

    def cleanup_job(self, job_handle: JobHandle, job_runtime_env: JobRuntimeEnv):
        # do nothing
        pass

    def get_result(self, job_handle: JobHandle, blocking: bool = True) -> object:
        self._check_job_exists(job_handle)

        if not blocking:
            return None

        self._job_stop_events[job_handle.job].wait()
        return None

    def get_job_status(self, job_handle: JobHandle) -> Status:
        self._check_job_exists(job_handle)
        # The read only job itself should always be running
        return Status.RUNNING

    def obtain_job_label(self, job_handle: JobHandle) -> Text:
        self._check_job_exists(job_handle)
        if not isinstance(job_handle.job, ReadOnlyJob):
            raise TypeError("Unknown job type: {}".format(type(job_handle.job)))
        return self.get_job_label(job_handle.job)

    def get_job_label(self, job: ReadOnlyJob) -> Text:
        return ""

    def _check_job_exists(self, job_handle):
        if job_handle.job not in self._job_stop_events:
            raise RuntimeError("Cannot find job {}.".format(job_handle.job))


class ReadOnlyJobPluginFactory(JobPluginFactory):
    def job_type(self) -> Text:
        return "read_only_job"

    def get_job_generator(self) -> JobGenerator:
        return ReadOnlyJobGenerator()

    def get_job_controller(self) -> JobController:
        return ReadOnlyJobController()
