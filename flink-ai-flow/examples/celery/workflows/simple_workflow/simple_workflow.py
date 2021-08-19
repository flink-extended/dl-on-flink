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
import ai_flow as af
from ai_flow import JobAction
from ai_flow.workflow.status import Status
from ai_flow_plugins.job_plugins.bash import BashProcessor


def main():
    af.init_ai_flow_context()
    with af.job_config('task_1'):
        af.user_define_operation(processor=BashProcessor("echo before_sleep"))
    with af.job_config('task_2'):
        af.user_define_operation(processor=BashProcessor("sleep 100"))
    with af.job_config('task_3'):
        af.user_define_operation(processor=BashProcessor("sleep 10"))

    af.action_on_job_status(job_name='task_2', upstream_job_name='task_1')
    af.action_on_job_status(job_name='task_3', upstream_job_name='task_2', upstream_job_status=Status.RUNNING)
    af.action_on_job_status(job_name='task_2', upstream_job_name='task_3', action=JobAction.STOP)

    workflow_name = af.current_workflow_config().workflow_name
    stop_workflow_executions(workflow_name)
    af.workflow_operation.submit_workflow(workflow_name)
    af.workflow_operation.start_new_workflow_execution(workflow_name)


def stop_workflow_executions(workflow_name):
    workflow_executions = af.workflow_operation.list_workflow_executions(workflow_name)
    for workflow_execution in workflow_executions:
        af.workflow_operation.stop_workflow_execution(workflow_execution.workflow_execution_id)


if __name__ == '__main__':
    main()
