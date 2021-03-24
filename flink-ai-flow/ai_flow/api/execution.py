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
_workflow_execution_id_set_flag = False
_workflow_execution_id = None


class ExecutionContext(object):
    def __init__(self):
        pass


def set_workflow_execution_id(workflow_execution_id: int):
    global _workflow_execution_id_set_flag
    if _workflow_execution_id_set_flag:
        raise Exception("project configuration cannot be set repeatedly!")
    else:
        _workflow_execution_id = workflow_execution_id
        _workflow_execution_id_set_flag = True


def get_workflow_execution_id():
    return _workflow_execution_id


def stop_workflow(workflow_id) -> bool:
    """
    Stop the workflow. No more dag_run would be scheduled and all running jobs would be stopped.

    :param workflow_id: workflow id
    :return: True if succeed
    """
    pass


def suspend_workflow(workflow_id) -> bool:
    """
    Suspend the workflow. No more dag_run would be scheduled.

    :param workflow_id: workflow id
    :return: True if succeed
    """
    pass


def resume_workflow(workflow_id) -> bool:
    """
    Resume a stopped workflow.

    :param workflow_id: workflow id
    :return: True if succeed
    """
    pass


def trigger_workflow_run(workflow_id) -> ExecutionContext:
    """
    Trigger a new instance of workflow immediately.

    :param workflow_id: workflow id
    :return: True if a new instance is triggered
    """
    pass


def start_task_instance(workflow_id, job_name, context: ExecutionContext) -> bool:
    """
    Force start a task. if it is running, do nothing.

    :param workflow_id: workflow id
    :param job_name: job name
    :param context: context of workflow instance
    :return: True if the task is started
    """
    pass


def stop_task_instance(workflow_id, job_name, context: ExecutionContext) -> bool:
    """
    Force stop a running task

    :param workflow_id: workflow id
    :param job_name: job name
    :param context: context of workflow instance
    :return: True if the task is stopped
    """
    pass


def restart_task_instance(workflow_id, job_name, context: ExecutionContext) -> bool:
    """
    Force restart a task

    :param workflow_id: workflow id
    :param job_name: job name
    :param context: context of workflow instance
    :return: True if the task is restarted
    """
    pass
