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
from abc import ABC, abstractmethod
from ai_flow.workflow.job import BaseJob
from ai_flow.workflow.job_handler import BaseJobHandler
from ai_flow.common.registry import BaseRegistry


class BaseJobSubmitter(ABC):
    """
    Used for submitting an executable job to specific platform when it's scheduled to run in workflow scheduler.
    The submitter is able to control the lifecycle of a workflow job. Users can also implement custom job submitter with
    their own job engine and execution platform.
    """

    def __init__(self) -> None:
        """
        Construct a :py:class:`ai_flow.deployer.job_submitter.BaseJobSubmitter`
        """
        pass

    @abstractmethod
    def submit_job(self, job: BaseJob) -> BaseJobHandler:
        """
        submit an executable job to run.

        :param job: A base job object that contains the necessary information for an execution.
        :return base_job_handler: a job handler that maintain the handler of a jobs runtime.
        """
        pass

    @abstractmethod
    def stop_job(self, job: BaseJob):
        """
        Stop a ai flow job.
        :param job: A base job object that contains the necessary information for an execution.
        """
        pass

    def cleanup_job(self, job: BaseJob):
        """
        clean up temporary resources created during this execution.
        :param job: A base job object that contains the necessary information for an execution.
        """
        pass


class JobSubmitterManager(BaseRegistry):
    def __init__(self) -> None:
        super().__init__()

    def submit_job(self, job: BaseJob) -> BaseJobHandler:
        job_submitter = self.get_job_submitter(job)
        return job_submitter.submit_job(job)

    def get_job_submitter(self, job):
        job_submitter: BaseJobSubmitter = self.get_object((job.platform, job.exec_engine))
        if job_submitter is None:
            raise Exception("job submitter platform {} engine {} not found!".format(job.platform, job.exec_engine))
        return job_submitter

    def stop_job(self, job: BaseJob):
        job_submitter = self.get_job_submitter(job)
        job_submitter.stop_job(job)

    def cleanup_job(self, job: BaseJob):
        job_submitter = self.get_job_submitter(job)
        job_submitter.cleanup_job(job=job)


_default_job_submitter_manager = JobSubmitterManager()


def register_job_submitter(platform, engine, job_submitter: BaseJobSubmitter):
    _default_job_submitter_manager.register((platform, engine), job_submitter)


def get_default_job_submitter_manager() -> JobSubmitterManager:
    return _default_job_submitter_manager
