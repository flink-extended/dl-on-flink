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
from ai_flow.airflow.dag_generator import AirflowCodeGenerator, register_airflow_code_generator
from ai_flow.translator.base_translator import BaseJobGenerator, register_job_generator
from ai_flow.workflow.job import BaseJob, JobContext
from ai_flow.workflow.job_config import BaseJobConfig, register_job_config
from ai_flow.deployer.job_submitter import BaseJobSubmitter, register_job_submitter
from ai_flow.graph.graph import AISubGraph
from ai_flow.project.project_description import ProjectDesc
from ai_flow.plugins.platform import AbstractPlatform, AbstractJobHandler
from ai_flow.plugins.engine import AbstractEngine
from ai_flow.airflow.dag_generator import job_name_to_task_id
from abc import abstractmethod
import logging

AbstractJobGenerator = BaseJobGenerator
AbstractJob = BaseJob
AbstractJobConfig = BaseJobConfig
AbstractJobSubmitter = BaseJobSubmitter


class AbstractJobPlugin(AbstractJobGenerator, AbstractJobSubmitter, AirflowCodeGenerator):

    def __init__(self) -> None:
        super().__init__()

    # job generator interface
    @abstractmethod
    def generate(self, sub_graph: AISubGraph, project_desc: ProjectDesc) -> AbstractJob:
        """
        Generate the job to execute.
        :param sub_graph: The subgraph of AI graph, which describes the operation logic of a job
        :param project_desc: The ai flow project description.
        :return: the job.
        """
        pass

    @abstractmethod
    def generate_job_resource(self, job: AbstractJob) -> None:
        pass

    # job submitter interface
    @abstractmethod
    def submit_job(self, job: AbstractJob) -> AbstractJobHandler:
        """
        submit an executable job to run.

        :param job: A base job object that contains the necessary information for an execution.
        :return base_job_handler: a job handler that maintain the handler of a jobs runtime.
        """
        pass

    @abstractmethod
    def stop_job(self, job: AbstractJob):
        """
        Stop a ai flow job.
        :param job: A base job object that contains the necessary information for an execution.
        """
        pass

    @abstractmethod
    def cleanup_job(self, job: AbstractJob):
        """
        clean up temporary resources created during this execution.
        :param job: A base job object that contains the necessary information for an execution.
        """
        pass

    # job type
    @abstractmethod
    def job_type(self) -> type(AbstractJob):
        """
        :return: The job type, which is a subclass of AbstractJob type.
        """
        pass

    # job config type
    @abstractmethod
    def job_config_type(self) -> type(AbstractJobConfig):
        """
        :return: The job config type, which is a subclass of AbstractJobConfig type.
        """
        pass

    @abstractmethod
    def platform(self) -> type(AbstractPlatform):
        """
        :return: The platform type, which is a subclass of AbstractPlatform type.
        """
        pass

    @abstractmethod
    def engine(self) -> type(AbstractEngine):
        """
        :return: The engine type, which is a subclass of AbstractEngine type.
        """
        pass


def register_job_plugin(plugin: AbstractJobPlugin):
    logging.debug("Register job plugin {} {} {}".format(plugin.__class__.__name__,
                                                        plugin.platform().platform(),
                                                        plugin.engine().engine()))
    register_job_generator(platform=plugin.platform().platform(), engine=plugin.engine().engine(), generator=plugin)
    register_job_submitter(platform=plugin.platform().platform(), engine=plugin.engine().engine(), job_submitter=plugin)
    register_job_config(platform=plugin.platform().platform(), engine=plugin.engine().engine(),
                        job_config_class=plugin.job_config_type())
    register_airflow_code_generator(plugin.platform().platform(), plugin.engine().engine(), plugin)
