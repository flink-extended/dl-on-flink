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
from ai_flow.project.project_config import ProjectConfig
from ai_flow.context.job_context import set_current_job_name
from ai_flow.context.project_context import init_project_config
from ai_flow.context.workflow_config_loader import init_workflow_config
from ai_flow.runtime.job_runtime_env import JobRuntimeEnv


def init_job_runtime_context(job_runtime_env: JobRuntimeEnv):
    """
    When running the ai flow job,
    you need to call this function to initialize the project, workflow and job environment information.
    This function has three functions:
    1. Init project configuration
    2. Init workflow configuration.
    3. Set current job's name.
    """
    init_project_config(job_runtime_env.project_config_file)
    init_workflow_config(job_runtime_env.workflow_config_file)
    set_current_job_name(job_runtime_env.job_name)
