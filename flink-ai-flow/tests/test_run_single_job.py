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

import time

from airflow.models import DagRun
from airflow.utils.state import State
from ai_flow.common.scheduler_type import SchedulerType
from airflow.models.taskexecution import TaskExecution
from airflow.utils.session import create_session
from notification_service.client import NotificationClient
from ai_flow.executor.executor import CmdExecutor
from tests.base_ete_test import BaseETETest, workflow_config_file, project_path
import ai_flow as af


class TestRunAIFlowJobs(BaseETETest):

    def test_run_cmd_job(self):
        def build_and_submit_ai_flow():
            with af.global_config_file(workflow_config_file()):
                with af.config('task_1'):
                    cmd_executor = af.user_define_operation(output_num=0,
                                                            executor=CmdExecutor(
                                                                cmd_line='echo "hello world"'.format(1)))
                dag_file = af.submit(project_path())
            return dag_file

        def run_task_function(client: NotificationClient):
            af.run(project_path(), 'test_workflow', SchedulerType.AIRFLOW)
            while True:
                with create_session() as session:
                    dag_run = session.query(DagRun).filter(DagRun.dag_id == 'test_workflow').first()
                    if dag_run is not None and dag_run.state == State.SUCCESS:
                        break
                    else:
                        time.sleep(1)

        self.run_ai_flow(build_and_submit_ai_flow, run_task_function)
        with create_session() as session:
            tes = session.query(TaskExecution).filter(TaskExecution.dag_id == 'test_workflow',
                                                      TaskExecution.task_id == 'task_1').all()
            self.assertEqual(1, len(tes))


