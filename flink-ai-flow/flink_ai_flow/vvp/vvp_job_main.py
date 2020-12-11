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
import importlib
import sys
import os
import logging
from ai_flow.common import serialization_utils
from ai_flow.api.configuration import set_default_project_config
from flink_ai_flow.vvp_flink_job import VVPJob
from flink_ai_flow.vvp_flink_job import VVPFlinkJobPlugin, VVPJobHandler


def read_config_file(file_path):
    with open(file_path, 'rb') as f:
        config_bytes = f.read()
        return serialization_utils.deserialize(config_bytes)


def run_project(project_path, config_file):
    vvp_job: VVPJob = read_config_file(config_file)
    set_default_project_config(vvp_job.job_context.project_config)
    vvp_plugin = VVPFlinkJobPlugin()
    handler: VVPJobHandler = vvp_plugin.submit_job(vvp_job)
    # save vvp deployment_id
    workflow_dir = '{}/temp/vvp/{}'.format(vvp_job.job_config.project_path,
                                           str(vvp_job.job_context.workflow_execution_id))
    os.makedirs(workflow_dir, exist_ok=True)
    with open('{}/{}'.format(workflow_dir, vvp_job.instance_id), 'w') as f:
        logging.info('workflow execution id: {}, job instance: {}, deployment job id: {} vvp job id: {}'.format(
            vvp_job.job_context.workflow_execution_id,
            vvp_job.instance_id, handler.vvp_deployment_id, handler.vvp_job_id))
        f.write(handler.vvp_deployment_id)
    # wait until job finished
    vvp_plugin.wait_until_deployment_finished(deployment_id=handler.vvp_deployment_id, job=vvp_job)


if __name__ == '__main__':

    l_project_path, l_config_file, l_entry_module_path \
        = sys.argv[1], sys.argv[2], sys.argv[3]
    mdl = importlib.import_module(l_entry_module_path)
    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
    else:
        names = [x for x in mdl.__dict__ if not x.startswith("_")]
    globals().update({k: getattr(mdl, k) for k in names})

    run_project(l_project_path, l_config_file)
