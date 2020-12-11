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
from flink_ai_flow.api.ops import *
from ai_flow.plugins.job_plugin import register_job_plugin
from ai_flow.plugins.platform import register_platform
from flink_ai_flow.local_flink_job import LocalFlinkJobPlugin, LocalFlinkJobConfig
from flink_ai_flow.kubernetes_flink_job import KubernetesFlinkJobPlugin, KubernetesFlinkJobConfig
from flink_ai_flow.flink_executor import FlinkJavaExecutor, FlinkPythonExecutor
from flink_ai_flow.vvp_platform import VVPPlatform
from flink_ai_flow.vvp_flink_job import VVPFlinkJobPlugin, VVPJobConfig
from flink_ai_flow.vvp import default_flink_config, default_logging, default_resources, default_flink_image_info


register_job_plugin(LocalFlinkJobPlugin())
register_job_plugin(KubernetesFlinkJobPlugin())
register_platform(VVPPlatform)
register_job_plugin(VVPFlinkJobPlugin())
