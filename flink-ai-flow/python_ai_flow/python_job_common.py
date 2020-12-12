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
from abc import ABC, abstractmethod
from typing import List, Dict, Text, Optional
from ai_flow.executor.executor import PythonObjectExecutor
from ai_flow.graph.ai_nodes.executable import ExecutableNode
from ai_flow.meta.example_meta import ExampleMeta
from ai_flow.common.registry import BaseRegistry
from ai_flow.graph.ai_node import AINode
from ai_flow.graph.ai_nodes import Example
from ai_flow.graph.edge import DataEdge
from ai_flow.common.json_utils import Jsonable
from ai_flow.workflow.job_context import JobContext
from ai_flow.udf.function_context import FunctionContext
from ai_flow.common.serialization_utils import deserialize
from python_ai_flow.user_define_funcs import Executor


class BaseComponent(ABC):
    def __init__(self, node: AINode, context: JobContext) -> None:
        self.node = node
        self.context = context

    @abstractmethod
    def batch_executor(self) -> Executor:
        pass

    @abstractmethod
    def stream_executor(self) -> Executor:
        pass


class ExecuteComponent(BaseComponent, ABC):
    class ExecuteExecutor(Executor):
        def __init__(self,
                     executor: PythonObjectExecutor) -> None:
            super().__init__()
            self.executor: Executor = deserialize(executor.python_object)
            if not isinstance(self.executor, Executor):
                raise Exception("python ai flow only support Executor class but config executor is {}"
                                .format(type(self.executor)))

        def setup(self, function_context: FunctionContext):
            self.executor.setup(function_context)

        def close(self, function_context: FunctionContext):
            self.executor.close(function_context)

        def execute(self, context: FunctionContext, args: List = None) -> List:
            return self.executor.execute(context, args)

    def __init__(self, node: AINode, context: JobContext) -> None:
        super().__init__(node, context)
        self.node: ExecutableNode = self.node

    def batch_executor(self) -> Executor:
        return ExecuteComponent.ExecuteExecutor(self.node.executor)

    def stream_executor(self) -> Executor:
        return ExecuteComponent.ExecuteExecutor(self.node.executor)


class BaseExampleComponent(ExecuteComponent, ABC):

    def __init__(self, node: AINode, context: JobContext) -> None:
        super().__init__(node, context)
        self.example_node: Example = self.node
        self.example_meta: ExampleMeta = self.example_node.example_meta
        self.is_source = self.example_node.is_source


class ExampleComponentRegistry(BaseRegistry):
    def __init__(self) -> None:
        super().__init__()
        self.object_dict: Dict[Text, BaseExampleComponent] = {}


# ai_nodes sort by call order
class RunGraph(Jsonable):
    def __init__(self) -> None:
        super().__init__()
        self.nodes: List[AINode] = []
        self.executor_bytes: List[bytes] = []
        self.dependencies: Dict[Text, List[DataEdge]] = {}


class RunArgs(object):
    def __init__(self,
                 run_graph: Optional[RunGraph],
                 job_context: JobContext,
                 ) -> None:
        super().__init__()
        self.run_graph = run_graph
        self.job_context = job_context


def batch_run_func(context: JobContext, graph: RunGraph):
    value_map = {}
    for i in range(len(graph.nodes)):
        node = graph.nodes[i]
        function_context: FunctionContext = FunctionContext(node_spec=node, job_context=context)
        c: Executor = deserialize(graph.executor_bytes[i])
        c.setup(function_context)
        if node.instance_id in graph.dependencies:
            ds = graph.dependencies[node.instance_id]
            params = []
            for d in ds:
                params.append(value_map[d.target_node_id][d.port])
            value_map[node.instance_id] = c.execute(function_context, params)
        else:
            value_map[node.instance_id] = c.execute(function_context, [])
        c.close(function_context)


def stream_run_func(context: JobContext, graph: RunGraph):
    executors: List[Executor] = []
    contexts: List[FunctionContext] = []
    for index in range(len(graph.nodes)):
        caller: Executor = deserialize(graph.executor_bytes[index])
        executors.append(caller)
        node: AINode = graph.nodes[index]
        function_context = FunctionContext(node_spec=node, job_context=context)
        contexts.append(function_context)

    def setup():
        for ii in range(len(executors)):
            cc = executors[ii]
            cc.setup(contexts[ii])

    def close():
        for ii in range(len(executors)):
            cc = executors[ii]
            cc.close(contexts[ii])

    setup()
    value_map = {}
    for i in range(len(graph.nodes)):
        node = graph.nodes[i]
        c = executors[i]
        if node.instance_id in graph.dependencies:
            ds = graph.dependencies[node.instance_id]
            params = []
            for d in ds:
                params.append(value_map[d.target_node_id][d.port])
            value_map[node.instance_id] = c.execute(contexts[i], params)
        else:
            value_map[node.instance_id] = c.execute(contexts[i], [])
    close()
