from ai_flow.workflow.control_edge import JobAction

from ai_flow.workflow.status import Status

import ai_flow as af
from ai_flow_plugins.job_plugins.bash import BashProcessor


def main():
    af.init_ai_flow_context()
    with af.job_config('task_1'):
        af.user_define_operation(processor=BashProcessor("sleep 30"))
    with af.job_config('task_2'):
        af.user_define_operation(processor=BashProcessor("sleep 60"))
    with af.job_config('task_3'):
        af.user_define_operation(processor=BashProcessor("echo hello"))

    af.action_on_job_status('task_2', 'task_1', upstream_job_status=Status.RUNNING, action=JobAction.START)
    af.action_on_job_status('task_2', 'task_1', upstream_job_status=Status.FINISHED, action=JobAction.STOP)

    af.action_on_job_status('task_3', 'task_1', upstream_job_status=Status.RUNNING, action=JobAction.START)
    af.action_on_job_status('task_3', 'task_2', upstream_job_status=Status.KILLED, action=JobAction.RESTART)

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
