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
import shutil
import uuid
from typing import Text, Dict
import os
import logging
from ai_flow.airflow.dag_generator import job_name_to_task_id
from ai_flow.plugins.platform import AbstractPlatform
from kubernetes import client
from pathlib import Path
from ai_flow.util import serialization_utils, json_utils
from ai_flow.util.json_utils import dumps
from ai_flow.plugins.job_plugin import AISubGraph, ProjectDesc, JobContext, \
    AbstractJobConfig, AbstractJob
from ai_flow.plugins.language import LanguageType
from ai_flow.plugins.kubernetes_platform import KubernetesPlatform, KubernetesJobHandler, \
    ANNOTATION_WORKFLOW_ID, ANNOTATION_JOB_ID, ANNOTATION_WATCHED, ANNOTATION_JOB_UUID
from ai_flow.meta.job_meta import ExecutionMode
from ai_flow.plugins.local_cmd_job_plugin import LocalCMDJob
from flink_ai_flow.flink_job_common import FlinkJobConfig
from flink_ai_flow import version
from flink_ai_flow.local_flink_job import LocalFlinkJobPlugin


class KubernetesFlinkJobConfig(FlinkJobConfig):
    """
    Implementation of the FlinkJobConfig. Used for set config of the kubernetes flink job.
    """

    def __init__(self):
        super().__init__(platform=KubernetesPlatform.platform())
        self.image = None
        self.parallelism = 2
        self.resources = {}
        self.flink_conf = {}
        self.logging_conf = {}


class KubernetesFlinkJob(LocalCMDJob):
    """
    Implementation of LocalCMDJob. Represents the kubernetes flink job.
    """

    def __init__(self,
                 ai_graph,
                 job_context: JobContext,
                 job_config: KubernetesFlinkJobConfig):
        """
        Construct method of KubernetesFlinkJob.

        :param ai_graph: Graph generated from ai nodes.
        :param job_context: Context of Kubernetes flink job.
        :param job_config: Config of kubernetes flink job.
        """
        super().__init__(exec_cmd=None, job_context=job_context, job_config=job_config)
        self.platform = KubernetesPlatform.platform()
        self.ai_graph = ai_graph
        self.config_file = None
        self.job_cluster_resource = None
        self.job_cluster_service_resource = None
        self.task_manager_resource = None
        self.flink_conf_config_map = None


