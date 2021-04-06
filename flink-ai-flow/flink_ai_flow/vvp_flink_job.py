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
from typing import Text, Dict, Any
import uuid
import os
import sys
import logging

from ai_flow.airflow.dag_generator import job_name_to_task_id
from ai_flow.project.blob_manager import BlobManagerFactory
from ai_flow.common.json_utils import dumps, Jsonable
from ai_flow.plugins.job_plugin import AISubGraph, ProjectDesc, JobContext, \
    AbstractJobConfig, AbstractJob, AbstractEngine
from ai_flow.meta.job_meta import ExecutionMode
from ai_flow.plugins.job_plugin import AbstractJobPlugin
from ai_flow.plugins.platform import AbstractPlatform
from flink_ai_flow.vvp.vvp_restful_api import default_flink_image_info, default_resources, default_flink_config, \
    default_logging, default_restore_strategy, default_upgrade_strategy, default_kubernetes, VVPRestful
from flink_ai_flow.flink_engine import FlinkEngine
from flink_ai_flow.vvp_platform import VVPJobHandler, VVPPlatform
from flink_ai_flow import version
from ai_flow.common import serialization_utils
from airflow.operators.bash_operator import BashOperator


# class VVPJobConfig(AbstractJobConfig):
#     @staticmethod
#     def from_dict(data: Dict, config) -> object:
#         AbstractJobConfig.from_dict(data, config)
#         config.base_url = data['base_url']
#         config.namespace = data['namespace']
#         config.token = data['token']
#         config.deployment_name = data['deployment_name']
#         config.jar_path = data.get('jar_path', None)
#         config.entry_class = data.get('entry_class', None)
#         config.main_args = data.get('main_args', None)
#         config.flink_image_info = data.get('flink_image_info', None)
#         config.parallelism = data.get('parallelism', 1)
#         config.resources = data.get('resources', None)
#         config.logging = data.get('logging', None)
#         config.flink_config = data.get('flink_config')
#         config.upgrade_strategy = data.get('upgrade_strategy', default_upgrade_strategy)
#         config.restore_strategy = data.get('restore_strategy', default_restore_strategy)
#         config.job_type = data.get('job_type', 'java')
#         config.addition_dependencies = data.get('addition_dependencies', [])
#         config.kubernetes = data.get('kubernetes', {})
#         config.spec = data.get('spec', None)
#         return config
#
#     def __init__(self,
#                  base_url: Text = None,
#                  namespace: Text = None,
#                  jar_path: Text = None,
#                  deployment_name: Text = None,
#                  entry_class: Text = "",
#                  main_args: Text = "",
#                  token: Text = None,
#                  flink_image_info=default_flink_image_info,
#                  parallelism=1,
#                  resources=default_resources,
#                  flink_config=default_flink_config,
#                  logging=default_logging,
#                  upgrade_strategy=default_upgrade_strategy,
#                  restore_strategy=default_restore_strategy,
#                  job_type='java',
#                  addition_dependencies=list(),
#                  kubernetes=default_kubernetes,
#                  spec=None,
#                  properties: Dict[Text, Jsonable] = None) -> None:
#         super().__init__('vvp', 'flink', properties)
#         self.base_url = base_url
#         self.namespace = namespace
#         self.jar_path = jar_path
#         self.deployment_name = deployment_name
#         self.token = token
#         self.flink_image_info = flink_image_info
#         self.parallelism = parallelism
#         self.resources = resources
#         self.flink_config = flink_config
#         self.logging = logging
#         self.entry_class = entry_class
#         self.main_args = main_args
#         self.job_type = job_type
#         self.restore_strategy = restore_strategy
#         self.upgrade_strategy = upgrade_strategy,
#         self.addition_dependencies = addition_dependencies
#         self.kubernetes = kubernetes
#         self.spec = spec

class VVPJobConfig(AbstractJobConfig):
    @staticmethod
    def from_dict(data: Dict, config) -> object:
        AbstractJobConfig.from_dict(data, config)
        config.namespace = data['namespace']
        config.deployment_id = data['deployment_id']
        if 'token' not in data:
            config.token = None
        else:
            config.token = data['token']
        return config

    def __init__(self,
                 namespace: Text = None,
                 deployment_id: Text = None,
                 token: Text = None,
                 properties: Dict[Text, Jsonable] = None) -> None:
        super().__init__('vvp', 'flink', properties)
        self.namespace = namespace
        self.deployment_name = deployment_id
        self.token = token


# class VVPJob(AbstractJob):
#     def __init__(self,
#                  job_context: JobContext,
#                  job_config: VVPJobConfig) -> None:
#         super().__init__(job_context, job_config)
#         self.vvp_deployment_id: Text = None
#         self.vvp_job_id: Text = None
#         self.vvp_restful: VVPRestful \
#             = VVPRestful(base_url=job_config.base_url, namespace=job_config.namespace, token=job_config.token)
#         self.config_file = None
#         self.exec_cmd = None
class VVPJob(AbstractJob):
    def __init__(self,
                 job_context: JobContext,
                 job_config: VVPJobConfig) -> None:
        super().__init__(job_context, job_config)


