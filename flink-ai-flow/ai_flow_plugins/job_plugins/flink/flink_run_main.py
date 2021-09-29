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
import importlib
import sys

from typing import List

from ai_flow.ai_graph.ai_node import AINode
from ai_flow.util import serialization_utils

from ai_flow.util.serialization_utils import read_object_from_serialized_file
from ai_flow.runtime.job_runtime_context import init_job_runtime_context
from ai_flow.runtime.job_runtime_env import JobRuntimeEnv
from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo
from ai_flow_plugins.job_plugins.flink import FlinkPythonProcessor, ExecutionContext
from ai_flow_plugins.job_plugins.flink.flink_job_plugin import RunGraph
from ai_flow_plugins.job_plugins.flink.flink_env import FlinkEnv


def flink_execute_func(run_graph: RunGraph, job_execution_info: JobExecutionInfo, flink_env: FlinkEnv):
    processors: List[FlinkPythonProcessor] = []
    contexts: List[ExecutionContext] = []
    exec_env, table_env, statement_set = flink_env.create_env()
    for index in range(len(run_graph.nodes)):
        caller: FlinkPythonProcessor = serialization_utils.deserialize(run_graph.processor_bytes[index])
        processors.append(caller)
        node: AINode = run_graph.nodes[index]
        execution_context = ExecutionContext(config=node.node_config,
                                             job_execution_info=job_execution_info,
                                             execution_env=exec_env,
                                             table_env=table_env,
                                             statement_set=statement_set)
        contexts.append(execution_context)

    def setup():
        for ii in range(len(processors)):
            cc = processors[ii]
            cc.open(contexts[ii])

    def close():
        for ii in range(len(processors)):
            cc = processors[ii]
            cc.close(contexts[ii])

    setup()
    value_map = {}
    for i in range(len(run_graph.nodes)):
        node = run_graph.nodes[i]
        c = processors[i]
        if node.node_id in run_graph.dependencies:
            ds = run_graph.dependencies[node.node_id]
            params = []
            for d in ds:
                params.append(value_map[d.source][d.port])
            value_map[node.node_id] = c.process(contexts[i], params)
        else:
            value_map[node.node_id] = c.process(contexts[i], [])
    close()
    
    if statement_set.wrapped_context.need_execute:
        statement_set.execute()
    
    job_id_list = table_env.wrapped_context.get_job_ids() + statement_set.wrapped_context.get_job_ids()
    if len(job_id_list) > 0:
        with open('./job_id', 'w') as fp:
            for job_id in job_id_list:
                fp.write(str(job_id) + "\n")
    
    table_env.wait_execution_results()
    statement_set.wait_execution_results()


def run_project(run_graph_file, working_dir, flink_env_file):
    run_graph: RunGraph = read_object_from_serialized_file(run_graph_file)
    flink_env: FlinkEnv = read_object_from_serialized_file(flink_env_file)
    job_runtime_env = JobRuntimeEnv(working_dir)
    job_execution_info = job_runtime_env.job_execution_info
    init_job_runtime_context(job_runtime_env)
    entry_module_path = job_execution_info.workflow_execution.workflow_info.workflow_name
    mdl = importlib.import_module(entry_module_path)
    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
    else:
        names = [x for x in mdl.__dict__ if not x.startswith("_")]
    globals().update({k: getattr(mdl, k) for k in names})
    try:
        flink_execute_func(run_graph=run_graph, job_execution_info=job_execution_info, flink_env=flink_env)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise Exception(str(e))


if __name__ == '__main__':
    l_graph_file, l_working_dir, l_flink_file = sys.argv[1], sys.argv[2], sys.argv[3]
    run_project(l_graph_file, l_working_dir, l_flink_file)
