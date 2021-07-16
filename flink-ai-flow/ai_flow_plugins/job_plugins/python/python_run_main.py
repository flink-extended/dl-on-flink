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
from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo
from ai_flow import current_workflow_config
from ai_flow.util import serialization_utils
from ai_flow.util.serialization_utils import read_object_from_serialized_file
from ai_flow.runtime.job_runtime_context import init_job_runtime_context
from ai_flow.runtime.job_runtime_env import JobRuntimeEnv
from ai_flow_plugins.job_plugins.python import PythonProcessor
from ai_flow_plugins.job_plugins.python.python_job_plugin import RunGraph
from ai_flow_plugins.job_plugins.python.python_processor import ExecutionContext


def python_execute_func(run_graph: RunGraph, job_execution_info: JobExecutionInfo):
    processor: List[PythonProcessor] = []
    contexts: List[ExecutionContext] = []
    for index in range(len(run_graph.nodes)):
        caller: PythonProcessor = serialization_utils.deserialize(run_graph.processor_bytes[index])
        processor.append(caller)
        node: AINode = run_graph.nodes[index]
        execution_context = ExecutionContext(config=node.node_config, job_execution_info=job_execution_info)
        contexts.append(execution_context)

    def setup():
        for ii in range(len(processor)):
            cc = processor[ii]
            cc.setup(contexts[ii])

    def close():
        for ii in range(len(processor)):
            cc = processor[ii]
            cc.close(contexts[ii])

    setup()
    value_map = {}
    for i in range(len(run_graph.nodes)):
        node = run_graph.nodes[i]
        c = processor[i]
        if node.node_id in run_graph.dependencies:
            ds = run_graph.dependencies[node.node_id]
            params = []
            for d in ds:
                params.append(value_map[d.source][d.port])
            value_map[node.node_id] = c.process(contexts[i], params)
        else:
            value_map[node.node_id] = c.process(contexts[i], [])
    close()


def run_project(run_graph_file, working_dir):
    run_graph: RunGraph = read_object_from_serialized_file(run_graph_file)
    job_runtime_env = JobRuntimeEnv(working_dir=working_dir)
    init_job_runtime_context(job_runtime_env)
    workflow_name = current_workflow_config().workflow_name
    entry_module_path = workflow_name
    mdl = importlib.import_module(entry_module_path)
    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
    else:
        names = [x for x in mdl.__dict__ if not x.startswith("_")]
    globals().update({k: getattr(mdl, k) for k in names})
    try:
        python_execute_func(run_graph=run_graph, job_execution_info=job_runtime_env.job_execution_info)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise Exception(str(e))


if __name__ == '__main__':
    l_graph_file, l_working_dir = sys.argv[1], sys.argv[2]
    run_project(l_graph_file, l_working_dir)
