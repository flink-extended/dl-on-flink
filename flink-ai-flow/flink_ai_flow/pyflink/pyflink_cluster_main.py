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
import argparse
import logging
from ai_flow.util import serialization_utils
from ai_flow.api.configuration import set_default_project_config
from flink_ai_flow.local_flink_job import LocalFlinkJob
from flink_ai_flow.pyflink import job_creator
from flink_ai_flow.pyflink.user_define_executor import TableEnvCreator


def read_config_file(file_path):
    with open(file_path, 'rb') as f:
        config_bytes = f.read()
        return serialization_utils.deserialize(config_bytes)


def run_project(project_path, config_file):
    local_flink_job: LocalFlinkJob = read_config_file("{}/temp/{}".format(project_path, config_file))
    table_creator: TableEnvCreator = local_flink_job.job_config.get_table_env_create_func()
    set_default_project_config(local_flink_job.job_context.project_config)
    exec_env, t_env, statement_set = table_creator.create_table_env()
    run_graph = job_creator.build_run_graph(local_flink_job.ai_graph)
    job_creator.submit_flink_job(exec_env, t_env, statement_set, local_flink_job, run_graph)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='program')
    parser.add_argument('--project-path')
    parser.add_argument('--config-file')
    parser.add_argument('--entry-module-path')
    args = parser.parse_args()
    l_project_path, l_config_file, l_entry_module_path \
        = args.project_path, args.config_file, args.entry_module_path
    logging.info(sys.path)
    mdl = importlib.import_module(l_entry_module_path)
    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
    else:
        names = [x for x in mdl.__dict__ if not x.startswith("_")]
    globals().update({k: getattr(mdl, k) for k in names})

    run_project(l_project_path, l_config_file)
