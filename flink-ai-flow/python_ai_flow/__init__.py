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
from python_ai_flow.local_python_job import LocalPythonJobPlugin, get_default_local_python_job_plugin
from python_ai_flow.kubernetes_python_job import KubernetesPythonJobPlugin, get_default_k8s_python_job_plugin
from python_ai_flow import example_components
from python_ai_flow.user_define_funcs import Executor, ExampleExecutor, FunctionContext

register_job_plugin(get_default_local_python_job_plugin())
register_job_plugin(get_default_k8s_python_job_plugin())
