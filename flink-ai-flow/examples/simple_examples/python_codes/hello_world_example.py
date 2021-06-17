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
import tempfile
import textwrap

from typing import List

from airflow.logging_config import configure_logging

import ai_flow
from python_ai_flow import Executor


def create_sever_config(root_dir_path):
    content = textwrap.dedent(f"""\
        master_ip: localhost
        master_port: 50051
        db_uri: sqlite:///{root_dir_path}/aiflow.db
        db_type: sql_lite
        start_default_notification: True
        notification_uri: localhost:50052
    """)
    master_yaml_path = root_dir_path + "/master.yaml"
    with open(master_yaml_path, "w") as f:
        f.write(content)
    return master_yaml_path


def create_project_config(root_dir_path):
    content = textwrap.dedent("""\
        project_name: test_project
        master_ip: localhost
        master_port: 50051
    """)
    project_yaml_path = root_dir_path + "/project.yaml"
    with open(project_yaml_path, "w") as f:
        f.write(content)
    return project_yaml_path


def create_workflow_config(root_dir_path):
    content = textwrap.dedent("""\
        job_1:
            platform: local
            engine: python
            job_name: job_1
        job_2:
            platform: local
            engine: python
            job_name: job_2
    """)
    workflow_config_path = root_dir_path + "/workflow_config.yaml"
    with open(root_dir_path + "/workflow_config.yaml", "w") as f:
        f.write(content)
    return workflow_config_path


def start_master(master_yaml_path):
    configure_logging()
    server_runner = ai_flow.AIFlowServerRunner(config_file=master_yaml_path)
    server_runner.start(is_block=False)
    return server_runner


class PrintHelloExecutor(Executor):
    def __init__(self, job_name):
        super().__init__()
        self.job_name = job_name

    def execute(self, function_context: ai_flow.FunctionContext, input_list: List) -> None:
        print("hello world! {}".format(self.job_name))


def build_workflow(workflow_config_path):
    with ai_flow.global_config_file(workflow_config_path):
        with ai_flow.config('job_1'):
            op_1 = ai_flow.user_define_operation(
                ai_flow.PythonObjectExecutor(PrintHelloExecutor('job_1')))

        with ai_flow.config('job_2'):
            op_2 = ai_flow.user_define_operation(
                ai_flow.PythonObjectExecutor(PrintHelloExecutor('job_2')))

        ai_flow.stop_before_control_dependency(op_2, op_1)


def run_workflow(root_dir_path, project_yaml_path):
    ai_flow.set_project_config_file(project_yaml_path)
    res = ai_flow.run(root_dir_path,
                      dag_id='hello_world_example',
                      scheduler_type=ai_flow.SchedulerType.AIFLOW)
    ai_flow.wait_workflow_execution_finished(res)


if __name__ == '__main__':
    root_dir = tempfile.mkdtemp()

    master_yaml = create_sever_config(root_dir)
    project_yaml = create_project_config(root_dir)
    workflow_config = create_workflow_config(root_dir)

    master_server = start_master(master_yaml)

    build_workflow(workflow_config)
    run_workflow(root_dir, project_yaml)

    master_server.stop()
    print("The output could be found in: %s/logs/" % root_dir)