class KubernetesFlinkJobPlugin(LocalFlinkJobPlugin):
    def __init__(self) -> None:
        super().__init__()
        self.job_handler_map: Dict[Text, KubernetesJobHandler] = {}

    def generate(self, sub_graph: AISubGraph, project_desc: ProjectDesc) -> KubernetesFlinkJob:
        """
        Generate Kubernetes flink job.

        :param sub_graph: Sub graph generates from ai nodes.
        :param project_desc: Description of the project.
        :return: Base job Object.
        """
        if sub_graph.config.exec_mode == ExecutionMode.BATCH:
            flink_context = JobContext(ExecutionMode.BATCH)
        else:
            flink_context = JobContext(ExecutionMode.STREAM)

        flink_context.project_config = project_desc.project_config
        k8s_job_config: KubernetesFlinkJobConfig = sub_graph.config
        job = KubernetesFlinkJob(ai_graph=sub_graph, job_context=flink_context, job_config=k8s_job_config)
        # set jar and class
        job.job_config.main_class = version.main_class
        job.job_config.jar_path = version.jar_path

        # set python main
        job.job_config.py_entry_file = version.py_main_file
        if job.job_config.language_type is None:
            job.job_config.language_type = self.get_language_type(sub_graph)

        return job

    def generate_job_resource(self, job: KubernetesFlinkJob) -> None:
        """
        Generate kubernetes flink job resource.

        :param job: Kubernetes flink job.
        """
        # gen config file
        project_path = job.job_config.project_path
        if project_path is None:
            project_path = "/tmp"
        project_path_temp = project_path + "/temp"

        if not os.path.exists(project_path_temp):
            os.mkdir(project_path_temp)
        execution_config_file = 'job_execution_config_' + str(uuid.uuid4()) + "_" + job.instance_id
        real_execution_config_file = project_path_temp + '/' + execution_config_file

        if job.job_config.language_type == LanguageType.JAVA:
            with open(real_execution_config_file, 'w') as f:
                f.write(dumps(job))
            job.config_file = Path(real_execution_config_file).name

        else:
            with open(real_execution_config_file, 'wb') as f:
                f.write(serialization_utils.serialize(job))
            job.config_file = execution_config_file

        # generate python_codes.zip
        python_codes = '{}/python_codes'.format(project_path)

        if os.path.exists(python_codes):
            zip_dir = '{}/zip'.format(project_path)
            if os.path.exists(zip_dir):
                shutil.rmtree(zip_dir)
            shutil.copytree(python_codes, zip_dir + '/python_codes')
            shutil.make_archive(python_codes, 'zip', zip_dir)

    def job_type(self) -> type(AbstractJob):
        return KubernetesFlinkJob

    def job_config_type(self) -> type(AbstractJobConfig):
        return KubernetesFlinkJobConfig

    def submit_job(self, job: KubernetesFlinkJob) -> KubernetesJobHandler:
        """
        Submit the flink job to run in kubernetes.

        :param job: A flink job object which contains the necessary information for an execution.
        :return: A job handler that maintains the handler of a job in runtime.
        """
        coreV1 = client.CoreV1Api()
        batchV1 = client.BatchV1Api()
        extensionsV1B1 = client.ExtensionsV1beta1Api()
        namespace = 'ai-flow'
        job.job_cluster_resource = get_flink_session_cluster_boilerplate(job)
        job.job_cluster_service_resource = get_flink_job_cluster_service_boilerplate(job)
        job.task_manager_resource = get_task_manager_boilerplate(job)
        job.flink_conf_config_map = get_flink_conf_config_map(job)
        coreV1.create_namespaced_service(namespace=namespace, body=job.job_cluster_service_resource)
        coreV1.create_namespaced_config_map(namespace=namespace, body=job.flink_conf_config_map)
        extensionsV1B1.create_namespaced_deployment(namespace=namespace, body=job.task_manager_resource)
        batchV1.create_namespaced_job(namespace=namespace, body=job.job_cluster_resource)
        hanlder = KubernetesJobHandler(job_instance_id=job.instance_id,
                                       workflow_id=job.job_context.workflow_execution_id,
                                       job_uuid=job.uuid)
        return hanlder

    def stop_job(self, job: KubernetesFlinkJob):
        """
        Stop an flink job in kubernetes.

        :param job: A flink job object which is going to be stopped.
        """
        if job.job_config.properties.get('debug_mode', False):
            return
        if job.job_config.is_clean_job_resource():
            self.cleanup_job(job)
        # coreV1 = client.CoreV1Api()
        # batchV1 = client.BatchV1Api()
        # extensionsV1B1 = client.ExtensionsV1beta1Api()
        # namespace = 'ai-flow'
        # coreV1.delete_namespaced_service(namespace=namespace, name=job.job_cluster_service_resource.metadata.name)
        # batchV1.delete_namespaced_job(namespace=namespace, name=job.job_cluster_resource.metadata.name,
        #                               body=client.V1DeleteOptions(
        #                                   propagation_policy='Foreground',
        #                                   grace_period_seconds=5))
        # extensionsV1B1.delete_namespaced_deployment(namespace=namespace, name=job.task_manager_resource.metadata.name,
        #                                             body=client.V1DeleteOptions(
        #                                                 propagation_policy='Foreground',
        #                                                 grace_period_seconds=5))
        # coreV1.delete_namespaced_config_map(namespace=namespace, name=job.flink_conf_config_map.metadata.name)

    def cleanup_job(self, job: KubernetesFlinkJob):
        """
        Clean up temporary resources created during this execution.
        However, this method should be pass when for debug usage, in debug mode,
        you can view the logs of this execution and other generated resource files

        :param job: A flink job object which is going to be cleaned up.
        """
        if job.job_config.properties.get('debug_mode', False):
            return
        coreV1 = client.CoreV1Api()
        batchV1 = client.BatchV1Api()
        extensionsV1B1 = client.ExtensionsV1beta1Api()
        namespace = 'ai-flow'
        coreV1.delete_namespaced_service(namespace=namespace, name=job.job_cluster_service_resource.metadata.name)
        batchV1.delete_namespaced_job(namespace=namespace, name=job.job_cluster_resource.metadata.name,
                                      body=client.V1DeleteOptions(
                                          propagation_policy='Foreground',
                                          grace_period_seconds=5))
        extensionsV1B1.delete_namespaced_deployment(namespace=namespace, name=job.task_manager_resource.metadata.name,
                                                    body=client.V1DeleteOptions(
                                                        propagation_policy='Foreground',
                                                        grace_period_seconds=5))
        coreV1.delete_namespaced_config_map(namespace=namespace, name=job.flink_conf_config_map.metadata.name)

    def platform(self) -> type(AbstractPlatform):
        return KubernetesPlatform

    def generate_job_name(self, job):
        return generate_job_name(job)

    def generate_code(self, op_index, job: AbstractJob):
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile(mode='w+t', prefix=job.job_name, suffix='.json',
                                dir=job.job_config.project_desc.get_absolute_temp_path(), delete=False) as f:
            f.write(json_utils.dumps(job))
            K8S_FLINK = """k8s_flink_{0} = "{2}"\nop_{0} = KubernetesFlinkOperator(task_id='{1}', dag=dag, job_file=k8s_flink_{0})\n"""
            return K8S_FLINK.format(op_index, job_name_to_task_id(job.job_name), f.name)

    def generate_operator_code(self):
        return "from flink_ai_flow.kubernetes_flink_operator import KubernetesFlinkOperator\n"


