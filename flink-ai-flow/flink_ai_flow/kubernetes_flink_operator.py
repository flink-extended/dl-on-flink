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
from ai_flow.plugins.kubernetes_platform import watch_k8s_job_status
from airflow.models.baseoperator import BaseOperator
from flink_ai_flow.kubernetes_flink_job import KubernetesFlinkJobPlugin
from ai_flow.util import json_utils


class KubernetesFlinkOperator(BaseOperator):

    def __init__(self, job_file, *args, **kwargs):
        super(KubernetesFlinkOperator, self).__init__(*args, **kwargs)
        with open(file=job_file, mode='rt') as f:
            job = f.read()
            self.job = json_utils.loads(job)
        self.plugin = KubernetesFlinkJobPlugin()

    def execute(self, context):
        self.plugin.submit_job(job=self.job)
        watch_k8s_job_status(job_name=self.plugin.generate_job_name(self.job))

    def on_kill(self):
        self.plugin.cleanup_job(self.job)
