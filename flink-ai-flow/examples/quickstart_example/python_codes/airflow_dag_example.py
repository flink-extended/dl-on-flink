import os
from typing import List

import ai_flow as af
from ai_flow import FunctionContext
from ai_flow.common.scheduler_type import SchedulerType
from python_ai_flow import Executor
from datetime import datetime


class PrintHelloExecutor(Executor):
    def __init__(self, job_name):
        super().__init__()
        self.job_name = job_name

    def execute(self, function_context: FunctionContext, input_list: List) -> None:
        print("hello world! {}".format(self.job_name))


project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_workflow():
    with af.global_config_file(project_path + '/resources/workflow_config.yaml'):
        with af.config('job_1'):
            op_1 = af.user_define_operation(af.PythonObjectExecutor(PrintHelloExecutor('job_1')))

        with af.config('job_2'):
            op_2 = af.user_define_operation(af.PythonObjectExecutor(PrintHelloExecutor('job_2')))

        with af.config('job_3'):
            op_3 = af.user_define_operation(af.PythonObjectExecutor(PrintHelloExecutor('job_3')))

    af.stop_before_control_dependency(op_3, op_1)
    af.stop_before_control_dependency(op_3, op_2)


def run_workflow():
    build_workflow()
    af.set_project_config_file(project_path + '/project.yaml')

    # deploy a workflow which should be scheduled every 10 minutes
    default_args = '{\'schedule_interval\': %s, \'start_date\': \'%s\'}' % ('\'*/10 * * * *\'', datetime.utcnow())
    af.deploy_to_airflow(project_path, dag_id='airflow_dag_example', default_args=default_args)

    # Force trigger once
    context = af.run(project_path=project_path,
                     dag_id='airflow_dag_example',
                     scheduler_type=SchedulerType.AIRFLOW)
    print(context.dagrun_id)


if __name__ == '__main__':
    run_workflow()