def get_flink_job_cluster_service_boilerplate(job: KubernetesFlinkJob) -> client.V1Service:
    labels = {'app': 'flink', 'component': 'job-cluster-' + str(job.uuid)}
    name = 'flink-job-cluster-' + str(job.uuid) + '-svc'
    object_meta = client.V1ObjectMeta(labels=labels, name=name)
    rpc_port = client.V1ServicePort(name='rpc', port=6123)
    blob_port = client.V1ServicePort(name='blob', port=6124)
    query_port = client.V1ServicePort(name='query', port=6125)
    ui_port = client.V1ServicePort(name='ui', port=8081)
    ports_list = [rpc_port, blob_port, query_port, ui_port]
    selector = labels
    spec = client.V1ServiceSpec(ports=ports_list, selector=selector, type="LoadBalancer")
    service = client.V1Service(api_version="v1", kind='Service', metadata=object_meta, spec=spec)
    return service


def generate_job_name(job):
    return 'flink-job-cluster-{}'.format(job.uuid)


def get_flink_session_cluster_boilerplate(job: KubernetesFlinkJob) -> client.V1Job:
    from ai_flow.application_master.master import GLOBAL_MASTER_CONFIG
    job_master_args_default = ["session-cluster",
                               "--job-classname", job.job_config.main_class,
                               "-Djobmanager.rpc.address=flink-job-cluster-{}-svc".format(job.uuid),
                               "-Dparallelism.default=1",
                               "-Dblob.server.port=6124",
                               "-Dqueryable-state.server.ports=6125"]
    rpc_container_port = client.V1ContainerPort(name='rpc', container_port=6123)
    blob_container_port = client.V1ContainerPort(name='blob', container_port=6124)
    query_container_port = client.V1ContainerPort(name='query', container_port=6125)
    ui_container_port = client.V1ContainerPort(name='ui', container_port=8081)
    mount_path = '/opt/ai-flow/project'
    volume_mount = client.V1VolumeMount(name='download-volume', mount_path=mount_path)
    flink_config_volume_mount = client.V1VolumeMount(name="flink-config-volume", mount_path="/opt/flink/conf")
    workflow_id_env = client.V1EnvVar(name='WORKFLOW_ID', value=str(job.job_context.workflow_execution_id))
    execution_config_env = client.V1EnvVar(name='CONFIG_FILE_NAME', value=job.config_file)
    if job.job_config.language_type == LanguageType.PYTHON:
        language_type_env = client.V1EnvVar(name='LANGUAGE_TYPE', value='python')
    else:
        language_type_env = client.V1EnvVar(name='LANGUAGE_TYPE', value='java')

    entry_module_path_env = client.V1EnvVar(name='ENTRY_MODULE_PATH',
                                            value=job.job_config.properties['entry_module_path'])
    flink_job_master_rpc_address_env = client.V1EnvVar(name='FLINK_JOB_MASTER_RPC_ADDRESS',
                                                       value="flink-job-cluster-{}-svc".format(job.uuid))

    job_master_container_image = None
    if 'flink_ai_flow_base_image' in GLOBAL_MASTER_CONFIG:
        job_master_container_image = GLOBAL_MASTER_CONFIG['flink_ai_flow_base_image']
    if job.job_config.image is not None:
        job_master_container_image = job.job_config.image

    if job_master_container_image is None:
        raise Exception("flink_ai_flow_base_image not set")

    job_master_container = client.V1Container(name='flink-job-master-{}'.format(job.uuid),
                                              image=job_master_container_image,
                                              image_pull_policy='Always',
                                              ports=[rpc_container_port, blob_container_port, query_container_port,
                                                     ui_container_port],
                                              command=['/docker-entrypoint.sh'],
                                              args=job_master_args_default,
                                              volume_mounts=[volume_mount, flink_config_volume_mount],
                                              env=[workflow_id_env,
                                                   execution_config_env,
                                                   flink_job_master_rpc_address_env,
                                                   entry_module_path_env,
                                                   language_type_env])

    try:
        jm_resources = job.job_config.resources['jobmanager']
        job_master_container.resources = client.V1ResourceRequirements(requests=jm_resources)
    except KeyError:
        pass

    init_args_default = [str(job.job_config.properties), str(job.job_context.workflow_execution_id),
                         job.job_config.project_path, mount_path]
    init_container = client.V1Container(name='init-container',
                                        image=GLOBAL_MASTER_CONFIG['ai_flow_base_init_image'],
                                        image_pull_policy='Always', command=["python", "/app/download.py"],
                                        args=init_args_default, volume_mounts=[volume_mount])
    volume = client.V1Volume(name='download-volume')

    # flink_conf.yaml config map volume
    config_name = "flink-config-{}".format(job.uuid)
    key_to_path_list = []
    key_to_path_list.append(client.V1KeyToPath(key="flink-conf.yaml", path="flink-conf.yaml"))
    key_to_path_list.append(client.V1KeyToPath(key="log4j.properties", path="log4j.properties"))
    key_to_path_list.append(client.V1KeyToPath(key="log4j-cli.properties", path="log4j-cli.properties"))
    flink_config_volume = client.V1Volume(name="flink-config-volume",
                                          config_map=client.V1ConfigMapVolumeSource(name=config_name,
                                                                                    items=key_to_path_list))
    pod_spec = client.V1PodSpec(restart_policy='Never', containers=[job_master_container],
                                init_containers=[init_container],
                                volumes=[volume, flink_config_volume])
    labels = {'app': 'flink', 'component': 'job-cluster-' + str(job.uuid)}
    object_meta = client.V1ObjectMeta(labels=labels,
                                      annotations={ANNOTATION_WATCHED: 'True', ANNOTATION_JOB_ID: str(job.instance_id),
                                                   ANNOTATION_WORKFLOW_ID: str(job.job_context.workflow_execution_id),
                                                   ANNOTATION_JOB_UUID: str(job.uuid)})
    template_spec = client.V1PodTemplateSpec(metadata=object_meta,
                                             spec=pod_spec)
    job_spec = client.V1JobSpec(template=template_spec, backoff_limit=0)
    object_meta = client.V1ObjectMeta(labels=labels, name=generate_job_name(job))
    job = client.V1Job(metadata=object_meta, spec=job_spec, api_version='batch/v1', kind='Job')
    return job


