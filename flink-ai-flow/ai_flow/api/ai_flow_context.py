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
import copy
from contextlib import contextmanager
from typing import Text, Union

from ai_flow.workflow.job import BaseJobConfig
from ai_flow.workflow.workflow_config import WorkFlowConfig, load_workflow_config, GLOBAL_CONFIG_KEY

ENGINE_NAME = "engine_name"
NONE_ENGINE = None

JOB_CONFIG = "__job_config__"
NONE_CONFIG = BaseJobConfig()


class AFJobContext(object):
    def __init__(self, config: BaseJobConfig) -> None:
        self.global_config: BaseJobConfig = BaseJobConfig(platform="local", engine="python")
        self.global_workflow_config: WorkFlowConfig = WorkFlowConfig()
        self.job_config: BaseJobConfig = config
        self.global_depth = 0
        self.job_depth = 0

    def merge_config(self) -> BaseJobConfig:
        real_config = copy.deepcopy(self.job_config)
        if self.global_config is None:
            return real_config

        if real_config.platform is None and self.global_config.platform is not None:
            real_config.platform = self.global_config.platform
        if real_config.engine is None and self.global_config.engine is not None:
            real_config.engine = self.global_config.engine
        if real_config.project_path is None and self.global_config.project_path is not None:
            real_config.project_path = self.global_config.project_path
        if self.global_config.properties is not None:
            for key, value in self.global_config.properties.items():
                if key not in real_config.properties:
                    real_config.properties[key] = value
        return real_config


__default_af_job_context = AFJobContext(config=NONE_CONFIG)


@contextmanager
def engine(name: Text):
    """
    Set the specific engine as current context with af.engine().

    :param name: Name of engine. It now supports python, cmd_line or flink.
    :return: None.
    """
    old_job_config = __default_af_job_context.job_config
    __default_af_job_context.job_config = BaseJobConfig(engine=name)
    try:
        __default_af_job_context.job_depth += 1
        if __default_af_job_context.job_depth > 1:
            raise Exception("job_config can not nesting")
        yield
    finally:
        __default_af_job_context.job_config = old_job_config
        __default_af_job_context.job_depth -= 1


@contextmanager
def config(config: Union[BaseJobConfig, Text, str]):
    """
    Set the specific job config as current context with af.config().

    :param config: Job config.
    """
    if isinstance(config, BaseJobConfig):
        current_config = config
    else:
        workflow_config = __default_af_job_context.global_workflow_config
        current_config = workflow_config.job_configs[config]

    old_job_config = __default_af_job_context.job_config
    __default_af_job_context.job_config = current_config
    __default_af_job_context.job_depth += 1
    if __default_af_job_context.job_depth > 1:
        raise Exception("job_config can not nesting")
    try:
        yield __default_af_job_context.job_config
    finally:
        __default_af_job_context.job_config = old_job_config
        __default_af_job_context.job_depth -= 1


@contextmanager
def global_config(global_config: BaseJobConfig):
    """
    Set the specific config as global context with af.global_config()

    :param global_config: Global job config.
    """
    old_global_config = __default_af_job_context.global_config
    __default_af_job_context.global_config = global_config
    __default_af_job_context.global_depth += 1
    if __default_af_job_context.global_depth > 1:
        raise Exception("global_config can not nesting")

    try:
        yield __default_af_job_context.global_config
    finally:
        __default_af_job_context.global_config = old_global_config
        __default_af_job_context.global_depth -= 1


@contextmanager
def global_config_file(config_path: Text):
    """
     Set the specific config file as global context with af.global_config_file()

    :param config_path: Path to the config file.
    """
    workflow_config: WorkFlowConfig = load_workflow_config(config_path)
    old_global_workflow_config = __default_af_job_context.global_workflow_config
    __default_af_job_context.global_workflow_config = workflow_config
    global_config_value = None
    if GLOBAL_CONFIG_KEY in workflow_config.job_configs:
        global_config_value = workflow_config.job_configs[GLOBAL_CONFIG_KEY]

    old_global_config = __default_af_job_context.global_config
    __default_af_job_context.global_config = global_config_value
    __default_af_job_context.global_depth += 1
    if __default_af_job_context.global_depth > 1:
        raise Exception("global_config can not nesting")

    try:
        yield __default_af_job_context.global_config
    finally:
        __default_af_job_context.global_workflow_config = old_global_workflow_config
        __default_af_job_context.global_config = old_global_config
        __default_af_job_context.global_depth -= 1


def default_af_job_context() -> AFJobContext:
    return __default_af_job_context

