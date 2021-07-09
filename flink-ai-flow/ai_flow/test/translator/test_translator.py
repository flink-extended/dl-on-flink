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
from ai_flow.meta.dataset_meta import DatasetMeta
from ai_flow.ai_graph.ai_node import AINode, ReadDatasetNode, WriteDatasetNode
from ai_flow.workflow.control_edge import ConditionConfig
from ai_flow.workflow.job_config import JobConfig
from ai_flow.project.project_config import ProjectConfig
from ai_flow.context.workflow_config_loader import init_workflow_config
from ai_flow.translator.translator import *


def build_ai_graph(node_number, job_number) -> AIGraph:
    graph = AIGraph()
    for i in range(node_number):
        j = i % job_number
        config = JobConfig(job_name='job_{}'.format(j), job_type='mock')
        if 0 == i:
            ai_node = ReadDatasetNode(dataset=DatasetMeta(name='source'))
        elif 3 == i:
            ai_node = WriteDatasetNode(dataset=DatasetMeta(name='sink'))
        else:
            ai_node = AINode()
        ai_node.config = config
        graph.nodes[ai_node.node_id] = ai_node

    add_data_edge(graph=graph, to_='AINode_4', from_='ReadDatasetNode_0')
    add_data_edge(graph=graph, to_='AINode_4', from_='WriteDatasetNode_1')
    add_control_edge(graph, 'job_2', 'job_0')
    add_control_edge(graph, 'job_2', 'job_1')

    return graph


def add_data_edge(graph, to_, from_):
    graph.add_edge(to_, DataEdge(destination=to_, source=from_))


def add_control_edge(graph, job_name, upstream_job_name):
    graph.add_edge(job_name,
                   ControlEdge(destination=job_name,
                               condition_config=ConditionConfig(
                                   sender=upstream_job_name,
                                   event_key='',
                                   event_value='')))


class MockJobGenerator(JobGenerator):

    def generate(self, sub_graph: AISubGraph, resource_dir: Text = None) -> Job:
        return Job(job_config=sub_graph.config)


class TestTranslator(unittest.TestCase):

    def test_translate_ai_graph_to_workflow(self):
        init_workflow_config(os.path.join(os.path.dirname(__file__), 'workflow_1.yaml'))
        project_context = ProjectContext()
        project_context.project_path = '/tmp'
        project_context.project_config = ProjectConfig()
        project_context.project_config.set_project_name('test_project')
        graph: AIGraph = build_ai_graph(9, 3)
        splitter = GraphSplitter()
        split_graph = splitter.split(graph)
        self.assertEqual(3, len(split_graph.nodes))
        self.assertEqual(1, len(split_graph.edges))
        self.assertEqual(2, len(split_graph.edges.get('job_2')))
        sub_graph = split_graph.nodes.get('job_0')
        self.assertTrue('AINode_4' in sub_graph.nodes)
        self.assertTrue('AINode_4' in sub_graph.edges)
        constructor = WorkflowConstructor()
        constructor.register_job_generator('mock', MockJobGenerator())
        workflow = constructor.build_workflow(split_graph, project_context)
        self.assertEqual(3, len(workflow.nodes))
        job = workflow.jobs.get('job_0')
        self.assertEqual(1, len(job.input_dataset_list))
        self.assertEqual(1, len(job.output_dataset_list))


if __name__ == '__main__':
    unittest.main()
