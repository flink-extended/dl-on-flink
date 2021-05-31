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
import unittest

import ai_flow as af
from ai_flow.api.ai_flow_context import ENGINE_NAME
from ai_flow.common import path_util, json_utils
from ai_flow.graph.graph import _default_ai_graph
from ai_flow.test import test_util
from ai_flow.workflow.workflow_config import WorkFlowConfig


class ContextTests(unittest.TestCase):

    def test_context(self):
        global_config = af.BaseJobConfig(platform='a', engine='b', properties={'c': 'c'})
        job_config = af.BaseJobConfig(platform='aa', engine='bb', properties={'cc': 'cc'})
        with af.global_config(global_config):
            with af.config(job_config):
                af.user_define_operation(executor=None)
        node_list = list(_default_ai_graph.nodes.values())
        self.assertEqual('bb', node_list[0].properties[ENGINE_NAME])
        self.assertEqual('cc', node_list[0].config.properties["cc"])
        self.assertEqual('c', node_list[0].config.properties["c"])
        self.assertEqual('bb', node_list[0].config.engine)
        self.assertEqual('aa', node_list[0].config.platform)

    def test_context_with_file(self):
        config_file = path_util.get_file_dir(__file__) + "/workflow_config.json"

        def generate_workflow_config():
            workflow_config = WorkFlowConfig()
            workflow_config.add_job_config(config_key="global_config_key",
                                           job_config=af.BaseJobConfig(platform="local", engine="python",
                                                                       properties={"common_key": "common_value"}))
            workflow_config.add_job_config(config_key="test_job",
                                           job_config=af.BaseJobConfig(platform=None, engine=None,
                                                                       properties={"job_key": "job_value"}))
            workflow_config.add_job_config(config_key="test_job_1",
                                           job_config=af.BaseJobConfig(platform='kubernetes', engine='flink',
                                                                       properties={"job_key_1": "job_value_1"}))
            with open(config_file, 'w') as f:
                f.write(json_utils.dumps(workflow_config))

        generate_workflow_config()

        with af.global_config_file(config_path=config_file):
            with af.config(config="test_job") as cc:
                cc.properties['aa'] = 'aa'
                af.user_define_operation(executor=None)
            node_list = list(_default_ai_graph.nodes.values())
            self.assertEqual('python', node_list[len(node_list) - 1].properties[ENGINE_NAME])
            self.assertEqual('common_value', node_list[len(node_list) - 1].config.properties["common_key"])
            self.assertEqual('job_value', node_list[len(node_list) - 1].config.properties["job_key"])
            self.assertEqual('aa', node_list[len(node_list) - 1].config.properties["aa"])

            self.assertEqual('python', node_list[len(node_list) - 1].config.engine)
            self.assertEqual('local', node_list[len(node_list) - 1].config.platform)
            with af.config(config="test_job_1"):
                af.user_define_operation(executor=None)
            node_list = list(_default_ai_graph.nodes.values())
            self.assertEqual('flink', node_list[len(node_list) - 1].properties[ENGINE_NAME])
            self.assertEqual('common_value', node_list[len(node_list) - 1].config.properties["common_key"])
            self.assertEqual('job_value_1', node_list[len(node_list) - 1].config.properties["job_key_1"])
            self.assertEqual('flink', node_list[len(node_list) - 1].config.engine)
            self.assertEqual('kubernetes', node_list[len(node_list) - 1].config.platform)

    def test_context_with_yaml_file(self):
        config_file = path_util.get_file_dir(__file__) + "/workflow.yaml"
        with af.global_config_file(config_path=config_file) as g_config:
            with af.config('task_1') as config_1:
                self.assertEqual('task_1', config_1.job_name)
                self.assertEqual('cmd_line', config_1.engine)
                self.assertEqual('interval', config_1.periodic_config.periodic_type)
                self.assertEqual(20, config_1.periodic_config.args['seconds'])
            with af.config('task_2') as config_2:
                self.assertEqual('task_2', config_2.job_name)
                self.assertEqual('cmd_line', config_2.engine)
                self.assertEqual('cron', config_2.periodic_config.periodic_type)
                self.assertEqual('* * * * *', config_2.periodic_config.args)



if __name__ == '__main__':
    test_util.set_project_config(__file__)
    unittest.main()