def get_task_manager_boilerplate(job: KubernetesFlinkJob) -> client.V1Deployment:
    from ai_flow.application_master.master import GLOBAL_MASTER_CONFIG
    dep_resource_metadata = client.V1ObjectMeta(
        name='flink-task-manager-' + str(job.uuid))

    mount_path = '/opt/ai-flow/project'
    volume_mount = client.V1VolumeMount(name='download-volume', mount_path=mount_path)
    flink_config_volume_mount = client.V1VolumeMount(name="flink-config-volume", mount_path="/opt/flink/conf")
    init_args_default = [str(job.job_config.properties), str(job.job_context.workflow_execution_id),
                         job.job_config.project_path, mount_path]

    init_container = client.V1Container(name='init-container',
                                        image=GLOBAL_MASTER_CONFIG['ai_flow_base_init_image'],
                                        image_pull_policy='Always',
                                        command=["python", "/app/download.py"],
                                        args=init_args_default,
                                        volume_mounts=[volume_mount, flink_config_volume_mount])
    volume = client.V1Volume(name='download-volume')

    task_manager_args = ["task-manager", "-Djobmanager.rpc.address=" +
                         'flink-job-cluster-{}-svc'.format(job.uuid)]

    try:
        flink_conf = job.job_config.flink_conf
        for key, value in flink_conf.items():
            task_manager_args.extend(["-D{}={}".format(key, value)])
    except KeyError:
        pass

    workflow_id_env = client.V1EnvVar(name='WORKFLOW_ID', value=str(job.job_context.workflow_execution_id))
    execution_config_env = client.V1EnvVar(name='CONFIG_FILE_NAME', value=job.config_file)

    # flink_conf.yaml config map volume
    config_name = "flink-config-{}".format(job.uuid)
    key_to_path_list = []
    key_to_path_list.append(client.V1KeyToPath(key="flink-conf.yaml", path="flink-conf.yaml"))
    key_to_path_list.append(client.V1KeyToPath(key="log4j.properties", path="log4j.properties"))
    key_to_path_list.append(client.V1KeyToPath(key="log4j-cli.properties", path="log4j-cli.properties"))
    flink_config_volume = client.V1Volume(name="flink-config-volume",
                                          config_map=client.V1ConfigMapVolumeSource(name=config_name,
                                                                                    items=key_to_path_list))

    task_manager_container_image = None
    if 'flink_ai_flow_base_image' in GLOBAL_MASTER_CONFIG:
        task_manager_container_image = GLOBAL_MASTER_CONFIG['flink_ai_flow_base_image']
    try:
        if job.job_config.image is not None:
            task_manager_container_image = job.job_config.image
    except KeyError:
        pass
    if task_manager_container_image is None:
        raise Exception("flink_ai_flow_base_image not set")

    tm_container = client.V1Container(
        name='flink-task-manager-' + str(job.uuid),
        image=task_manager_container_image,
        command=['/docker-entrypoint.sh'],
        args=task_manager_args,
        env=[workflow_id_env, execution_config_env],
        volume_mounts=[volume_mount]
    )

    try:
        tm_resource = job.job_config.resources['taskmanager']
        tm_container.resources = client.V1ResourceRequirements(requests=tm_resource)
    except KeyError:
        pass

    containers = [tm_container]
    labels = {'app': 'flink', 'component': 'task-manager-' + str(job.uuid)}
    pod_template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels=labels),
        spec=client.V1PodSpec(containers=containers, init_containers=[init_container],
                              volumes=[volume, flink_config_volume])
    )

    labels = {'app': 'flink', 'component': 'task-manager-' + str(job.uuid)}
    deployment_spec = client.V1DeploymentSpec(replicas=job.job_config.parallelism, template=pod_template,
                                              selector={'matchLabels': labels})
    dep_resource = client.V1Deployment(api_version='extensions/v1beta1', kind='Deployment', spec=deployment_spec,
                                       metadata=dep_resource_metadata)
    return dep_resource


