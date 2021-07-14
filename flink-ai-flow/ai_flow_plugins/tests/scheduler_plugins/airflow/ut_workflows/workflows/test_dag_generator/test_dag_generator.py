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
import unittest
import os
import shutil
from ai_flow.workflow.periodic_config import PeriodicConfig

from ai_flow import AIFlowServerRunner, init_ai_flow_context
import ai_flow as af
from ai_flow.workflow.control_edge import TaskAction, ConditionConfig, ConditionType
from ai_flow.workflow.status import Status
from ai_flow.test.api.mock_plugins import MockJobFactory


class TestDagGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config_file = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '/master.yaml'
        cls.master = AIFlowServerRunner(config_file=config_file)
        cls.master.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.master.stop()

    def setUp(self):
        self.master._clear_db()
        af.current_graph().clear_graph()
        init_ai_flow_context()

    def tearDown(self):
        self.master._clear_db()
        generated = '{}/generated'.format(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        if os.path.exists(generated):
            shutil.rmtree(generated)

    def test_one_task(self):
        with af.job_config('task_1'):
            af.user_define_operation(processor=None)
        w = af.workflow_operation.submit_workflow(workflow_name='test_dag_generator')
        code = w.properties.get('code')
        self.assertTrue('op_0 = AIFlowOperator' in code)

    def test_two_task(self):
        with af.job_config('task_1'):
            af.user_define_operation(processor=None)
        with af.job_config('task_2'):
            af.user_define_operation(processor=None)
        af.action_on_event(job_name='task_2', event_key='a', event_type='a', event_value='a', sender='task_1')
        w = af.workflow_operation.submit_workflow(workflow_name='test_dag_generator')
        code = w.properties.get('code')
        self.assertTrue("op_1.subscribe_event('a', 'a', 'default', 'task_1')" in code)
        self.assertTrue("op_1.set_events_handler(AIFlowHandler(configs_op_1))" in code)

    def test_three_task(self):
        with af.job_config('task_1'):
            af.user_define_operation(processor=None)
        with af.job_config('task_2'):
            af.user_define_operation(processor=None)
        with af.job_config('task_3'):
            af.user_define_operation(processor=None)
        af.action_on_event(job_name='task_3', event_key='a', event_type='a', event_value='a', sender='task_1')
        af.action_on_job_status(job_name='task_3', upstream_job_name='task_2',
                                upstream_job_status=Status.FINISHED,
                                action=TaskAction.START)
        w = af.workflow_operation.submit_workflow(workflow_name='test_dag_generator')
        code = w.properties.get('code')
        self.assertTrue(".subscribe_event('a', 'a', 'default', 'task_1')" in code)
        # Now do not support the event_type equals JOB_STATUS_CHANGED event.
        # self.assertTrue(".subscribe_event('test_dag_generator', 'JOB_STATUS_CHANGED', 'test_project', 'task_2')" in code)
        self.assertTrue(".set_events_handler(AIFlowHandler(configs_op_" in code)

    def test_periodic_cron_task(self):
        with af.job_config('task_4'):
            af.user_define_operation(processor=None)
        w = af.workflow_operation.submit_workflow(workflow_name='test_dag_generator')
        code = w.properties.get('code')
        self.assertTrue('op_0 = AIFlowOperator' in code)
        self.assertTrue('op_0.executor_config' in code)

    def test_periodic_interval_task(self):
        with af.job_config('task_5'):
            af.user_define_operation(processor=None)
        w = af.workflow_operation.submit_workflow(workflow_name='test_dag_generator')
        code = w.properties.get('code')

        self.assertTrue('op_0 = AIFlowOperator' in code)
        self.assertTrue('op_0.executor_config' in code)

    def test_periodic_cron_workflow(self):
        workflow_config_ = af.current_workflow_config()
        workflow_config_.periodic_config = PeriodicConfig(trigger_config={'start_date': "2020,1,1,,,,Asia/Chongqing",
                                                                          'cron': "*/5 * * * * * *"})
        with af.job_config('task_1'):
            af.user_define_operation(processor=None)
        w = af.workflow_operation.submit_workflow(workflow_name='test_dag_generator')
        code = w.properties.get('code')
        self.assertTrue('op_0 = AIFlowOperator' in code)
        self.assertTrue('datetime' in code)
        self.assertTrue('schedule_interval' in code)

    def test_periodic_interval_workflow(self):
        workflow_config_ = af.current_workflow_config()
        workflow_config_.periodic_config = PeriodicConfig(trigger_config={'start_date': "2020,1,1,,,,Asia/Chongqing",
                                                                          'interval': "1,1,1,"})
        with af.job_config('task_1'):
            af.user_define_operation(processor=None)
        w = af.workflow_operation.submit_workflow(workflow_name='test_dag_generator')
        code = w.properties.get('code')
        self.assertTrue('op_0 = AIFlowOperator' in code)
        self.assertTrue('datetime' in code)
        self.assertTrue('schedule_interval' in code)
        self.assertTrue('timedelta' in code)

    def test_action_on_job_status(self):
        with af.job_config('task_1'):
            af.user_define_operation(processor=None)
        with af.job_config('task_2'):
            af.user_define_operation(processor=None)
        with af.job_config('task_3'):
            af.user_define_operation(processor=None)
        af.action_on_job_status(job_name='task_2', upstream_job_name='task_1')
        af.action_on_job_status(job_name='task_3', upstream_job_name='task_2',
                                upstream_job_status=Status.RUNNING,
                                action=TaskAction.START)
        w = af.workflow_operation.submit_workflow(workflow_name='test_dag_generator')
        code = w.properties.get('code')
        self.assertTrue(
            "op_1.subscribe_event('test_dag_generator.task_1', 'TASK_STATUS_CHANGED', 'test_project', 'task_1')" in code)
        self.assertTrue(
            "op_2.subscribe_event('test_dag_generator.task_2', 'TASK_STATUS_CHANGED', 'test_project', 'task_2')" in code)

    def test_action_on_job_status_two_status(self):
        with af.job_config('task_1'):
            af.user_define_operation(processor=None)
        with af.job_config('task_2'):
            af.user_define_operation(processor=None)
        af.action_on_job_status(job_name='task_2', upstream_job_name='task_1',
                                upstream_job_status=Status.RUNNING,
                                action=TaskAction.START)
        af.action_on_job_status(job_name='task_2', upstream_job_name='task_1', upstream_job_status=Status.FINISHED,
                                action=TaskAction.STOP)
        w = af.workflow_operation.submit_workflow(workflow_name='test_dag_generator')
        code = w.properties.get('code')
        self.assertTrue('"event_value": "RUNNING"' in code)
        self.assertTrue('"event_value": "FINISHED"' in code)



if __name__ == '__main__':
    unittest.main()
