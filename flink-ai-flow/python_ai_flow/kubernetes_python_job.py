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
from tempfile import NamedTemporaryFile
from kubernetes import client

from ai_flow.airflow.dag_generator import job_name_to_task_id
from ai_flow.common import json_utils
from ai_flow.plugins.engine import AbstractEngine
from ai_flow.plugins.platform import AbstractPlatform
from python_ai_flow.local_python_job import LocalPythonJobPlugin, LocalPythonJob, LocalPythonJobConfig
from typing import Text, Dict, Any, Optional, Tuple, List
from ai_flow.plugins.job_plugin import AISubGraph, ProjectDesc, JobContext, AbstractJobConfig, AbstractJob
from ai_flow.plugins.kubernetes_platform import KubernetesPlatform, KubernetesJobHandler, DEFAULT_PROJECT_PATH, \
    ANNOTATION_WATCHED, ANNOTATION_JOB_ID, ANNOTATION_JOB_UUID, ANNOTATION_WORKFLOW_ID
from ai_flow.plugins.kubernetes_job_plugin import KubernetesJobPlugin, KubernetesJob
from ai_flow.meta.job_meta import ExecutionMode
from ai_flow.common.serialization_utils import serialize
from python_ai_flow.python_engine import PythonEngine
from python_ai_flow.python_job_common import RunGraph, batch_run_func, stream_run_func, BaseExampleComponent


class KubernetesPythonJobConfig(LocalPythonJobConfig):
    def __init__(self) -> None:
        super().__init__()
        self.platform = KubernetesPlatform.platform()
        self.engine = PythonEngine.engine()


class KubernetesPythonJob(LocalPythonJob, KubernetesJob):
    def __init__(self,
                 run_func: bytes,
                 run_graph: Optional[RunGraph],
                 job_context: JobContext = JobContext(),
                 job_config: KubernetesPythonJobConfig = KubernetesPythonJobConfig()):
        super().__init__(run_func, run_graph, job_context, job_config)


class KubernetesPythonJobPlugin(LocalPythonJobPlugin, KubernetesJobPlugin):

    def __init__(self) -> None:
        super().__init__()
        self.job_handler_map: Dict[Text, KubernetesJobHandler] = {}

    def job_type(self) -> type(AbstractJob):
        return KubernetesPythonJob

    def job_config_type(self) -> type(AbstractJobConfig):
        return KubernetesPythonJobConfig

    def platform(self) -> type(AbstractPlatform):
        return KubernetesPlatform

    def engine(self) -> type(AbstractEngine):
        return PythonEngine

    def generate(self, sub_graph: AISubGraph, project_desc: ProjectDesc) -> KubernetesPythonJob:
        if sub_graph.config.exec_mode == ExecutionMode.BATCH:
            run_func = serialize(batch_run_func)
            py_context = JobContext(ExecutionMode.BATCH)
        else:
            run_func = serialize(stream_run_func)
            py_context = JobContext(ExecutionMode.STREAM)

        py_context.project_config = project_desc.project_config
        run_graph: RunGraph = self.build_run_graph(sub_graph, py_context)
        job_config: KubernetesPythonJobConfig = sub_graph.config

        return KubernetesPythonJob(run_graph=run_graph, run_func=run_func,
                                   job_context=py_context, job_config=job_config)

    def generate_job_resource(self, job: KubernetesPythonJob):
        LocalPythonJobPlugin.generate_job_resource(self, job)

    def cleanup_job(self, job: KubernetesPythonJob):
        KubernetesJobPlugin.cleanup_job(self, job)

    def stop_job(self, job: KubernetesPythonJob):
        return KubernetesJobPlugin.stop_job(self, job)

    def submit_job(self, job: KubernetesPythonJob) -> KubernetesJobHandler:
        return KubernetesJobPlugin.submit_job(self, job)

    def generate_job_name(self, job):
        return job.job_name.lower().replace('.', '-').replace('_', '-')

    def create_k8s_job(self, job: KubernetesPythonJob) -> client.V1Job:
        volume_mount = client.V1VolumeMount(name='download-volume', mount_path=DEFAULT_PROJECT_PATH)
        image = job.job_config.properties.get('ai_flow_worker_image')
        python_job_args = [str(job.job_context.workflow_execution_id), job.exec_func_file, job.exec_args_file,
                           job.job_config.properties.get('entry_module_path')]
        working_dir = KubernetesJobPlugin.get_container_working_dir(job)
        job_container = client.V1Container(name='python-job',
                                           image=image,
                                           image_pull_policy='Always',
                                           command=['/opt/python_entrypoint.sh'],
                                           args=python_job_args,
                                           working_dir=working_dir,
                                           volume_mounts=[volume_mount])

        pod_spec = KubernetesJobPlugin.create_init_container(job, volume_mount, job_container)
        labels = {'app': 'ai-flow', 'component': 'python-job-' + str(job.instance_id)}
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

    def generate_code(self, op_index, job: AbstractJob):
        with NamedTemporaryFile(mode='w+t', prefix=job.job_name, suffix='.json',
                                dir=job.job_config.project_desc.get_absolute_temp_path(), delete=False) as f:
            f.write(json_utils.dumps(job))
            K8S_PYTHON = """k8s_python_{0} = "{2}"\nop_{0} = KubernetesPythonOperator(task_id='{1}', dag=dag, job_file=k8s_python_{0})\n"""
            return K8S_PYTHON.format(op_index, job.job_name, f.name)

    def generate_operator_code(self):
        return """from python_ai_flow.kubernetes_python_operator import KubernetesPythonOperator\n"""


_default_k8s_python_job_plugin = KubernetesPythonJobPlugin()


def get_default_k8s_python_job_plugin() -> KubernetesPythonJobPlugin:
    return _default_k8s_python_job_plugin


def register_k8s_example_component(key: Text, component: type(BaseExampleComponent)) -> None:
    _default_k8s_python_job_plugin.register_example(key, component)
