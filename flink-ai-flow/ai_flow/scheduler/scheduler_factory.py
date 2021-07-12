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

from ai_flow.common.module_load import import_string
from ai_flow.plugin_interface.scheduler_interface import Scheduler


class SchedulerFactory(object):
    """
    SchedulerFactory creates scheduler() based on configuration information.
    """
    @classmethod
    def create_scheduler(cls, class_name, config: Dict) -> Scheduler:
        """
        :param class_name: The class name of a scheduler(ai_flow.plugin_interface.scheduler_interface.Scheduler)
        :param config: The configuration of the scheduler.
        """
        class_object = import_string(class_name)
        return class_object(config)
