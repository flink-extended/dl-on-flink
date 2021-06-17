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
from typing import Text
from kubernetes import client
import os
import logging
from ai_flow.plugins.kubernetes_platform import DEFAULT_PROJECT_PATH, DEFAULT_NAMESPACE


def create_init_container(job, volume_mount, job_container):
    from ai_flow.application_master.server_runner import GLOBAL_MASTER_CONFIG
    logging.info('Kubernetes GLOBAL_MASTER_CONFIG {}'.format(GLOBAL_MASTER_CONFIG))
    init_args_default = [str(job.job_config.project_desc.project_config),
                         str(job.job_context.workflow_execution_id),
                         job.job_config.project_path,
                         DEFAULT_PROJECT_PATH]
    container \
        = client.V1Container(name='init-container',
                             image=GLOBAL_MASTER_CONFIG['ai_flow_base_init_image'],
                             image_pull_policy='Always',
                             command=["python", "/app/download.py"],
                             args=init_args_default, volume_mounts=[volume_mount])
    volume = client.V1Volume(name='download-volume')
    pod_spec = client.V1PodSpec(restart_policy='Never', containers=[job_container],
                                init_containers=[container],
                                volumes=[volume])
    return pod_spec


def get_container_working_dir(job) -> Text:
    project_dir_name = 'workflow_{}_project'.format(job.job_context.workflow_execution_id)
    user_project_dir_name = os.path.basename(job.job_config.project_desc.project_path)
    working_dir = "{}/{}/{}".format(DEFAULT_PROJECT_PATH, project_dir_name, user_project_dir_name)
    logging.info("working_dir {}".format(working_dir))
    return working_dir


def submit_job(job):
    batchV1 = client.BatchV1Api()
    batchV1.create_namespaced_job(namespace=DEFAULT_NAMESPACE, body=job)


def kill_job(name):
    batchV1 = client.BatchV1Api()
    response = batchV1.delete_namespaced_job(namespace=DEFAULT_NAMESPACE,
                                             name=name,
                                             body=client.V1DeleteOptions(
                                                 propagation_policy='Foreground',
                                                 grace_period_seconds=5))
