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
import os
import time
from typing import List

import ai_flow as af
from ai_flow import FunctionContext
from ai_flow.graph.edge import TaskAction
from ai_flow.common.scheduler_type import SchedulerType
from python_ai_flow import Executor

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PrintHelloExecutor(Executor):

    def __init__(self, job_name):
        super().__init__()
        self.job_name = job_name

    def execute(self, function_context: FunctionContext, input_list: List) -> None:
        print("hello world! {}".format(self.job_name))


class SendEventExecutor(Executor):

    def __init__(self, key, value, event_type="UNDEFINED", num=1, pre_time=0, post_time=0):
        super().__init__()
        self.key = key
        self.value = value
        self.event_type = event_type
        self.num = num
        self.pre_time = pre_time
        self.post_time = post_time

    def execute(self, function_context: FunctionContext, input_list: List) -> None:
        for i in range(self.num):
            time.sleep(self.pre_time)
            af.send_event(self.key, self.value, self.event_type)
            time.sleep(self.post_time)


def build_workflow():
    with af.global_config_file(project_path + '/resources/workflow_config.yaml'):
        with af.config('job_1'):
            op_1 = af.user_define_operation(af.PythonObjectExecutor(PrintHelloExecutor('job_1')))

        with af.config('job_2'):
            op_2 = af.user_define_operation(af.PythonObjectExecutor(
                SendEventExecutor(key='key_1', value='value_1', num=2, post_time=30)))

        with af.config('job_3'):
            op_3 = af.user_define_operation(af.PythonObjectExecutor(
                SendEventExecutor(key='key_2', value='value_2', num=2, post_time=30)))

    af.user_define_control_dependency(op_1, op_2, event_key='key_1', event_type='UNDEFINED',
                                      event_value="value_1", action=TaskAction.RESTART)

    af.user_define_control_dependency(op_1, op_3, event_key='key_2', event_type='UNDEFINED',
                                      event_value="value_2", action=TaskAction.RESTART)


def run_workflow():
    build_workflow()
    af.set_project_config_file(project_path+ '/project.yaml')
    res = af.run(project_path, dag_id='repeated_dag_example', scheduler_type=SchedulerType.AIFLOW)
    af.wait_workflow_execution_finished(res)


if __name__ == '__main__':
    run_workflow()