def get_flink_conf_config_map(job: KubernetesFlinkJob) -> client.V1ConfigMap:
    flink_conf_map = {}
    flink_conf_map["jobmanager.rpc.address"] = "flink-job-cluster-{}-svc".format(job.uuid)
    flink_conf_map["taskmanager.numberOfTaskSlots"] = 2
    flink_conf_map["blob.server.port"] = 6124
    flink_conf_map["jobmanager.rpc.port"] = 6123
    flink_conf_map["taskmanager.rpc.port"] = 6122
    flink_conf_map["jobmanager.heap.size"] = "1024m"
    flink_conf_map["taskmanager.memory.process.size"] = "1024m"

    flink_conf_yaml = ''
    try:
        for key, value in job.job_config.flink_conf.items():
            flink_conf_map[key] = str(value)
    except KeyError:
        pass

    for key, value in flink_conf_map.items():
        flink_conf_yaml += '{}: {}\n'.format(key, value)

    log4j_properties = ""
    try:
        logging_confs = job.job_config.logging_conf
        for conf_k, conf_v in logging_confs.items():
            log4j_properties += "{}={}\n".format(conf_k, conf_v)
    except KeyError:
        pass
    logging.info(flink_conf_yaml)

    log4j_cli_properties = ""

    config_map_data = {}
    config_map_data["flink-conf.yaml"] = flink_conf_yaml
    config_map_data["log4j.properties"] = log4j_properties
    config_map_data["log4j-cli.properties"] = log4j_cli_properties

    config_name = "flink-config-{}".format(job.uuid)
    labels = {'app': 'flink', 'component': 'config-map-' + str(job.uuid)}
    config_map = client.V1ConfigMap(api_version="v1", kind="ConfigMap",
                                    metadata=client.V1ObjectMeta(name=config_name, labels=labels), data=config_map_data)
    return config_map
