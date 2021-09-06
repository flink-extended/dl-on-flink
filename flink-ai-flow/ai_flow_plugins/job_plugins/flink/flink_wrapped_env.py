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
from typing import List, Text
from pyflink.table import StatementSet, TableEnvironment
from pyflink.table.table_environment import BatchTableEnvironment, StreamTableEnvironment
from pyflink.table.table_result import TableResult


class WrappedTableEnvironmentContext:
    """
    WrappedTableEnvironmentContext provides container to store extra information for WrappedTableEnvironment,
    including list of TableResult for each execution.
    It can help to provide these functions:
    - Lists the ids of the Flink jobs.
    - Waits for the execution result of the Flink job.
    """

    def __init__(self):
        self.execute_sql_results: List[TableResult] = []

    def add_execute_sql_result(self, result: TableResult):
        self.execute_sql_results.append(result)

    def get_job_ids(self) -> List[Text]:
        result = []
        for r in self.execute_sql_results:
            job_client = r.get_job_client()
            if job_client is not None:
                job_id = str(job_client.get_job_id())
                result.append(job_id)
        return result

    def wait_execution_results(self):
        for r in self.execute_sql_results:
            job_client = r.get_job_client()
            if job_client is not None:
                job_client.get_job_execution_result().result()


class WrappedTableEnvironment(TableEnvironment):
    """
    WrappedTableEnvironment overrides the following functions to collect information needed for 'flink_run_main.py':
    - execute_sql(self, stmt: str) -> TableResult
    - create_statement_set(self) -> 'WrappedStatementSet':
    """
    wrapped_context = WrappedTableEnvironmentContext()

    def execute_sql(self, stmt: str) -> TableResult:
        result = super().execute_sql(stmt)
        self.wrapped_context.add_execute_sql_result(result)
        return result

    def create_statement_set(self) -> 'WrappedStatementSet':
        _s_set = super().create_statement_set()
        s_set = WrappedStatementSet(_s_set._j_statement_set, _s_set._t_env)
        return s_set

    def wait_execution_results(self):
        self.wrapped_context.wait_execution_results()


class WrappedBatchTableEnvironment(BatchTableEnvironment, WrappedTableEnvironment):

    def __init__(self, j_tenv):
        super().__init__(j_tenv)

    @staticmethod
    def create_from(t_env: BatchTableEnvironment) -> 'WrappedBatchTableEnvironment':
        return WrappedBatchTableEnvironment(t_env._j_tenv)


class WrappedStreamTableEnvironment(StreamTableEnvironment, WrappedTableEnvironment):

    def __init__(self, j_tenv):
        super().__init__(j_tenv)

    @staticmethod
    def create_from(t_env: StreamTableEnvironment) -> 'WrappedStreamTableEnvironment':
        return WrappedStreamTableEnvironment(t_env._j_tenv)


class WrappedStatementSetContext:
    """
    WrappedStatementSetContext provides container to store extra information for WrappedStatementSet,
    including list of TableResult for each execution.
    It can help to provide these functions:
    - Lists the ids of the Flink jobs.
    - Waits for the execution result of the Flink job.
    - Decides whether 'StatementSet' needs to call 'execute()' method based on whether it contains 'execute_sql'.
    """

    def __init__(self):
        self.execute_results: List[TableResult] = []
        self.need_execute = False

    def add_execute_result(self, result: TableResult):
        self.execute_results.append(result)

    def get_job_ids(self) -> List[Text]:
        result = []
        for r in self.execute_results:
            job_client = r.get_job_client()
            if job_client is not None:
                job_id = str(job_client.get_job_id())
                result.append(job_id)
        return result

    def wait_execution_results(self):
        for r in self.execute_results:
            job_client = r.get_job_client()
            if job_client is not None:
                job_client.get_job_execution_result().result()


class WrappedStatementSet(StatementSet):
    """
    WrappedStatementSet overrides the following functions to collect information needed for 'flink_run_main.py':
    - execute(self) -> TableResult
    - add_insert_sql(self, stmt: str) -> 'StatementSet':
    """

    wrapped_context = WrappedStatementSetContext()

    def execute(self) -> TableResult:
        result = super().execute()
        self.wrapped_context.add_execute_result(result)
        self.wrapped_context.need_execute = False
        return result

    def add_insert_sql(self, stmt: str) -> 'StatementSet':
        result = super().add_insert_sql(stmt)
        self.wrapped_context.need_execute = True
        return result

    def add_insert(self, target_path, table, overwrite: bool = False) -> 'StatementSet':
        result = super().add_insert(target_path, table, overwrite=overwrite)
        self.wrapped_context.need_execute = True
        return result

    def wait_execution_results(self):
        self.wrapped_context.wait_execution_results()
