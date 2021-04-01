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

from typing import Any, Dict, List, Optional

from airflow.configuration import conf
from airflow.executors.base_executor import BaseExecutor, CommandType
from airflow.models.taskinstance import TaskInstance, TaskInstanceKey


class VVPExecutor(BaseExecutor):
    """
    This executor is meant for debugging purposes. It can be used with SQLite.

    It executes one task instance at time. Additionally to support working
    with sensors, all sensors ``mode`` will be automatically set to "reschedule".
    """

    def __init__(self):
        super().__init__()
        self.tasks_to_run: List[TaskInstance] = []
        # Place where we keep information for task instance raw run
        self.tasks_params: Dict[TaskInstanceKey, Dict[str, Any]] = {}
        self.fail_fast = conf.getboolean("debug", "fail_fast")

    def _start_task_instance(self, key: TaskInstanceKey):
        super()._start_task_instance(key)

    def _stop_related_process(self, ti: TaskInstance) -> bool:
        pass

    def _stop_task_instance(self, key: TaskInstanceKey) -> bool:
        return super()._stop_task_instance(key)

    def execute_async(self, key: TaskInstanceKey, command: CommandType, queue: Optional[str] = None,
                      executor_config: Optional[Any] = None) -> None:
        pass

    def end(self) -> None:
        pass

    def terminate(self):
        pass



