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

from ai_flow.project.project_description import get_project_description_from
from ai_flow.application_master.master import AIFlowMaster
from ai_flow.test import test_util
from ai_flow.workflow.job_config import PeriodicConfig
from ai_flow.graph.graph import default_graph
import ai_flow as af
from ai_flow.executor.executor import CmdExecutor
from ai_flow.translator.base_translator import *


def build_ai_graph_node(size) -> AIGraph:
    graph = AIGraph()
    for i in range(size):
        graph.add_node(AINode(name="name_" + str(i)))
    return graph


def add_data_edge(graph, src, target):
    nodes = []
    for n in graph.nodes.values():
        nodes.append(n)
    graph.add_edge(nodes[src].instance_id,
                   DataEdge(source_node_id=nodes[src].instance_id, target_node_id=nodes[target].instance_id))


def add_control_edge(graph, src, target):
    nodes = []
    for n in graph.nodes.values():
        nodes.append(n)
    graph.add_edge(nodes[src].instance_id,
                   ControlEdge(source_node_id=nodes[src].instance_id, target_node_id=nodes[target].instance_id))


class TestTranslator(unittest.TestCase):

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
        TestTranslator.master._clear_db()
        default_graph().clear_graph()

    def tearDown(self):
        TestTranslator.master._clear_db()

    def test_split_graph(self):
        def build_ai_graph() -> AIGraph:
            graph = AIGraph()
            for i in range(6):
                graph.add_node(AINode(name="name_" + str(i)))
            nodes = []
            for n in graph.nodes.values():
                nodes.append(n)

            graph.add_edge(nodes[2].instance_id,
                           DataEdge(source_node_id=nodes[2].instance_id, target_node_id=nodes[0].instance_id, port=0))
            graph.add_edge(nodes[2].instance_id,
                           DataEdge(source_node_id=nodes[2].instance_id, target_node_id=nodes[1].instance_id, port=0))
            graph.add_edge(nodes[4].instance_id,
                           ControlEdge(source_node_id=nodes[4].instance_id, target_node_id=nodes[2].instance_id))
            graph.add_edge(nodes[4].instance_id,
                           ControlEdge(source_node_id=nodes[4].instance_id, target_node_id=nodes[3].instance_id))
            return graph

        graph: AIGraph = build_ai_graph()
        splitter = DefaultGraphSplitter()
        graph = DefaultTranslator.optimize(graph)
        split_graph = splitter.split(graph, ProjectDesc())
        self.assertEqual(4, len(split_graph.nodes))
        self.assertEqual(1, len(split_graph.edges))
        for v in split_graph.edges.values():
            self.assertEqual(2, len(v))

    def test_split_ai_graph(self):
        def build_ai_graph() -> AIGraph:
            with af.engine('cmd_line'):
                p_list = []
                for i in range(3):
                    p = af.user_define_operation(
                        executor=CmdExecutor(cmd_line="echo 'hello_{}' && sleep 3".format(i)))
                    p_list.append(p)
                af.stop_before_control_dependency(p_list[0], p_list[1])
                af.stop_before_control_dependency(p_list[0], p_list[2])

            return af.default_graph()

        graph: AIGraph = build_ai_graph()
        splitter = DefaultGraphSplitter()
        split_graph = splitter.split(graph, ProjectDesc())
        self.assertEqual(3, len(split_graph.nodes))
        self.assertEqual(1, len(split_graph.edges))

    def test_optimize_graph(self):
        def build_ai_graph() -> AIGraph:
            """
            - or | data edge
            == or || control edge
                 11
                 ||
            12=0-1-2--3-5
               | |  | ||
               | 13 4--6
               |      ||
               7-8====9

            10

            """
            graph = build_ai_graph_node(14)

            add_data_edge(graph, 1, 0)
            add_data_edge(graph, 2, 1)
            add_data_edge(graph, 3, 2)
            add_data_edge(graph, 4, 2)
            add_data_edge(graph, 5, 3)
            add_data_edge(graph, 6, 4)
            add_data_edge(graph, 7, 0)
            add_data_edge(graph, 8, 7)
            add_data_edge(graph, 13, 1)

            add_control_edge(graph, 6, 3)
            add_control_edge(graph, 9, 6)
            add_control_edge(graph, 8, 9)
            add_control_edge(graph, 11, 1)
            add_control_edge(graph, 0, 12)

            return graph

        graph: AIGraph = build_ai_graph()
        g = DefaultTranslator.optimize(graph)
        cluster_graph = build_cluster_graph(g)

        self.assertEqual(18, len(g.nodes))
        self.assertEqual(7, len(cluster_graph.cluster_dict))
        node_list_name_0 = []
        for n in graph.nodes.values():
            if n.name == "name_0":
                node_list_name_0.append(n)
        self.assertEqual(3, len(node_list_name_0))
        for n in node_list_name_0:
            es = graph.edges[n.instance_id]
            self.assertEqual(1, len(es))
            self.assertEqual("name_12", graph.nodes[es[0].target_node_id].name)

    def test_compute_cluster_graph_1(self):
        def build_ai_graph() -> AIGraph:
            graph = build_ai_graph_node(5)
            add_data_edge(graph, 1, 0)
            add_data_edge(graph, 2, 1)
            add_data_edge(graph, 3, 0)
            add_data_edge(graph, 4, 3)
            add_control_edge(graph, 4, 2)
            return graph

        graph: AIGraph = build_ai_graph()

        has_circle, do_split, err_message = DefaultTranslator.compute_cluster_graph(graph)
        self.assertTrue(has_circle)
        self.assertTrue(do_split)
        cluster_graph = build_cluster_graph(graph)
        self.assertEqual(2, len(cluster_graph.cluster_dict))

    def test_compute_cluster_graph_2(self):
        def build_ai_graph() -> AIGraph:
            graph = build_ai_graph_node(6)
            add_data_edge(graph, 1, 0)
            add_data_edge(graph, 2, 1)
            add_data_edge(graph, 3, 0)
            add_data_edge(graph, 4, 3)
            add_control_edge(graph, 5, 2)
            add_control_edge(graph, 4, 5)

            return graph

        graph: AIGraph = build_ai_graph()

        has_circle, do_split, err_message = DefaultTranslator.compute_cluster_graph(graph)
        self.assertTrue(has_circle)
        self.assertTrue(do_split)
        cluster_graph = build_cluster_graph(graph)
        self.assertEqual(3, len(cluster_graph.cluster_dict))

    def test_compute_cluster_graph_3(self):
        def build_ai_graph() -> AIGraph:
            graph = build_ai_graph_node(6)
            add_data_edge(graph, 1, 0)
            add_data_edge(graph, 2, 1)
            add_data_edge(graph, 3, 0)
            add_data_edge(graph, 4, 3)
            add_control_edge(graph, 5, 2)
            add_control_edge(graph, 4, 5)
            add_control_edge(graph, 3, 1)
            return graph

        graph: AIGraph = build_ai_graph()

        has_circle, do_split, err_message = DefaultTranslator.compute_cluster_graph(graph)
        self.assertTrue(has_circle)
        self.assertTrue(do_split)
        cluster_graph = build_cluster_graph(graph)
        self.assertEqual(3, len(cluster_graph.cluster_dict))

    def test_compute_cluster_graph_4(self):
        def build_ai_graph() -> AIGraph:
            graph = build_ai_graph_node(6)
            add_data_edge(graph, 1, 0)
            add_data_edge(graph, 2, 1)
            add_data_edge(graph, 3, 0)
            add_data_edge(graph, 4, 3)
            add_control_edge(graph, 5, 2)
            add_control_edge(graph, 4, 5)
            add_control_edge(graph, 2, 3)
            return graph

        graph: AIGraph = build_ai_graph()

        has_circle, do_split, err_message = DefaultTranslator.compute_cluster_graph(graph)
        self.assertTrue(has_circle)
        self.assertTrue(do_split)
        cluster_graph = build_cluster_graph(graph)
        self.assertEqual(3, len(cluster_graph.cluster_dict))
        self.assertTrue(True, cluster_graph.has_circle())

    def test_compute_cluster_graph_5(self):
        def build_ai_graph() -> AIGraph:
            graph = build_ai_graph_node(8)
            add_data_edge(graph, 1, 0)
            add_data_edge(graph, 2, 1)
            add_data_edge(graph, 3, 0)
            add_data_edge(graph, 4, 3)
            add_data_edge(graph, 5, 0)
            add_data_edge(graph, 6, 1)
            add_data_edge(graph, 7, 6)
            add_control_edge(graph, 4, 2)
            return graph

        graph: AIGraph = build_ai_graph()

        has_circle, do_split, err_message = DefaultTranslator.compute_cluster_graph(graph)
        self.assertTrue(has_circle)
        self.assertTrue(do_split)
        cluster_graph = build_cluster_graph(graph)
        self.assertEqual(2, len(cluster_graph.cluster_dict))
        self.assertEqual(9, len(graph.nodes))
        self.assertFalse(cluster_graph.has_circle())

    def test_compute_cluster_graph_6(self):
        def build_ai_graph() -> AIGraph:
            graph = build_ai_graph_node(8)
            add_data_edge(graph, 1, 0)
            add_data_edge(graph, 2, 0)
            add_data_edge(graph, 3, 1)
            add_data_edge(graph, 3, 2)

            add_data_edge(graph, 5, 4)
            add_data_edge(graph, 6, 4)
            add_data_edge(graph, 7, 5)
            add_data_edge(graph, 7, 6)
            add_control_edge(graph, 5, 1)
            add_control_edge(graph, 2, 6)

            return graph

        graph: AIGraph = build_ai_graph()

        has_circle, do_split, err_message = DefaultTranslator.compute_cluster_graph(graph)
        self.assertTrue(has_circle)
        self.assertFalse(do_split)
        cluster_graph = build_cluster_graph(graph)

    def test_compute_cluster_graph_7(self):
        def build_ai_graph() -> AIGraph:
            graph = build_ai_graph_node(4)
            add_data_edge(graph, 1, 0)
            add_data_edge(graph, 2, 1)
            add_data_edge(graph, 2, 0)
            add_data_edge(graph, 3, 0)
            add_control_edge(graph, 3, 1)
            return graph

        graph: AIGraph = build_ai_graph()

        has_circle, do_split, err_message = DefaultTranslator.compute_cluster_graph(graph)
        self.assertTrue(has_circle)
        self.assertTrue(do_split)
        cluster_graph = build_cluster_graph(graph)
        self.assertEqual(2, len(cluster_graph.cluster_dict))
        res = set()
        for n in graph.nodes.values():
            if n.name == "name_2":
                n2 = n
        for e in graph.edges[n2.instance_id]:
            res.add(e.target_node_id)

        self.assertTrue("AINode_4" in res)

    def test_compute_cluster_graph_8(self):
        def build_ai_graph() -> AIGraph:
            graph = build_ai_graph_node(5)
            add_data_edge(graph, 1, 0)
            add_data_edge(graph, 2, 1)
            add_data_edge(graph, 3, 1)
            add_data_edge(graph, 4, 3)
            add_control_edge(graph, 2, 3)
            add_control_edge(graph, 4, 1)
            return graph

        graph: AIGraph = build_ai_graph()
        exception_flag = False
        try:
            graph = DefaultTranslator.optimize(graph)
        except Exception as e:
            exception_flag = True
        self.assertTrue(True, exception_flag)

    def test_compute_cluster_graph_9(self):
        def build_ai_graph() -> AIGraph:
            graph = build_ai_graph_node(5)
            add_data_edge(graph, 2, 0)
            add_data_edge(graph, 2, 1)
            add_data_edge(graph, 3, 2)
            add_data_edge(graph, 4, 2)
            add_control_edge(graph, 1, 0)
            add_control_edge(graph, 3, 4)
            return graph

        graph: AIGraph = build_ai_graph()
        exception_flag = False
        try:
            DefaultTranslator.optimize(graph)
        except Exception as e:
            exception_flag = True
        self.assertTrue(True, exception_flag)

    def test_periodic_job(self):
        periodic_config = PeriodicConfig(periodic_type='interval', args={'seconds': 5})
        job_config = af.BaseJobConfig(platform='local', engine='cmd_line')
        job_config.job_name = 'test_periodic'
        job_config.periodic_config = periodic_config
        with af.config(job_config):
            job = af.user_define_operation(executor=af.CmdExecutor(cmd_line="echo 'hello world!'"))

        job_config_2 = af.BaseJobConfig(platform='local', engine='cmd_line')
        job_config_2.job_name = 'test_job'
        with af.config(job_config_2):
            job2 = af.user_define_operation(executor=af.CmdExecutor(cmd_line="echo 'hello world!'"))

        af.user_define_control_dependency(job2, job, event_key='a', event_value='b')

        workflow = get_default_translator().translate(graph=default_graph(),
                                                      project_desc=get_project_description_from(
                                                          test_util.get_project_path()))
        self.assertIsNotNone(workflow.jobs['LocalCMDJob_0'].job_config.periodic_config)

    def test_not_validated_periodic_job(self):
        periodic_config = PeriodicConfig(periodic_type='interval', args={'seconds': 5})
        job_config_1 = af.BaseJobConfig(platform='local', engine='cmd_line')
        job_config_1.job_name = 'test_periodic_1'
        job_config_1.periodic_config = periodic_config
        with af.config(job_config_1):
            job1 = af.user_define_operation(executor=af.CmdExecutor(cmd_line="echo 'hello world!'"))

        job_config_2 = af.BaseJobConfig(platform='local', engine='cmd_line')
        job_config_2.job_name = 'test_job'
        with af.config(job_config_2):
            job2 = af.user_define_operation(executor=af.CmdExecutor(cmd_line="echo 'hello world!'"))

        af.user_define_control_dependency(job1, job2, event_key='a', event_value='b')
        with self.assertRaises(Exception) as context:
            workflow = get_default_translator().translate(graph=default_graph(),
                                                          project_desc=get_project_description_from(
                                                              test_util.get_project_path()))
            self.assertTrue('Periodic job' in context.exception)


if __name__ == '__main__':
    unittest.main()
