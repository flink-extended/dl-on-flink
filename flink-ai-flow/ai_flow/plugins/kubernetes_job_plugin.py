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
import logging
from abc import ABC, abstractmethod
from typing import Dict, Text
from kubernetes import client
from ai_flow.plugins.platform import AbstractPlatform
from ai_flow.workflow.job_context import JobContext

from ai_flow.plugins.kubernetes_platform import KubernetesPlatform, KubernetesJobHandler, DEFAULT_NAMESPACE, \
    DEFAULT_PROJECT_PATH

from ai_flow.plugins.job_plugin import AbstractJobConfig, AbstractJob, AbstractJobPlugin
from ai_flow.plugins import k8s_util


class KubernetesJobConfig(AbstractJobConfig):
    @staticmethod
    def from_dict(data: Dict, config) -> object:
        return AbstractJobConfig.from_dict(data, config)

    def __init__(self, engine: Text):
        super().__init__(platform=KubernetesPlatform.platform(), engine=engine)


class KubernetesJob(AbstractJob):
    def __init__(self,
                 job_context: JobContext = JobContext(),
                 job_config: AbstractJobConfig = KubernetesJobConfig):
        super().__init__(job_context, job_config)
        self.k8s_job_handler = None


class KubernetesJobPlugin(AbstractJobPlugin, ABC):

    def __init__(self) -> None:
        super().__init__()
        self.job_handler_map: Dict[Text, KubernetesJobHandler] = {}

    def platform(self) -> type(AbstractPlatform):
        return KubernetesPlatform

    def submit_job(self, job: KubernetesJob) -> KubernetesJobHandler:
        if job.k8s_job_handler is None:
            job.k8s_job_handler = self.create_k8s_job(job)

        batchV1 = client.BatchV1Api()
        batchV1.create_namespaced_job(namespace=DEFAULT_NAMESPACE, body=job.k8s_job_handler)
        logging.info("create k8s job {}".format(job.job_name))
        job_handler = KubernetesJobHandler(job_instance_id=job.instance_id,
                                           job_uuid=job.uuid,
                                           workflow_id=job.job_context.workflow_execution_id)
        return job_handler

    def stop_job(self, job: KubernetesJob):
        self.cleanup_job(job)

    def cleanup_job(self, job: KubernetesJob):
        if job.k8s_job_handler is None:
            return
        if job.job_config.is_clean_job_resource():
            k8s_util.kill_job(name=job.k8s_job_handler.metadata.name)
            job.k8s_job_handler = None

        if job.uuid in self.job_handler_map:
            del self.job_handler_map[job.uuid]

    @abstractmethod
    def create_k8s_job(self, job: KubernetesJob)->client.V1Job:
        pass

    @staticmethod
    def create_init_container(job: AbstractJob, volume_mount, job_container)->client.V1PodSpec:
        return k8s_util.create_init_container(job, volume_mount, job_container)

    @staticmethod
    def get_container_working_dir(job: AbstractJob)->Text:
        return k8s_util.get_container_working_dir(job)
