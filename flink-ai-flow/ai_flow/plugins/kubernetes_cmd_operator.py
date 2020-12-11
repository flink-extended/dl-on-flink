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
from airflow.models.baseoperator import BaseOperator
from ai_flow.plugins.kubernetes_cmd_job_plugin import KubernetesCMDJobPlugin
from ai_flow.plugins.k8s_util import kill_job
from ai_flow.common import json_utils
from ai_flow.plugins.kubernetes_platform import watch_k8s_job_status


class KubernetesCMDOperator(BaseOperator):

    def __init__(self, job, *args, **kwargs):
        super(KubernetesCMDOperator, self).__init__(*args, **kwargs)
        self.job = json_utils.loads(job)
        self.plugin = KubernetesCMDJobPlugin()

    def execute(self, context):
        self.plugin.submit_job(job=self.job)
        watch_k8s_job_status(job_name=self.plugin.generate_job_name(self.job))

    def on_kill(self):
        kill_job(self.plugin.generate_job_name(self.job))
