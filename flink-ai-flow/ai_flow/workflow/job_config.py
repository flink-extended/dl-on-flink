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
from ai_flow.meta.job_meta import ExecutionMode
from ai_flow.util.json_utils import Jsonable
from ai_flow.project.project_description import ProjectDesc
from ai_flow.common.registry import BaseRegistry
from typing import Text, Dict, Optional, Tuple, Union


class PeriodicConfig(Jsonable):
    """
    Set period semantics for job. Jobs with periodic semantics will restart at regular intervals.
    """
    def __init__(self, periodic_type: Text,
                 args: Union[Text, Dict[Text, Jsonable]] = None) -> None:
        """
        :param periodic_type: ``interval`` or ``cron``
        link apscheduler.schedulers.background.BackgroundScheduler add_job

        """
        super().__init__()
        self.periodic_type = periodic_type
        if args is None:
            args = {}
        self.args = args


class BaseJobConfig(Jsonable):
    """
    Base class for job config. It is used to set the basic job config.

    """
    def __init__(self, platform: Text = None, engine: Text = None, job_name: Text = None,
                 periodic_config: PeriodicConfig = None, exec_mode: Optional[ExecutionMode] = ExecutionMode.BATCH,
                 properties: Dict[Text, Jsonable] = None) -> None:
        """
        Set platform and engine in base job config.

        :param platform: Platform of the configured job. It can be local or kubernetes.
        :param engine: Engine of the configured job. It can be python, cmd_line flink or other available engine.
        :param job_name: Name of the configured job.
        :param properties: Properties of the configured job.
        """
        super().__init__()
        self.platform: Text = platform
        self.engine: Text = engine
        self.project_desc: ProjectDesc = ProjectDesc()
        self.project_path: Text = None
        self.project_local_path: Text = None
        if properties is None:
            self.properties: Dict[Text, Jsonable] = {}
        else:
            self.properties: Dict[Text, Jsonable] = properties
        self.properties['clean_job_resource'] = "True"
        self.periodic_config: PeriodicConfig = periodic_config
        self.exec_mode: Optional[ExecutionMode] = exec_mode
        self.job_name: Text = job_name

    def is_clean_job_resource(self) -> bool:
        if "clean_job_resource" in self.properties \
                and ("True" == self.properties['clean_job_resource'] or self.properties['clean_job_resource'] is True):
            return True
        else:
            return False

    def set_clean_job_resource(self):
        self.properties['clean_job_resource'] = "True"

    def unset_clean_job_resource(self):
        self.properties['clean_job_resource'] = "False"

    @staticmethod
    def from_dict(data: Dict, config) -> object:
        return dict_to_base_job_config(data, config)


def dict_to_periodic_config(data: Dict) -> Optional[PeriodicConfig]:
    if data is None:
        return None
    periodic_type = data['periodic_type']
    args = data.get('args', {})
    return PeriodicConfig(periodic_type=periodic_type, args=args)


def dict_to_base_job_config(data: Dict, job_config) -> BaseJobConfig:
    job_config.platform = data['platform']
    job_config.engine = data['engine']
    job_config.properties = data.get('properties', {})
    job_config.project_path = data.get('project_path', None)
    job_config.project_local_path = data.get('project_local_path', None)
    job_config.job_name = data.get('job_name', None)
    job_config.periodic_config = dict_to_periodic_config(data.get('periodic_config', None))
    job_config.exec_mode = ExecutionMode.value_of(data.get('exec_mode', ExecutionMode.BATCH.value))

    return job_config


class JobConfigRegistry(BaseRegistry):
    def register(self, key: Tuple, value: object):
        self.object_dict[key] = value

    def get_object(self, key: Tuple):
        return self.object_dict[key]


__default_job_config_registry = JobConfigRegistry()


def register_job_config(platform, engine, job_config_class):
    __default_job_config_registry.register(key=(platform, engine), value=job_config_class)


def get_default_job_config_registry() -> JobConfigRegistry:
    return __default_job_config_registry


def get_job_config_class(platform, engine):
    return get_default_job_config_registry().get_object((platform, engine))
