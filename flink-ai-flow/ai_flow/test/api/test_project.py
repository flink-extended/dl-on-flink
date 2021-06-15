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
import sys
import time
import unittest

import ai_flow as af
from ai_flow import AIFlowMaster
from ai_flow.executor.executor import CmdExecutor
from ai_flow.graph.edge import TaskAction, MetValueCondition, MetCondition, EventLife
from ai_flow.test import test_util
from ai_flow.workflow.job_config import PeriodicConfig


class TestProject(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config_file = test_util.get_master_config_file()
        cls.master = AIFlowMaster(config_file=config_file)
        cls.master.start()
        test_util.set_project_config(__file__)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.master.stop()

    def setUp(self):
        TestProject.master._clear_db()
        af.default_graph().clear_graph()

    def tearDown(self):
        TestProject.master._clear_db()

    @staticmethod
    def build_ai_graph(sleep_time: int):
        with af.engine('cmd_line'):
            p_list = []
            for i in range(3):
                p = af.user_define_operation(
                    executor=CmdExecutor(cmd_line="echo 'hello_{}' && sleep {}".format(i, sleep_time)))
                p_list.append(p)
            af.stop_before_control_dependency(p_list[0], p_list[1])
            af.stop_before_control_dependency(p_list[0], p_list[2])

    def test_run_project(self):
        print(sys._getframe().f_code.co_name)
        TestProject.build_ai_graph(1)
        workflow_id = af.submit_ai_flow()
        res = af.wait_workflow_execution_finished(workflow_id)
        self.assertEqual(0, res)

    def test_stream_with_external_trigger(self):
        print(sys._getframe().f_code.co_name)
        trigger = af.external_trigger(name='stream_trigger')
        job_config = af.BaseJobConfig('local', 'cmd_line')
        job_config.job_name = 'test_cmd'
        with af.config(job_config):
            cmd_executor = af.user_define_operation(output_num=0,
                                                    executor=CmdExecutor(
                                                        cmd_line="echo 'hello world' && sleep {}".format(1)))
        af.user_define_control_dependency(src=cmd_executor, dependency=trigger, event_key='key',
                                          event_value='value', event_type='name', condition=MetCondition.NECESSARY
                                          , action=TaskAction.START, life=EventLife.ONCE,
                                          value_condition=MetValueCondition.EQUAL)
        workflow_id = af.submit_ai_flow()
        af.get_ai_flow_client().publish_event('key', 'value', 'name')
        time.sleep(5)
        af.get_ai_flow_client().publish_event('key', 'value', 'name')
        time.sleep(10)
        af.stop_execution_by_id(workflow_id)
        res = af.get_ai_flow_client().list_job(5, 0)
        self.assertEqual(3, len(res))

    def test_user_define_control_dependency(self):
        print(sys._getframe().f_code.co_name)
        trigger = af.external_trigger(name='stream_trigger')
        job_config = af.BaseJobConfig('local', 'cmd_line')
        job_config.job_name = 'test_cmd'
        with af.config(job_config):
            cmd_executor = af.user_define_operation(output_num=0,
                                                    executor=CmdExecutor(
                                                        cmd_line="echo 'hello world' && sleep {}".format(1)))
        af.user_define_control_dependency(src=cmd_executor, dependency=trigger, event_key='key',
                                          event_value='value', event_type='name', condition=MetCondition.NECESSARY
                                          , action=TaskAction.START, life=EventLife.ONCE,
                                          value_condition=MetValueCondition.UPDATE)
        workflow_id = af.submit_ai_flow()
        af.get_ai_flow_client().publish_event('key', 'value1', 'name')
        time.sleep(5)
        af.get_ai_flow_client().publish_event('key', 'value2', 'name')
        time.sleep(10)
        af.stop_execution_by_id(workflow_id)
        res = af.get_ai_flow_client().list_job(5, 0)
        self.assertEqual(3, len(res))

    def test_user_define_control_dependency_1(self):
        print(sys._getframe().f_code.co_name)
        trigger = af.external_trigger(name='stream_trigger')
        job_config = af.BaseJobConfig('local', 'cmd_line')
        job_config.job_name = 'test_cmd'
        with af.config(job_config):
            cmd_executor = af.user_define_operation(output_num=0,
                                                    executor=CmdExecutor(
                                                        cmd_line="echo 'hello world' && sleep {}".format(2)))
        af.user_define_control_dependency(src=cmd_executor, dependency=trigger, event_key='key',
                                          event_value='value', event_type='name', condition=MetCondition.NECESSARY
                                          , action=TaskAction.RESTART, life=EventLife.ONCE,
                                          value_condition=MetValueCondition.UPDATE)
        workflow_id = af.submit_ai_flow()
        af.get_ai_flow_client().publish_event('key', 'value1', 'name')
        time.sleep(5)
        af.get_ai_flow_client().publish_event('key', 'value2', 'name')
        time.sleep(10)
        af.stop_execution_by_id(workflow_id)
        res = af.get_ai_flow_client().list_job(5, 0)
        self.assertEqual(3, len(res))

    def test_stream_with_external_trigger_with_model_control(self):
        print(sys._getframe().f_code.co_name)
        model_name = 'test_create_model_version'
        model_desc = 'test create model version'
        response = af.register_model(model_name=model_name, model_type=af.ModelType.CHECKPOINT,
                                     model_desc=model_desc)

        trigger = af.external_trigger(name='stream_trigger')
        job_config = af.BaseJobConfig('local', 'cmd_line')
        job_config.job_name = 'test_cmd'
        with af.config(job_config):
            cmd_executor = af.user_define_operation(output_num=0,
                                                    executor=CmdExecutor(
                                                        cmd_line="echo 'hello world' && sleep {}".format(1)))
        af.model_version_control_dependency(src=cmd_executor, dependency=trigger, model_name=model_name,
                                            model_version_event_type='MODEL_DEPLOYED')
        workflow_id = af.submit_ai_flow()

        model_path1 = 'fs://source1.pkl'
        model_metric1 = 'http://metric1'
        model_flavor1 = '{"flavor.version":1}'
        version_desc1 = 'test create model version1'
        time.sleep(1)
        response = af.register_model_version(model=model_name, model_path=model_path1,
                                             model_metric=model_metric1, model_flavor=model_flavor1,
                                             version_desc=version_desc1, current_stage=af.ModelVersionStage.DEPLOYED)
        time.sleep(5)
        response = af.register_model_version(model=model_name, model_path=model_path1,
                                             model_metric=model_metric1, model_flavor=model_flavor1,
                                             version_desc=version_desc1, current_stage=af.ModelVersionStage.DEPLOYED)
        time.sleep(10)
        af.stop_execution_by_id(workflow_id)
        res = af.get_ai_flow_client().list_job(5, 0)
        self.assertEqual(3, len(res))

    def test_project_register(self):
        print(sys._getframe().f_code.co_name)
        TestProject.build_ai_graph(1)
        af.register_dataset(name="a")
        w_id = af.submit_ai_flow()
        res = af.wait_workflow_execution_finished(w_id)
        self.assertEqual(0, res)
        e_meta = af.get_dataset_by_name("a")
        self.assertEqual("a", e_meta.name)

    def test_periodic_job(self):
        print(sys._getframe().f_code.co_name)
        periodic_config = PeriodicConfig(periodic_type='interval', args={'seconds': 5})
        job_config = af.BaseJobConfig(platform='local', engine='cmd_line')
        job_config.job_name = 'test_periodic'
        job_config.periodic_config = periodic_config
        with af.config(job_config):
            af.user_define_operation(executor=af.CmdExecutor(cmd_line="echo 'hello world!'"))
        workflow_id = af.submit_ai_flow()
        time.sleep(10)
        af.stop_execution_by_id(workflow_id)

    def test_stop_workflow_execution(self):
        print(sys._getframe().f_code.co_name)
        TestProject.build_ai_graph(5)
        exec_id = af.submit_ai_flow()
        self.assertGreater(exec_id, 0, "workflow execution id must greater than 0")
        time.sleep(3)
        res = af.stop_execution_by_id(exec_id)
        self.assertEqual(0, res[0])


if __name__ == '__main__':
    unittest.main()
