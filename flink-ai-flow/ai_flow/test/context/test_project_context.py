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
import os

from ai_flow.util.path_util import get_file_dir

from ai_flow.context.project_context import init_project_context, current_project_config, build_project_context


class TestProjectContext(unittest.TestCase):

    def test_project_init_context(self):
        project_path = os.path.dirname(__file__)
        init_project_context(project_path)
        self.assertEqual('test_project', current_project_config().get_project_name())
        self.assertEqual('a', current_project_config().get('a'))

    def test_build_project_context(self):
        project_path = get_file_dir(__file__)
        project_context = build_project_context(project_path)
        self.assertTrue(project_context.get_project_config_file().endswith('project.yaml'))
        self.assertTrue(project_context.get_generated_path().endswith('generated'))
        self.assertTrue(project_context.get_workflows_path().endswith('workflows'))
        self.assertTrue(project_context.get_dependencies_path().endswith('dependencies'))
        self.assertTrue(project_context.get_python_dependencies_path().endswith('python'))
        self.assertTrue(project_context.get_go_dependencies_path().endswith('go'))
        self.assertTrue(project_context.get_jar_dependencies_path().endswith('jar'))
        self.assertTrue(project_context.get_resources_path().endswith('resources'))


if __name__ == '__main__':
    unittest.main()
