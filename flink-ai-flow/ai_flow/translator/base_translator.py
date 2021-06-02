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
from ai_flow.common.time_utils import generate_time_str
from ai_flow.meta.job_meta import State, ExecutionMode
from ai_flow.rest_endpoint.service.client.aiflow_client import AIFlowClient
from ai_flow.api.configuration import project_config
from ai_flow.meta.workflow_execution_meta import WorkflowExecutionMeta
from ai_flow.workflow.workflow import Workflow
from ai_flow.workflow.job import BaseJob, BaseJobConfig
from ai_flow.graph.graph import AIGraph, SplitGraph, AISubGraph
from ai_flow.graph.ai_node import AINode
from ai_flow.api.ai_flow_context import ENGINE_NAME
from ai_flow.graph.edge import ControlEdge, DataEdge, JobControlEdge, control_edge_to_job_edge
from ai_flow.common.json_utils import dumps
from ai_flow.project.project_description import ProjectDesc
from ai_flow.common.json_utils import Jsonable
from typing import Dict, Text, List, Set, Tuple, Optional
from abc import ABC, abstractmethod
import queue
import copy


class BaseTranslator(ABC):
    @abstractmethod
    def translate(self, graph: AIGraph, project_desc: ProjectDesc) -> Workflow:
        pass


class BaseGraphSplitter(ABC):
    @abstractmethod
    def split(self, graph: AIGraph, project_desc: ProjectDesc) -> SplitGraph:
        pass


