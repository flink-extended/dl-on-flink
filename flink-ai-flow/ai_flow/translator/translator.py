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
from abc import abstractmethod, ABC
from typing import Dict, Text, List
import copy
import time
import os
from ai_flow.ai_graph.ai_node import ReadDatasetNode, WriteDatasetNode
from ai_flow.context.workflow_config_loader import current_workflow_config
from ai_flow.workflow.workflow import Workflow
from ai_flow.workflow.job import Job
from ai_flow.ai_graph.ai_graph import AIGraph, AISubGraph
from ai_flow.ai_graph.data_edge import DataEdge
from ai_flow.workflow.control_edge import ControlEdge
from ai_flow.context.project_context import ProjectContext


class JobGenerator(ABC):
    """
    JobGenerator: Convert AISubGraph(ai_flow.ai_graph.ai_graph.AISubGraph) to Job(ai_flow.workflow.job.Job)
    """
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def generate(self, sub_graph: AISubGraph, resource_dir: Text = None) -> Job:
        """
        Convert AISubGraph(ai_flow.ai_graph.ai_graph.AISubGraph) to Job(ai_flow.workflow.job.Job)
        :param sub_graph: An executable Graph composed of AINode and data edges with the same job configuration.
        :param resource_dir: Store the executable files generated during the generation process.
        :return: Job(ai_flow.workflow.job.Job)
        """
        pass


class SplitGraph(AIGraph):
    def __init__(self) -> None:
        super().__init__()
        self.nodes: Dict[Text, AISubGraph] = {}
        self.edges: Dict[Text, List[ControlEdge]] = {}

    def add_node(self, node: AISubGraph):
        self.nodes[node.config.job_name] = node


class GraphSplitter(object):

    def __init__(self) -> None:
        super().__init__()

    def split(self, graph: AIGraph) -> SplitGraph:

        split_graph = SplitGraph()

        for n in graph.nodes.values():
            job_name = n.config.job_name
            if job_name in split_graph.nodes:
                sub_graph = split_graph.nodes.get(job_name)
            else:
                sub_graph = AISubGraph(config=n.config)
                split_graph.add_node(sub_graph)
            sub_graph.add_node(n)

        # add data edge to sub graph
        for sub_graph in split_graph.nodes.values():
            for n in sub_graph.nodes.values():
                if n.node_id in graph.edges:
                    for e in graph.edges[n.node_id]:
                        if isinstance(e, DataEdge):
                            sub_graph.add_edge(n.node_id, e)

        for e in graph.edges:
            for ee in graph.edges[e]:
                if isinstance(ee, ControlEdge):
                    split_graph.add_edge(ee.destination, ee)
        return split_graph


class WorkflowConstructor(object):
    class JobGeneratorRegistry(object):
        def __init__(self) -> None:
            super().__init__()
            self.object_dict: Dict[Text, JobGenerator] = {}

        def register(self, key: Text, value: JobGenerator):
            self.object_dict[key] = value

        def get_object(self, key: Text) -> JobGenerator:
            return self.object_dict[key]

    def __init__(self) -> None:
        super().__init__()
        self.job_generator_registry: WorkflowConstructor.JobGeneratorRegistry \
            = WorkflowConstructor.JobGeneratorRegistry()

    def register_job_generator(self, engine, generator: JobGenerator):
        self.job_generator_registry.register(engine, generator)

    def build_workflow(self, split_graph: SplitGraph, project_context: ProjectContext) -> Workflow:
        workflow = Workflow()
        workflow.workflow_config = current_workflow_config()
        workflow.workflow_snapshot_id = '{}.{}.{}'.format(project_context.project_name, workflow.workflow_name,
                                                          round(time.time() * 1000))
        # add ai_nodes to workflow
        for sub in split_graph.nodes.values():
            if sub.config.job_type not in self.job_generator_registry.object_dict:
                raise Exception("job generator not support job_type {}"
                                .format(sub.config.job_type))
            generator: JobGenerator = self.job_generator_registry \
                .get_object(sub.config.job_type)

            # set job resource dir
            job_resource_dir = os.path.join(project_context.get_generated_path(),
                                            workflow.workflow_snapshot_id,
                                            sub.config.job_name)
            if not os.path.exists(job_resource_dir):
                os.makedirs(job_resource_dir)

            job: Job = generator.generate(sub_graph=sub, resource_dir=job_resource_dir)
            job.resource_dir = job_resource_dir

            # set input output dataset
            for node in sub.nodes.values():
                if isinstance(node, ReadDatasetNode):
                    job.input_dataset_list.append(node.dataset())
                elif isinstance(node, WriteDatasetNode):
                    job.output_dataset_list.append(node.dataset())

            workflow.add_job(job)

        def validate_edge(head, tail):
            if head not in workflow.jobs:
                raise Exception('job: {} is not defined in workflow!'.format(head))
            if tail is not None and tail != '' and tail != '*' and tail not in workflow.jobs:
                raise Exception('job: {} is not defined in workflow!'.format(tail))
        # add edges to workflow
        for edges in split_graph.edges.values():
            for e in edges:
                control_edge = copy.deepcopy(e)
                validate_edge(control_edge.destination, control_edge.source)
                workflow.add_edge(control_edge.destination, control_edge)
        return workflow


class Translator(object):
    """
    Translator translates the user-defined program ai graph(ai_flow.ai_graph.ai_graph.AIGraph)
    into ai flow executable workflow(ai_flow.workflow.workflow.Workflow)
    """
    def __init__(self,
                 graph_splitter: GraphSplitter,
                 workflow_constructor: WorkflowConstructor
                 ) -> None:
        super().__init__()
        self.graph_splitter = graph_splitter
        self.workflow_constructor = workflow_constructor

    def translate(self, graph: AIGraph, project_context: ProjectContext) -> Workflow:
        """
        :param graph: The ai graph(ai_flow.ai_graph.ai_graph.AIGraph)
        :param project_context: The ai flow project context(ai_flow.context.project_context.ProjectContext)
        """
        split_graph = self.graph_splitter.split(graph=graph)
        workflow = self.workflow_constructor.build_workflow(split_graph=split_graph,
                                                            project_context=project_context)
        return workflow


__current_translator__ = Translator(graph_splitter=GraphSplitter(),
                                    workflow_constructor=WorkflowConstructor())


def get_translator() -> Translator:
    return __current_translator__


def register_job_generator(job_type, generator: JobGenerator) -> None:
    __current_translator__.workflow_constructor.register_job_generator(job_type, generator)
