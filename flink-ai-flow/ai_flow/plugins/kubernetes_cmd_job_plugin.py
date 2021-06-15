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
from typing import Dict, List
from kubernetes import client

from ai_flow.airflow.dag_generator import job_name_to_task_id
from ai_flow.plugins.job_plugin import AISubGraph, ProjectDesc, JobContext, \
    AbstractJobConfig, AbstractJob, AbstractEngine
from ai_flow.plugins.engine import CMDEngine
from ai_flow.plugins.kubernetes_platform import DEFAULT_PROJECT_PATH, \
    ANNOTATION_WORKFLOW_ID, ANNOTATION_JOB_UUID, ANNOTATION_JOB_ID, ANNOTATION_WATCHED
from ai_flow.plugins.kubernetes_job_plugin import KubernetesJob, KubernetesJobPlugin, KubernetesJobConfig
from ai_flow.meta.job_meta import ExecutionMode
from ai_flow.graph.ai_nodes.executable import ExecutableNode
from ai_flow.executor.executor import CmdExecutor
from ai_flow.util import json_utils


class KubernetesCMDJobConfig(KubernetesJobConfig):
    @staticmethod
    def from_dict(data: Dict, config) -> object:
        return AbstractJobConfig.from_dict(data, config)

    def __init__(self):
        super().__init__(engine=CMDEngine.engine())


class KubernetesCMDJob(KubernetesJob):
    def __init__(self,
                 exec_cmd,
                 job_context: JobContext = JobContext(),
                 job_config: AbstractJobConfig = KubernetesCMDJobConfig()):
        super().__init__(job_context, job_config)
        self.exec_cmd = exec_cmd


class KubernetesCMDJobPlugin(KubernetesJobPlugin):

    def __init__(self) -> None:
        super().__init__()

    def generate(self, sub_graph: AISubGraph, project_desc: ProjectDesc) -> AbstractJob:
        assert 1 == len(sub_graph.nodes)
        node: ExecutableNode = list(sub_graph.nodes.values())[0]
        if sub_graph.config.exec_mode == ExecutionMode.BATCH:
            context = JobContext(ExecutionMode.BATCH)
        else:
            context = JobContext(ExecutionMode.STREAM)
        executor: CmdExecutor = node.executor
        return KubernetesCMDJob(job_context=context, exec_cmd=executor.cmd_line, job_config=sub_graph.config)

    def generate_job_resource(self, job: AbstractJob) -> None:
        pass

    def job_type(self) -> type(AbstractJob):
        return KubernetesCMDJob

    def job_config_type(self) -> type(AbstractJobConfig):
        return KubernetesCMDJobConfig

    def engine(self) -> type(AbstractEngine):
        return CMDEngine

    def generate_job_name(self, job):
        return job.job_name.lower().replace('.', '-').replace('_', '-')

    def create_k8s_job(self, job: KubernetesCMDJob) -> client.V1Job:
        volume_mount = client.V1VolumeMount(name='download-volume', mount_path=DEFAULT_PROJECT_PATH)
        image = job.job_config.properties.get('ai_flow_worker_image')
        if isinstance(job.exec_cmd, List):
            cmd = job.exec_cmd
        else:
            cmd = [job.exec_cmd]
        working_dir = KubernetesJobPlugin.get_container_working_dir(job)
        job_container = client.V1Container(name='cmd-job',
                                           image=image,
                                           image_pull_policy='Always',
                                           command=cmd,
                                           working_dir=working_dir,
                                           volume_mounts=[volume_mount])

        pod_spec = KubernetesJobPlugin.create_init_container(job, volume_mount, job_container)
        labels = {'app': 'ai-flow', 'component': 'cmd-job-' + str(job.instance_id)}
        object_meta = client.V1ObjectMeta(labels=labels,
                                          annotations={ANNOTATION_WATCHED: 'True',
                                                       ANNOTATION_JOB_ID: str(job.instance_id),
                                                       ANNOTATION_JOB_UUID: str(job.uuid),
                                                       ANNOTATION_WORKFLOW_ID: str(
                                                           job.job_context.workflow_execution_id)})
        template_spec = client.V1PodTemplateSpec(metadata=object_meta,
                                                 spec=pod_spec)
        job_spec = client.V1JobSpec(template=template_spec, backoff_limit=0)
        object_meta = client.V1ObjectMeta(labels=labels,
                                          name=self.generate_job_name(job))
        job = client.V1Job(metadata=object_meta, spec=job_spec, api_version='batch/v1', kind='Job')
        return job

    def generate_code(self, op_index, job):
        K8S_CMD = """k8s_cmd_{0} = \"""{2}\"""\nop_{0} = KubernetesCMDOperator(task_id='{1}', dag=dag, job=k8s_cmd_{0})\n"""
        return K8S_CMD.format(op_index, job_name_to_task_id(job.job_name), json_utils.dumps(job))

    def generate_operator_code(self):
        return """from ai_flow.plugins.kubernetes_cmd_operator import KubernetesCMDOperator\n"""