class BaseJobGenerator(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def generate(self, sub_graph: AISubGraph, project_desc: ProjectDesc) -> BaseJob:
        pass

    def generate_job_resource(self, job: BaseJob) -> None:
        pass


class BaseWorkflowConstructor(ABC):
    @abstractmethod
    def build_workflow(self, split_graph: SplitGraph, project_desc: ProjectDesc) -> Workflow:
        pass


def compute_data_edges(graph: AIGraph) -> Dict[Text, List[Text]]:
    res: Dict[Text, List[Text]] = {}
    for es in graph.edges:
        for e in graph.edges[es]:
            if not isinstance(e, ControlEdge):
                if es not in res:
                    res[es] = []
                res[es].append(e.target_node_id)
    return res


def compute_r_data_edges(graph: AIGraph) -> Dict[Text, List[Text]]:
    res: Dict[Text, List[Text]] = {}
    for es in graph.edges:
        for e in graph.edges[es]:
            if not isinstance(e, ControlEdge):
                if e.target_node_id not in res:
                    res[e.target_node_id] = []
                res[e.target_node_id].append(es)
    return res


def generate_set_key(my_set: Set[Text]) -> Text:
    sorted_list = sorted(list(my_set))
    return sorted_list[0]


class DefaultGraphSplitter(BaseGraphSplitter):

    def __init__(self) -> None:
        super().__init__()

    def split(self, graph: AIGraph, project_desc: ProjectDesc) -> SplitGraph:

        edges = compute_data_edges(graph=graph)

        r_edges = compute_r_data_edges(graph=graph)

        split_graph = SplitGraph()

        def validate_engine_type(ai_sub_graph: AISubGraph):
            if len(ai_sub_graph.nodes) <= 0:
                raise Exception("AISubGraph is Empty!")
            nodes = list(ai_sub_graph.nodes.values())
            engine_name = nodes[0].properties[ENGINE_NAME]
            for node in ai_sub_graph.nodes.values():
                engine = node.properties[ENGINE_NAME]
                if engine_name != engine:
                    raise Exception("AISubGraph engine name not same:{}!={} graph:{}"
                                    .format(engine_name, engine, dumps(ai_sub_graph)))
            ai_sub_graph.job_type = engine_name

        # add node to subGraph
        node_set: Set[Text] = set()
        for n in graph.nodes.values():
            if n.instance_id in node_set:
                continue
            else:
                node_id_to_sub_id = {}
                tmp_sub = AISubGraph(config=n.config)
                tmp_sub.add_node(n)
                q = queue.Queue()
                q.put(n)
                node_set.add(n.instance_id)
                # add depends to sub graph
                while not q.empty():
                    nn = q.get()
                    if nn.instance_id in edges:
                        for e in edges[nn.instance_id]:
                            tmp_node = graph.get_node_by_id(e)
                            if not tmp_sub.is_in_graph(tmp_node.instance_id):
                                tmp_sub.add_node(tmp_node)
                            if e not in node_set:
                                q.put(tmp_node)
                                node_set.add(e)
                            node_id_to_sub_id[tmp_node.instance_id] = tmp_sub.instance_id
                    if nn.instance_id in r_edges:
                        for e in r_edges[nn.instance_id]:
                            tmp_node = graph.get_node_by_id(e)
                            if not tmp_sub.is_in_graph(tmp_node.instance_id):
                                tmp_sub.add_node(tmp_node)
                            if e not in node_set:
                                q.put(tmp_node)
                                node_set.add(e)
                            node_id_to_sub_id[tmp_node.instance_id] = tmp_sub.instance_id

                # set AISubGraph engine name and validate AISubGraph ai_nodes in same engine name
                validate_engine_type(tmp_sub)

                split_graph.add_node(tmp_sub)

        # add data edge to sub graph
        for sub_graph in split_graph.nodes.values():
            for n in sub_graph.nodes.values():
                if n.instance_id in graph.edges:
                    for e in graph.edges[n.instance_id]:
                        if isinstance(e, DataEdge):
                            sub_graph.add_edge(n.instance_id, e)

        # add control edge to split graph
        def get_sub_graph_by_node_id(node_id: Text) -> AISubGraph:
            for sg in split_graph.nodes.values():
                if sg.is_in_graph(node_id):
                    return sg
            return None

        for e in graph.edges:
            sub = get_sub_graph_by_node_id(e)
            for ee in graph.edges[e]:
                if isinstance(ee, ControlEdge):
                    tmp = get_sub_graph_by_node_id(ee.target_node_id)
                    tmp_edge = copy.deepcopy(ee)
                    tmp_edge.target_node_id = tmp.instance_id
                    tmp_edge.source_node_id = sub.instance_id
                    split_graph.add_edge(sub.instance_id, tmp_edge)
        return split_graph


class DefaultWorkflowConstructor(BaseWorkflowConstructor):
    class JobGeneratorRegistry(object):
        def __init__(self) -> None:
            super().__init__()
            self.object_dict: Dict[Tuple[Text, Text], BaseJobGenerator] = {}

        def register(self, key: Tuple[Text, Text], value: BaseJobGenerator):
            self.object_dict[key] = value

        def get_object(self, key: Tuple[Text, Text]) -> BaseJobGenerator:
            return self.object_dict[key]

    def __init__(self) -> None:
        super().__init__()
        self.job_generator_registry: DefaultWorkflowConstructor.JobGeneratorRegistry \
            = DefaultWorkflowConstructor.JobGeneratorRegistry()
        self.client: AIFlowClient = None

    def get_client(self):
        self.client = AIFlowClient(server_uri=project_config().get_master_uri())
        return self.client

    def register_job_generator(self, platform, engine, generator: BaseJobGenerator):
        self.job_generator_registry.register((platform, engine), generator)

    def register_workflow_execution(self, workflow: Workflow):
        exec_name = generate_time_str()
        workflow_meta: WorkflowExecutionMeta = self.get_client().register_workflow_execution(
            name=exec_name,
            project_id=int(workflow.project_desc.project_config.get_project_uuid()),
            execution_state=State.INIT,
            workflow_json=dumps(workflow))
        workflow.workflow_id = workflow_meta.uuid
        workflow.execution_name = exec_name

        # set workflow execution id to job context
        for job in workflow.jobs.values():
            job.job_context.workflow_execution_id = workflow_meta.uuid

    def build_workflow(self, split_graph: SplitGraph, project_desc: ProjectDesc) -> Workflow:
        sub_id_to_job_id = {}
        workflow = Workflow()
        workflow.project_desc = project_desc
        # add ai_nodes to workflow
        for sub in split_graph.nodes.values():
            if (sub.config.platform, sub.config.engine) not in self.job_generator_registry.object_dict:
                raise Exception("job generator not support platform {} engine {}"
                                .format(sub.config.platform, sub.config.engine))
            generator: BaseJobGenerator = self.job_generator_registry \
                .get_object((sub.config.platform, sub.config.engine))
            job: BaseJob = generator.generate(sub_graph=sub, project_desc=project_desc)
            job.job_config.project_desc = project_desc
            if job.job_name is None:
                job.job_name = job.job_config.job_name
            workflow.add_job(job)
            sub_id_to_job_id[sub.instance_id] = job.instance_id
        # add edges to workflow
        for edges in split_graph.edges.values():
            for e in edges:
                control_edge = copy.deepcopy(e)
                control_edge.source_node_id = sub_id_to_job_id[e.source_node_id]
                control_edge.target_node_id = sub_id_to_job_id[e.target_node_id]
                job_edge: JobControlEdge = control_edge_to_job_edge(control_edge=control_edge)
                workflow.add_edge(sub_id_to_job_id[e.source_node_id], job_edge)

        self.register_workflow_execution(workflow)

        for job in workflow.jobs.values():
            job.job_config.project_path = project_desc.project_path
            if job.job_config.exec_mode is None:
                job.job_config.exec_mode = ExecutionMode.BATCH
            generator: BaseJobGenerator = self.job_generator_registry \
                .get_object((job.platform, job.exec_engine))
            generator.generate_job_resource(job)
        return workflow


def compute_control_edges(graph: AIGraph) -> Dict[Text, List[Text]]:
    res: Dict[Text, List[Text]] = {}
    for es in graph.edges:
        for e in graph.edges[es]:
            if isinstance(e, ControlEdge):
                if es not in res:
                    res[es] = []
                res[es].append(e.target_node_id)
    return res


def compute_r_control_edges(graph: AIGraph) -> Dict[Text, List[Text]]:
    res: Dict[Text, List[Text]] = {}
    for es in graph.edges:
        for e in graph.edges[es]:
            if isinstance(e, ControlEdge):
                if e.target_node_id not in res:
                    res[e.target_node_id] = []
                res[e.target_node_id].append(es)
    return res


def compute_control_nodes(graph: AIGraph) -> Set[Text]:
    res: Set = set()
    for es in graph.edges:
        for e in graph.edges[es]:
            if isinstance(e, ControlEdge):
                res.add(e.source_node_id)
                res.add(e.target_node_id)
    return res


class ClusterGraph(Jsonable):
    def __init__(self) -> None:
        # key: cluster name, value: nodes
        self.cluster_dict: Dict[Text, Set[Text]] = {}
        self.cluster_edges: Dict[Text, Set[Text]] = {}
        self.node_cluster_index: Dict[Text, Text] = {}
        self.can_not_split_cluster: Set[Text] = set()
        # key cluster name, value: node_names
        self.display_cluster: Dict[Text, Set[Text]] = {}
        self.edges: Dict[Text, List[Text]] = {}
        self.r_edges: Dict[Text, List[Text]] = {}
        self.control_edges: Dict[Text, List[Text]] = {}
        self.r_control_edges: Dict[Text, List[Text]] = {}

    def update_self(self):
        self.compute_node_cluster_index()

    def compute_node_cluster_index(self):
        for c in self.cluster_dict:
            for n in self.cluster_dict[c]:
                self.node_cluster_index[n] = c

    def find_all_dependencies(self, cluster) -> Set[Text]:
        res = set()
        q = queue.Queue()
        q.put(cluster)

        while not q.empty():
            c = q.get()
            if c in self.cluster_edges:
                for target in self.cluster_edges[c]:
                    if target not in res:
                        res.add(target)
                        q.put(target)

        return res

    def has_circle(self) -> bool:
        for cluster_id in self.cluster_dict:
            deps = self.find_all_dependencies(cluster_id)
            if cluster_id in deps:
                return True
        return False


def build_cluster_graph(graph: AIGraph) -> ClusterGraph:
    cluster_graph = ClusterGraph()
    edges = compute_data_edges(graph=graph)
    r_edges = compute_r_data_edges(graph=graph)
    control_edges = compute_control_edges(graph=graph)
    r_control_edges = compute_r_control_edges(graph=graph)
    cluster_graph.edges = edges
    cluster_graph.r_edges = r_edges
    cluster_graph.control_edges = control_edges
    cluster_graph.r_control_edges = r_control_edges

    def compute_data_cluster(node_instance_id: Text) -> Set[Text]:
        node_set: Set[Text] = set()
        q = queue.Queue()
        node_set.add(node_instance_id)
        q.put(node_instance_id)
        while not q.empty():
            tmp_node_id = q.get()
            if tmp_node_id in edges:
                for e in edges[tmp_node_id]:
                    if e not in node_set:
                        q.put(e)
                        node_set.add(e)

            if tmp_node_id in r_edges:
                for e in r_edges[tmp_node_id]:
                    if e not in node_set:
                        q.put(e)
                        node_set.add(e)
        return node_set

    # key node|...
    # value node list
    # init cluster graph
    # 1. init nodes
    for node in graph.nodes.values():
        node_cluster = compute_data_cluster(node_instance_id=node.instance_id)
        cluster_graph.cluster_dict[generate_set_key(node_cluster)] = node_cluster
    cluster_graph.update_self()

    # 2. init edges
    for src in control_edges:
        for target in control_edges[src]:
            src_cluster = cluster_graph.node_cluster_index[src]
            target_cluster = cluster_graph.node_cluster_index[target]
            if src_cluster not in cluster_graph.cluster_edges:
                cluster_graph.cluster_edges[src_cluster] = set()
            cluster_graph.cluster_edges[src_cluster].add(target_cluster)

    # 3. set display cluster
    for c in cluster_graph.cluster_dict:
        for n in cluster_graph.cluster_dict[c]:
            if c not in cluster_graph.display_cluster:
                cluster_graph.display_cluster[c] = set()
            cluster_graph.display_cluster[c].add(graph.nodes.get(n).name)

    return cluster_graph


class DefaultTranslator(BaseTranslator):
    def __init__(self,
                 graph_splitter: BaseGraphSplitter,
                 workflow_constructor: BaseWorkflowConstructor
                 ) -> None:
        super().__init__()
        self.graph_splitter = graph_splitter
        self.workflow_constructor = workflow_constructor

    @staticmethod
    def compute_cluster_graph(graph: AIGraph) -> Tuple[bool, bool, Optional[Set]]:
        cluster_graph: ClusterGraph = build_cluster_graph(graph)
        edges = cluster_graph.edges
        r_edges = cluster_graph.r_edges
        control_edges = cluster_graph.control_edges
        r_control_edges = cluster_graph.r_control_edges

        def compute_before_data_cluster(node_instance_id: Text) -> Set[Text]:
            node_set: Set[Text] = set()
            q = queue.Queue()
            node_set.add(node_instance_id)
            q.put(node_instance_id)
            while not q.empty():
                tmp_node_id = q.get()
                if tmp_node_id in edges:
                    for e in edges[tmp_node_id]:
                        if e not in node_set:
                            q.put(e)
                            node_set.add(e)
            return node_set

        def compute_after_data_cluster(node_instance_id: Text) -> Set[Text]:
            node_set: Set[Text] = set()
            q = queue.Queue()
            node_set.add(node_instance_id)
            q.put(node_instance_id)
            while not q.empty():
                tmp_node_id = q.get()
                if tmp_node_id in r_edges:
                    for e in r_edges[tmp_node_id]:
                        if e not in node_set:
                            q.put(e)
                            node_set.add(e)
            return node_set

        def cluster_can_split(src_node, target_node) -> bool:
            """
            :param src_node:  cluster source node
            :param target_node: cluster target node
            :return:
            """
            src_set = compute_after_data_cluster(src_node)
            target_set = compute_after_data_cluster(target_node)
            if len(src_set.intersection(target_set)) == 0:
                return True
            else:
                return False

        def rewrite_ai_graph(src_node, target_node):
            def get_control_edge(src_node_id, target_node_id) -> Optional[ControlEdge]:
                es = graph.edges[src_node_id]
                for e in es:
                    if isinstance(e, ControlEdge) and e.target_node_id == target_node_id:
                        return e
                return None

            def get_data_edge(src_node_id, target_node_id) -> Optional[DataEdge]:
                es = graph.edges[src_node_id]
                for e in es:
                    if isinstance(e, DataEdge) and e.target_node_id == target_node_id:
                        return e
                return None

            src_before_set: Set[Text] = compute_before_data_cluster(src_node)
            target_before_set: Set[Text] = compute_before_data_cluster(target_node)
            res: Set[Text] = src_before_set.intersection(target_before_set)
            id_pair: Dict[Text, Text] = {}
            # copy the intersection node and edges
            for node_id in res:
                node: AINode = graph.get_node_by_id(node_id=node_id)
                copy_node = copy.deepcopy(node)
                graph.add_node(copy_node)
                id_pair[node_id] = copy_node.instance_id
            # change target set node edge to copy node
            # 1. copy control edges
            for node_id in res:
                if node_id in control_edges:
                    for e in control_edges[node_id]:
                        org_edge = get_control_edge(node_id, e)
                        copy_edge = copy.deepcopy(org_edge)
                        copy_edge.source_node_id = id_pair[node_id]
                        if e in id_pair:
                            copy_edge.target_node_id = id_pair[e]
                        else:
                            pass
                        graph.add_edge(copy_edge.source_node_id, copy_edge)

                if node_id in r_control_edges:
                    for e in r_control_edges[node_id]:
                        org_edge = get_control_edge(e, node_id)
                        copy_edge = copy.deepcopy(org_edge)
                        copy_edge.target_node_id = id_pair[node_id]
                        if e in id_pair:
                            copy_edge.source_node_id = id_pair[e]
                        else:
                            pass
                        graph.add_edge(copy_edge.source_node_id, copy_edge)

            # 2. copy data edge
            target_after_set: Set[Text] = compute_after_data_cluster(target_node)
            for node_id in res:
                if node_id in edges:
                    for e in edges[node_id]:
                        # e must in res
                        org_edge = get_data_edge(node_id, e)
                        copy_edge = copy.deepcopy(org_edge)
                        copy_edge.source_node_id = id_pair[node_id]
                        if e in id_pair:
                            copy_edge.target_node_id = id_pair[e]
                        graph.add_edge(copy_edge.source_node_id, copy_edge)

                if node_id in r_edges:
                    for e in r_edges[node_id]:
                        if e in target_before_set or e in target_after_set:
                            org_edge = get_data_edge(e, node_id)
                            copy_edge = copy.deepcopy(org_edge)
                            if e in id_pair:
                                # add this edge in edges
                                continue
                            else:
                                graph.edges[e].remove(org_edge)
                            copy_edge.target_node_id = id_pair[node_id]
                            graph.add_edge(copy_edge.source_node_id, copy_edge)

        def find_a_tuple_circle_node(cluster_id) -> Tuple[Optional[Text], Optional[Text]]:
            node_set = cluster_graph.cluster_dict[cluster_id]

            for n in node_set:
                if n in edges:
                    res = set()
                    q = queue.Queue()
                    q.put(n)
                    while not q.empty():
                        c = q.get()
                        if c in control_edges:
                            for target in control_edges[c]:
                                if target in node_set:
                                    # check if can split
                                    if cluster_can_split(n, target):
                                        return n, target
                                    else:
                                        continue
                                else:
                                    if target not in res:
                                        res.add(target)
                                        q.put(target)
            return None, None

        # check graph has circle
        has_circle = False
        do_split = False
        for cluster_id in cluster_graph.cluster_dict.keys():
            if cluster_id in cluster_graph.cluster_edges:
                all_dependencies = cluster_graph.find_all_dependencies(cluster_id)
                # need to split
                if cluster_id in all_dependencies:
                    has_circle = True
                    if cluster_id not in cluster_graph.can_not_split_cluster:
                        # find circle edge and split
                        src, target = find_a_tuple_circle_node(cluster_id)
                        if src is None:
                            cluster_graph.can_not_split_cluster.add(cluster_id)
                        else:
                            rewrite_ai_graph(src, target)
                            do_split = True
                            break
                    else:
                        pass
                else:
                    # do not have circle so do not need split
                    pass
            else:
                # no dependencies so do not need split
                pass
        if has_circle and not do_split:
            return has_circle, do_split, cluster_graph.can_not_split_cluster
        else:
            return has_circle, do_split, None

    @staticmethod
    def optimize(graph: AIGraph) -> AIGraph:
        """
        rewrite AIGraph copy the node belong to different sub graph
        :param graph: Default AIGraph
        :return:
        """
        has_circle = True
        while has_circle:
            has_circle, do_split, err_message = DefaultTranslator.compute_cluster_graph(graph)
            if has_circle and not do_split:
                raise Exception("{} cluster has circle".format(dumps(err_message)))

        return graph

    def translate(self, graph: AIGraph, project_desc: ProjectDesc) -> Workflow:
        optimized_graph = self.optimize(graph=graph)
        split_graph = self.graph_splitter.split(graph=optimized_graph,
                                                project_desc=project_desc)
        workflow = self.workflow_constructor.build_workflow(split_graph=split_graph,
                                                            project_desc=project_desc)
        self.check_periodic_job_validated(workflow)
        return workflow

    def check_periodic_job_validated(self, workflow: Workflow):
        for node_id, job in workflow.jobs.items():
            job_config: BaseJobConfig = job.job_config
            if job_config.periodic_config is not None:
                if node_id in workflow.edges:
                    raise Exception('Periodic job: {} can not have upstream job or upstream event.'
                                    .format(job.job_name))


_default_graph_splitter = DefaultGraphSplitter()
_default_workflow_constructor = DefaultWorkflowConstructor()
_default_translator = DefaultTranslator(graph_splitter=_default_graph_splitter,
                                        workflow_constructor=_default_workflow_constructor)


def get_default_translator() -> BaseTranslator:
    return _default_translator


def register_job_generator(platform, engine, generator: BaseJobGenerator) -> None:
    _default_workflow_constructor.register_job_generator(platform, engine, generator)
