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
import os
import sys

from ai_flow.api.execution import set_workflow_execution_id
from ai_flow.api.configuration import set_default_project_config
from ai_flow.util.serialization_utils import deserialize
from python_ai_flow.python_job_common import RunArgs


def read_from_serialized_file(file_path):
    with open(file_path, 'rb') as f:
        serialized_bytes = f.read()
    return deserialize(serialized_bytes)


def del_tmp_file(func_file_path, args_file_path):
    if os.path.exists(func_file_path):
        os.remove(func_file_path)
    if os.path.exists(args_file_path):
        os.remove(args_file_path)


def run_project(project_path, func_file, args_file, entry_module_path):
    mdl = importlib.import_module(entry_module_path)
    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
    else:
        names = [x for x in mdl.__dict__ if not x.startswith("_")]
    globals().update({k: getattr(mdl, k) for k in names})
    func = read_from_serialized_file("{}/temp/{}".format(project_path, func_file))
    args: RunArgs = read_from_serialized_file("{}/temp/{}".format(project_path, args_file))
    set_default_project_config(args.job_context.project_config)
    set_workflow_execution_id(args.job_context.workflow_execution_id)
    try:
        func(args.job_context, args.run_graph)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise Exception(str(e))


if __name__ == '__main__':
    l_project_path, l_func_file, l_args_file, l_entry_module_path \
        = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    run_project(l_project_path, l_func_file, l_args_file, l_entry_module_path)
