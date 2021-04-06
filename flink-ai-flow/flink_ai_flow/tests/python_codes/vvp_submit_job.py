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
from ai_flow.application_master.master import AIFlowMaster
import flink_ai_flow as faf
import test_util


def run_flink_job():
    with af.global_config_file(test_util.get_job_config_file()):
        with af.config('vvp_job'):
            faf.vvp_job()
    workflow_id = af.run(test_util.get_project_path())
    res = af.wait_workflow_execution_finished(workflow_id)
    print(res)


def run_flink_python_job():
    with af.global_config_file(test_util.get_job_config_file()):
        with af.config('vvp_python_job'):
            faf.vvp_job()
    workflow_id = af.run(test_util.get_project_path(), dag_id='wordcount_vvp_python',
                         scheduler_type=af.SchedulerType.AIRFLOW)
    # res = af.wait_workflow_execution_finished(workflow_id)
    # print(res)


def run_flink_spec_job():
    with af.global_config_file(test_util.get_job_config_file()):
        with af.config('task_1'):
            faf.vvp_job()
        result = af.deploy_to_airflow(test_util.get_project_path())
        print(result)


if __name__ == '__main__':
    config_file = test_util.get_master_config_file()
    master = AIFlowMaster(
        config_file=config_file)
    master.start()
    test_util.set_project_config(__file__)
    # run_flink_job()
    # run_flink_python_job()
    run_flink_spec_job()
    master.stop()
