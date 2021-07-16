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
from abc import abstractmethod
from typing import List, Dict
from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo
from ai_flow.util import json_utils


class ExecutionContext(json_utils.Jsonable):
    """
    ExecutionContext contains job execution information(job_execution_info)
    and AINode node configuration parameters(config).
    ExecutionContext is passed as a parameter to the process function of PythonProcessor.
    """
    def __init__(self,
                 job_execution_info: JobExecutionInfo,
                 config: Dict):
        self._job_execution_info = job_execution_info
        self._config: Dict = config

    @property
    def job_execution_info(self) -> JobExecutionInfo:
        """
        :return: The job execution information
        """
        return self._job_execution_info

    @property
    def name(self):
        return self._config['name']

    @property
    def node_type(self):
        return self._config['node_type']

    @property
    def config(self) -> Dict:
        """
        :return: The AINode node configuration parameters.
        """
        return self._config


class PythonProcessor(object):
    """
    PythonProcessor is the processor corresponding to the python job.
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        """
        Process method for user-defined function. User write their logic in this method.
        :param execution_context: The execution_context contains job execution information(job_execution_info)
        and AINode node configuration parameters(config).
        :param input_list: The input data list of the processor.
        :return The output of the processor.
        """
        pass

    def setup(self, execution_context: ExecutionContext):
        """
        Setup method for user-defined function. It can be used as a preparation stage before the process function.
        """
        pass

    def close(self, execution_context: ExecutionContext):
        """
        Close method for user-defined function. It can be used as a cleanup phase after the process function.
        """
        pass
