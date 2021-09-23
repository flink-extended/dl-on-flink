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
from typing import Dict

from ai_flow.common.configuration import AIFlowConfiguration
from ai_flow.plugin_interface.scheduler_interface import SchedulerConfig


class SchedulerServiceConfig(AIFlowConfiguration):

    def __init__(self, config: Dict):
        super().__init__()
        if config is None:
            raise Exception(
                'The `{}` option is not configured in the {} option. Please add it!'.format('scheduler_service',
                                                                                            'aiflow_server.yaml'))

        self['repository'] = '/tmp'
        if config.get('repository') is not None:
            self['repository'] = config.get('repository')
        scheduler_meta = SchedulerConfig(config.get('scheduler'))
        self['scheduler'] = scheduler_meta

    def repository(self):
        return self['repository']

    def set_repository(self, value):
        self['repository'] = value

    def scheduler(self):
        return self['scheduler']

    def set_scheduler(self, value):
        self['scheduler'] = value
