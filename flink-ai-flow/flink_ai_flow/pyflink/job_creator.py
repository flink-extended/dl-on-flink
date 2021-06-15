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
import logging
import os
from typing import Dict, Text, List, Union

from pyflink.table import TableEnvironment, StatementSet
from pyflink.table.table import Table

from ai_flow.util import serialization_utils
from ai_flow.graph.ai_nodes.executable import ExecutableNode
from ai_flow.graph.edge import DataEdge
from ai_flow.graph.graph import AISubGraph
from flink_ai_flow.flink_executor import FlinkPythonExecutor
from flink_ai_flow.local_flink_job import LocalFlinkJob
from flink_ai_flow.pyflink.user_define_executor import Executor, SinkExecutor, SourceExecutor, FlinkFunctionContext


class ExecutorWrapper(object):
    def __init__(self,
                 executor: FlinkPythonExecutor) -> None:
        super().__init__()
        self.executor: Union[Executor, SinkExecutor, SourceExecutor] \
            = serialization_utils.deserialize(executor.python_object)
        if not isinstance(self.executor, Executor) \
                and not isinstance(self.executor, SourceExecutor) \
                and not isinstance(self.executor, SinkExecutor):
            raise Exception("python ai flow only support Executor, SourceExecutor, SinkExecutor class "
                            "but config executor is {}"
                            .format(type(self.executor)))

    def setup(self, function_context: FlinkFunctionContext):
        self.executor.setup(function_context)

    def close(self, function_context: FlinkFunctionContext):
        self.executor.close(function_context)

    def execute(self, context: FlinkFunctionContext, args: List[Table]) -> List[Table]:
        if isinstance(self.executor, Executor):
            return self.executor.execute(context, args)
        elif isinstance(self.executor, SourceExecutor):
            return [self.executor.execute(context)]
        elif isinstance(self.executor, SinkExecutor):
            self.executor.execute(context, args[0])
            return []


class FlinkRunGraph(object):
    def __init__(self) -> None:
        super().__init__()
        self.nodes: List[ExecutableNode] = []
        self.executor_list: List[ExecutorWrapper] = []
        self.dependencies: Dict[Text, List[DataEdge]] = {}


def create_executor_wrapper(node: ExecutableNode) -> ExecutorWrapper:
    return ExecutorWrapper(executor=node.executor)


def build_run_graph(sub_graph: AISubGraph) -> FlinkRunGraph:
    run_graph = FlinkRunGraph()
    processed_nodes = set()
    node_list: List[ExecutableNode] = []
    for n in sub_graph.nodes.values():
        node_list.append(n)
    for e in sub_graph.edges:
        data_channel_list = []
        for c in sub_graph.edges[e]:
            cc: DataEdge = c
            data_channel_list.append(cc)
        run_graph.dependencies[e] = data_channel_list

    node_size = len(sub_graph.nodes)
    processed_size = len(processed_nodes)
    while processed_size != node_size:
        p_nodes = []
        for i in range(len(node_list)):
            if node_list[i].instance_id in sub_graph.edges:
                flag = True
                for c in sub_graph.edges[node_list[i].instance_id]:
                    if c.target_node_id in processed_nodes:
                        pass
                    else:
                        flag = False
                        break
            else:
                flag = True
            if flag:
                p_nodes.append(node_list[i])
        if 0 == len(p_nodes):
            raise Exception("graph has circle!")
        for n in p_nodes:
            run_graph.nodes.append(n)
            run_graph.executor_list.append(create_executor_wrapper(n))
            node_list.remove(n)
            processed_nodes.add(n.instance_id)
        processed_size = len(processed_nodes)
    return run_graph


def submit_flink_job(exec_env, t_env: TableEnvironment, statement_set: StatementSet, flink_job: LocalFlinkJob,
                     graph: FlinkRunGraph):
    context = flink_job.job_context
    value_map = {}
    for i in range(len(graph.nodes)):
        node = graph.nodes[i]
        function_context: FlinkFunctionContext = FlinkFunctionContext(exec_env=exec_env, t_env=t_env,
                                                                      statement_set=statement_set,
                                                                      node_spec=node, job_context=context)
        c: Union[Executor, SourceExecutor, SinkExecutor] = graph.executor_list[i]
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
    job_client = statement_set.execute().get_job_client()
    if job_client is not None:
        workflow_dir = '{}/temp/{}'.format(flink_job.job_config.project_path,
                                           str(flink_job.job_context.workflow_execution_id))
        os.makedirs(workflow_dir, exist_ok=True)
        with open('{}/{}'.format(workflow_dir, flink_job.instance_id), 'w') as f:
            logging.info('workflow execution id: {}, job uuid: {}, Flink job id: {}'.format(
                flink_job.job_context.workflow_execution_id, flink_job.instance_id, job_client.get_job_id()))
            f.write(str(job_client.get_job_id()))
        job_client.get_job_execution_result(user_class_loader=None).result()
