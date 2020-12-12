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
from ai_flow.plugins.job_plugin import register_job_plugin
from ai_flow.plugins.platform import register_platform
from ai_flow.plugins.local_platform import LocalPlatform
from ai_flow.plugins.kubernetes_platform import KubernetesPlatform
from ai_flow.plugins.local_cmd_job_plugin import LocalCMDJobPlugin
from ai_flow.plugins.kubernetes_cmd_job_plugin import KubernetesCMDJobPlugin
from ai_flow.plugins.local_dummy_job_plugin import LocalDummyJobPlugin


register_platform(LocalPlatform)
register_platform(KubernetesPlatform)

register_job_plugin(LocalCMDJobPlugin())
register_job_plugin(KubernetesCMDJobPlugin())
register_job_plugin(LocalDummyJobPlugin())

