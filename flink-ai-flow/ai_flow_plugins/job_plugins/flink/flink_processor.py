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
from typing import List, Dict, Text, Optional
from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo
from ai_flow.util import json_utils
from pyflink.dataset import ExecutionEnvironment
from pyflink.table import TableEnvironment, StatementSet, Table


class ExecutionContext(json_utils.Jsonable):
    """
    ExecutionContext contains job execution information(job_execution_info),
    AINode node configuration parameters(config), ExecutionEnvironment, TableEnvironment and StatementSet.
    ExecutionContext is passed as a parameter to the process function of FlinkPythonProcessor.
    """
    def __init__(self,
                 job_execution_info: JobExecutionInfo,
                 config: Dict,
                 execution_env: ExecutionEnvironment,
                 table_env: TableEnvironment,
                 statement_set: StatementSet
                 ):
        self._job_execution_info = job_execution_info
        self._config: Dict = config
        self._execution_env = execution_env
        self._table_env = table_env
        self._statement_set = statement_set

    @property
    def job_execution_info(self) -> JobExecutionInfo:
        return self._job_execution_info

    @property
    def name(self):
        return self._config['name']

    @property
    def node_type(self):
        return self._config['node_type']

    @property
    def config(self) -> Dict:
        return self._config

    @property
    def execution_env(self) -> ExecutionEnvironment:
        return self._execution_env

    @property
    def table_env(self) -> TableEnvironment:
        return self._table_env

    @property
    def statement_set(self) -> StatementSet:
        return self._statement_set


class FlinkPythonProcessor(object):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def process(self, execution_context: ExecutionContext, input_list: List[Table] = None) -> List[Table]:
        """
        Process method for user-defined function. User write their logic in this method.
        """
        pass

    def setup(self, execution_context: ExecutionContext):
        """
        Setup method for user-defined function. It can be used as a preparation stage before the process function.
        By default, this method does nothing.
        """
        pass

    def close(self, execution_context: ExecutionContext):
        """
        Close method for user-defined function. It can be used as a cleanup phase after the process function.
        By default, this method does nothing.
        """
        pass


class FlinkJavaProcessor(object):
    """
    FlinkJavaProcessor is the processor of flink java jobs.
    """
    def __init__(self,
                 entry_class: Optional[Text],
                 main_jar_file: Text,
                 args: List[Text] = None) -> None:
        """
        :param entry_class: Flink job entry class.
        :param main_jar_file: Flink job jar package name.
        :param args: The args are user-defined parameters.
        """
        super().__init__()
        self.entry_class: Text = entry_class
        self.main_jar_file: Text = main_jar_file
        self.args = args