class VVPFlinkJobPlugin(AbstractJobPlugin):

    def __init__(self) -> None:
        super().__init__()

    def generate(self, sub_graph: AISubGraph, project_desc: ProjectDesc) -> VVPJob:
        if sub_graph.config.exec_mode == ExecutionMode.BATCH:
            flink_context = JobContext(ExecutionMode.BATCH)
        else:
            flink_context = JobContext(ExecutionMode.STREAM)
        flink_context.project_config = project_desc.project_config
        job_config: VVPJobConfig = sub_graph.config
        job = VVPJob(job_context=flink_context, job_config=job_config)
        return job

    def generate_job_resource(self, job: VVPJob) -> None:
        """
        Generate flink job resource.

        :param job: Local flink job.
        """
        project_path = job.job_config.project_path
        if project_path is None:
            project_path = "/tmp"
        project_path_temp = project_path + "/temp"
        if not os.path.exists(project_path_temp):
            os.mkdir(project_path_temp)
        execution_config_file = project_path_temp + '/job_execution_config_' + str(
            uuid.uuid4()) + "_" + job.instance_id

        job.config_file = execution_config_file
        with open(execution_config_file, 'wb') as f:
            f.write(serialization_utils.serialize(job))

        script_path = version.vvp_job_main_file
        entry_module_path = job.job_config.project_desc.project_config['entry_module_path']
        python3_location = sys.executable
        cmd = [python3_location, script_path, job.job_config.project_path,
               execution_config_file, entry_module_path]
        job.exec_cmd = ' '.join(cmd)
        logging.info(job.exec_cmd)

    def submit_job(self, job: VVPJob) -> VVPJobHandler:
        blob_manager = BlobManagerFactory.get_blob_manager(job.job_config.properties)
        if job.job_config.project_path is not None:
            downloaded_blob_path = blob_manager.download_blob(job.instance_id, job.job_config.project_path)

        vvp_config: VVPJobConfig = job.job_config
        dp_id, job_id = job.vvp_restful.submit_job(name=job.job_config.deployment_name,
                                                   artifact_path=job.job_config.jar_path,
                                                   entry_class=job.job_config.entry_class,
                                                   main_args=job.job_config.main_args,
                                                   addition_dependencies=job.job_config.addition_dependencies,
                                                   flink_image_info=vvp_config.flink_image_info,
                                                   parallelism=vvp_config.parallelism,
                                                   resources=vvp_config.resources,
                                                   flink_config=vvp_config.flink_config,
                                                   logging=vvp_config.logging,
                                                   kubernetes=vvp_config.kubernetes,
                                                   upgrade_strategy=job.job_config.upgrade_strategy,
                                                   restore_strategy=job.job_config.restore_strategy,
                                                   spec=job.job_config.spec
                                                   )
        job.vvp_deployment_id = dp_id
        job.vvp_restful.start_deployment(job.vvp_deployment_id)
        job.vvp_job_id = job_id

        return VVPJobHandler(vvp_restful=job.vvp_restful,
                             vvp_job_id=job_id,
                             vvp_deployment_id=dp_id,
                             job_instance_id=job.instance_id,
                             job_uuid=job.uuid,
                             workflow_id=job.job_context.workflow_execution_id)

    def stop_job(self, job: VVPJob):
        job.vvp_restful.sync_stop_deployment(job.vvp_deployment_id)

    def cleanup_job(self, job: AbstractJob):
        pass

    def platform(self) -> type(AbstractPlatform):
        return VVPPlatform

    def job_type(self) -> type(AbstractJob):
        return VVPJob

    def job_config_type(self) -> type(AbstractJobConfig):
        return VVPJobConfig

    def engine(self) -> type(AbstractEngine):
        return FlinkEngine

    def generate_operator_code(self) -> Text:
        return "from airflow.operators.vvp import VVPOperator\n"

    def generate_code(self, op_index, job):
        if job.job_config.token is None:
            VVP_OPERATOR = """op_{0} = VVPOperator(task_id='{1}', namespace='{2}', deployment_id='{3}', token=None, dag=dag)\n"""
            return VVP_OPERATOR.format(op_index,
                                       job_name_to_task_id(job.job_name),
                                       job.job_config.namespace,
                                       job.job_config.deployment_id)
        else:
            VVP_OPERATOR = """op_{0} = VVPOperator(task_id='{1}', namespace='{2}', deployment_id='{3}', token='{4}', dag=dag)\n"""
            return VVP_OPERATOR.format(op_index,
                                       job_name_to_task_id(job.job_name),
                                       job.job_config.namespace,
                                       job.job_config.deployment_id,
                                       job.job_config.token)

    def wait_until_deployment_finished(self, deployment_id, job: VVPJob):
        job.vvp_restful.wait_deployment_state(deployment_id, state=set(['CANCELLED', 'FINISHED']), interval=60)
