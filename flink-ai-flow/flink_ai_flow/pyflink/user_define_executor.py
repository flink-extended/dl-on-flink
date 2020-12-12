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
from typing import List
from abc import ABC, abstractmethod
from ai_flow.graph.ai_node import AINode
from ai_flow.workflow.job_context import JobContext
from ai_flow.udf.function_context import FunctionContext
from ai_flow.meta.example_meta import ExampleMeta
from ai_flow.graph.ai_nodes.example import Example
from pyflink.table.table import Table
from pyflink.dataset import ExecutionEnvironment
from pyflink.table import TableConfig, BatchTableEnvironment, TableEnvironment, StatementSet


class FlinkFunctionContext(FunctionContext):

    def __init__(self, exec_env, t_env: TableEnvironment, statement_set: StatementSet,
                 node_spec: AINode, job_context: JobContext) -> None:
        super().__init__(node_spec, job_context)
        self.exec_env = exec_env
        self.t_env = t_env
        self.statement_set = statement_set
        if isinstance(node_spec, Example):
            self.example_meta = node_spec.example_meta
        else:
            self.example_meta = None

    def get_exec_env(self):
        return self.exec_env

    def get_table_env(self) -> TableEnvironment:
        return self.t_env

    def get_statement_set(self) -> StatementSet:
        return self.statement_set

    def get_example_meta(self) -> ExampleMeta:
        return self.example_meta


class Executor(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def execute(self, function_context: FlinkFunctionContext, input_list: List[Table]) -> List[Table]:
        pass

    def setup(self, function_context: FlinkFunctionContext):
        pass

    def close(self, function_context: FlinkFunctionContext):
        pass


class SourceExecutor(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def execute(self, function_context: FlinkFunctionContext) -> Table:
        pass

    def setup(self, function_context: FlinkFunctionContext):
        pass

    def close(self, function_context: FlinkFunctionContext):
        pass


class SinkExecutor(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def execute(self, function_context: FlinkFunctionContext, input_table: Table) -> None:
        pass

    def setup(self, function_context: FlinkFunctionContext):
        pass

    def close(self, function_context: FlinkFunctionContext):
        pass


class TableEnvCreator(ABC):

    def create_table_env(self):
        exec_env = ExecutionEnvironment.get_execution_environment()
        exec_env.set_parallelism(1)
        t_config = TableConfig()
        t_env = BatchTableEnvironment.create(exec_env, t_config)
        statement_set = t_env.create_statement_set()
        return exec_env, t_env, statement_set
