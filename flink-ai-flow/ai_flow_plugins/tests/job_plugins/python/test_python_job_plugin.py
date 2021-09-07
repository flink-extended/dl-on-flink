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

from ai_flow_plugins.job_plugins.bash.bash_processor import BashProcessor

from ai_flow.ai_graph.ai_node import AINode

from ai_flow.workflow.job_config import JobConfig

from ai_flow.ai_graph.ai_graph import AISubGraph
from ai_flow_plugins.job_plugins.python import PythonProcessor

from ai_flow_plugins.job_plugins.python.python_job_plugin import PythonJobGenerator, PythonJob


class TestPythonJobGenerator(unittest.TestCase):
    def test_generate_invalid_subgraph_raise_exception(self):
        sub_graph = AISubGraph(JobConfig())
        ai_node = AINode(processor=BashProcessor('hello'))
        sub_graph.add_node(ai_node)
        sub_graph.add_node(AINode(processor=PythonProcessor()))
        python_job_generator = PythonJobGenerator()

        with self.assertRaises(Exception):
            python_job_generator.generate(sub_graph)

    def test_generate(self):
        sub_graph = AISubGraph(JobConfig())
        sub_graph.add_node(AINode(processor=PythonProcessor()))
        sub_graph.add_node(AINode(processor=PythonProcessor()))
        python_job_generator = PythonJobGenerator()

        job = python_job_generator.generate(sub_graph)
        self.assertIsInstance(job, PythonJob)

