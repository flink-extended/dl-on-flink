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
import getopt
import json
import sys
from logging.config import dictConfig
from typing import List, Dict

from flask import Flask, request
from flask_cors import CORS
from werkzeug.local import LocalProxy

from ai_flow import WorkflowMeta
from ai_flow.ai_graph.ai_graph import AIGraph
from ai_flow.ai_graph.ai_node import AINode, ReadDatasetNode, WriteDatasetNode
from ai_flow.ai_graph.data_edge import DataEdge
from ai_flow.endpoint.server.server_config import DBType
from ai_flow.plugin_interface.scheduler_interface import Scheduler, SchedulerFactory
from ai_flow.store.abstract_store import Filters, AbstractStore
from ai_flow.store.db.db_util import extract_db_engine_from_uri, parse_mongo_uri
from ai_flow.store.mongo_store import MongoStore
from ai_flow.store.sqlalchemy_store import SqlAlchemyStore
from ai_flow.util.json_utils import loads, Jsonable, dumps
from ai_flow.workflow.control_edge import ControlEdge

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
CORS(app=app)

store: AbstractStore = None
scheduler: Scheduler = None
airflow: str = None


def init(store_uri: str, scheduler_class: str, airflow_web_server_uri: str):
    global store
    if DBType.value_of(extract_db_engine_from_uri(store_uri)) == DBType.MONGODB:
        username, password, host, port, db = parse_mongo_uri(store_uri)
        store = MongoStore(host=host,
                           port=int(port),
                           username=username,
                           password=password,
                           db=db)
    else:
        store = SqlAlchemyStore(store_uri)
    global scheduler
    scheduler = SchedulerFactory.create_scheduler(scheduler_class,
                                                  {'notification_service_uri': None, 'airflow_deploy_path': None})
    global airflow
    airflow = airflow_web_server_uri


class Edge(Jsonable):
    def __init__(self, id: str = None, name: str = None, is_signal: int = 1, is_closed_loop_node: bool = True,
                 dag_data_type: str = None):
        self._id = id
        self._name = name
        self._is_signal = is_signal
        self._is_closed_loop_node = is_closed_loop_node
        self._dag_data_type = dag_data_type

    @property
    def id(self) -> str:
        return self._id

    def to_dict(self):
        return {'id': self._id, 'name': self._name, 'isSignal': self._is_signal,
                'isClosedLoopNode': self._is_closed_loop_node,
                'dagDataType': self._dag_data_type}


class Node(Jsonable):

    def __init__(self, id: str = None, layer: int = None, parent: List[Edge] = None, children: List[Edge] = None,
                 node_type: int = None, is_virtual: int = None, name: str = None, job_type_name=None,
                 is_real_node: bool = True, job_id: int = None, source_flag: bool = None, rsuuid: str = None,
                 data_name: str = None, source_type: str = None, material_id: str = None, material_ready: bool = False,
                 material_parent_project_id: int = None):
        self._id = id
        self._layer = layer
        self._parent = parent
        self._children = children
        self._node_type = node_type
        self._is_virtual = is_virtual
        self._name = name
        self._job_type_name = job_type_name
        self._is_real_node = is_real_node
        self._job_id = job_id
        self._source_flag = source_flag
        self._rsuuid = rsuuid
        self._data_name = data_name
        self._source_type = source_type
        self._material_id = material_id
        self._material_ready = material_ready
        self._material_parent_project_id = material_parent_project_id

    @property
    def id(self) -> str:
        return self._id

    @property
    def layer(self) -> int:
        return self._layer

    @layer.setter
    def layer(self, layer: int):
        self._layer = layer

    @property
    def parent(self) -> List[Edge]:
        return self._parent

    @parent.setter
    def parent(self, parent: List[Edge]):
        self._parent = parent

    @property
    def children(self) -> List[Edge]:
        return self._children

    @children.setter
    def children(self, children: List[Edge]):
        self._children = children

    @property
    def name(self) -> str:
        return self._name

    @property
    def data_name(self) -> str:
        return self._data_name

    def to_dict(self):
        return {'id': self._id, 'layer': self._layer,
                'parent': None if self._parent is None else [edge.to_dict() for edge in self._parent],
                'children': None if self._children is None else [edge.to_dict() for edge in self._children],
                'nodeType': self._node_type, 'isVirtual': self._is_virtual, 'name': self._name,
                'jobTypeName': self._job_type_name,
                'isRealNode': self._is_real_node, 'jobId': self._job_id, 'sourceFlag': self._source_flag,
                'rsuuid': self._rsuuid, 'dataName': self._data_name,
                'sourceType': self._source_type, 'materialId': self._material_id, 'materialReady': self._material_ready,
                'materialParentProjectId': self._material_parent_project_id}


def node_layer(node: Node, parent_edges: Dict, nodes: Dict):
    if node.id not in parent_edges:
        return 1
    else:
        max_layer = 1
        for parent_edge in parent_edges[node.id]:
            layer = 1 + node_layer(nodes[parent_edge.id], parent_edges, nodes)
            if layer > max_layer:
                max_layer = layer
        return max_layer


def generate_graph(workflow_meta: WorkflowMeta):
    workflow_graph: AIGraph = extract_graph(workflow_meta)
    workflow_nodes, id_nodes, name_nodes = build_nodes(workflow_graph)
    parent_edges, children_edges = build_edges(workflow_graph, workflow_nodes, id_nodes, name_nodes)
    return build_graph(name_nodes, parent_edges, children_edges)


def extract_graph(workflow_meta: WorkflowMeta):
    graph_meta: Dict[str, str] = json.loads(workflow_meta.graph)
    if '_context_extractor' in graph_meta:
        graph_meta.pop('_context_extractor', None)
    return loads(dumps(graph_meta))


def build_nodes(workflow_graph: AIGraph):
    workflow_nodes: Dict[str, AINode] = {}
    id_nodes: Dict[str, Node] = {}
    name_nodes: Dict[str, Node] = {}
    for graph_node in workflow_graph.nodes.values():
        workflow_nodes.update({graph_node.node_id: graph_node})
        if isinstance(graph_node, ReadDatasetNode) or isinstance(graph_node, WriteDatasetNode):
            data_node = Node(id=graph_node.dataset().name, source_flag=True,
                             data_name=graph_node.dataset().name)
            id_nodes.update({graph_node.node_id: data_node})
            name_nodes.update({graph_node.dataset().name: data_node})
        else:
            job_node = Node(id=graph_node.config.job_name, node_type=0, name=graph_node.config.job_name,
                            job_type_name=graph_node.config.job_type, source_flag=False)
            id_nodes.update({graph_node.node_id: job_node})
            name_nodes.update({graph_node.config.job_name: job_node})
    return workflow_nodes, id_nodes, name_nodes


def build_edges(workflow_graph: AIGraph, workflow_nodes: Dict[str, AINode], id_nodes: Dict[str, Node],
                name_nodes: Dict[str, Node]):
    parent_edges: Dict[str, List[Edge]] = {}
    children_edges: Dict[str, List[Edge]] = {}
    for graph_edges in workflow_graph.edges.values():
        for graph_edge in graph_edges:
            if isinstance(graph_edge, DataEdge):
                source_workflow_node: AINode = workflow_nodes.get(graph_edge.source)
                destination_workflow_node: AINode = workflow_nodes.get(graph_edge.destination)
                dag_data_type = 'source' if isinstance(source_workflow_node, ReadDatasetNode) else 'sink'
                source_node: Node = id_nodes.get(graph_edge.source)
                source_name = source_node.data_name \
                    if isinstance(source_workflow_node, ReadDatasetNode) \
                    else source_node.name
                source_edge: Edge = Edge(id=source_name, name=source_name, dag_data_type=dag_data_type, )
                destination_node: Node = id_nodes.get(graph_edge.destination)
                destination_name = destination_node.data_name \
                    if isinstance(destination_workflow_node, WriteDatasetNode) \
                    else destination_node.name
                destination_edge: Edge = Edge(id=destination_name, name=destination_name,
                                              dag_data_type=dag_data_type)
                if source_name in children_edges:
                    children_edges[source_name].append(destination_edge)
                else:
                    children_edges[source_name] = [destination_edge]
                if destination_name in parent_edges:
                    parent_edges[destination_name].append(source_edge)
                else:
                    parent_edges[destination_name] = [source_edge]
            else:
                control_edge: ControlEdge = graph_edge
                for event in control_edge.scheduling_rule.event_condition.events:
                    if event.sender != '*':
                        sender_event_edge: Edge = Edge(id=name_nodes[event.sender].id,
                                                       name=name_nodes[event.sender].name,
                                                       dag_data_type='event')
                        receiver_event_edge: Edge = Edge(id=name_nodes[control_edge.destination].id,
                                                         name=name_nodes[control_edge.destination].name,
                                                         dag_data_type='event')
                        if name_nodes[event.sender].id in children_edges:
                            children_edges[name_nodes[event.sender].id].append(receiver_event_edge)
                        else:
                            children_edges[name_nodes[event.sender].id] = [receiver_event_edge]
                        if name_nodes[control_edge.destination].id in parent_edges:
                            parent_edges[name_nodes[control_edge.destination].id].append(sender_event_edge)
                        else:
                            parent_edges[name_nodes[control_edge.destination].id] = [sender_event_edge]
    return parent_edges, children_edges


def build_graph(name_nodes: Dict[str, Node], parent_edges: Dict[str, List[Edge]],
                children_edges: Dict[str, List[Edge]]):
    graph_nodes = []
    for graph_node in name_nodes.values():
        graph_node.layer = node_layer(graph_node, parent_edges, name_nodes)
        if graph_node.id in parent_edges:
            graph_node.parent = parent_edges[graph_node.id]
        if graph_node.id in children_edges:
            graph_node.children = children_edges[graph_node.id]
        graph_nodes.append(graph_node.to_dict())
    return json.dumps(graph_nodes)


def filter_class(filter_name: str):
    return getattr(sys.modules[store.__module__], filter_name)


def build_filters(req: LocalProxy):
    filters = Filters()
    for key, value in req.args.items():
        if key not in ('pageNo', 'pageSize') and value:
            filters.add_filter((filter_class('FilterEqual')(key), value))
    return filters


@app.route('/api/project')
def project_metadata():
    project_list = store.list_projects(page_size=int(request.args.get('pageSize')),
                                       offset=(int(request.args.get('pageNo')) - 1) * int(request.args.get('pageSize')),
                                       filters=build_filters(request))
    return dumps({'data': project_list if project_list else []})


@app.route('/api/workflow')
def workflow_metadata():
    workflow_list = store.list_workflows(page_size=int(request.args.get('pageSize')),
                                         offset=(int(request.args.get('pageNo')) - 1) * int(
                                             request.args.get('pageSize')),
                                         filters=build_filters(request))
    return dumps({'data': workflow_list if workflow_list else []})


@app.route('/api/workflow/data-view')
def data_view():
    project_id = request.args.get('project_id')
    workflow_name = request.args.get('workflow_name')
    project_meta = store.get_project_by_id(project_id)
    if project_meta is None:
        raise Exception('The project({}) for the workflow({}) is not found.'.format(project_id, workflow_name))
    workflow_meta = store.get_workflow_by_name(project_name=project_meta.name, workflow_name=workflow_name)
    if workflow_meta is None:
        raise Exception('The workflow({}) of the project({}) is not found.'.format(workflow_name, project_id))
    else:
        return generate_graph(workflow_meta)


@app.route('/api/workflow/task-view')
def task_view():
    project_id = request.args.get('project_id')
    workflow_name = request.args.get('workflow_name')
    project_meta = store.get_project_by_id(project_id)
    if project_meta is None:
        raise Exception('The project({}) for the workflow({}) is not found.'.format(project_id, workflow_name))
    workflow_meta = store.get_workflow_by_name(project_name=project_meta.name, workflow_name=workflow_name)
    if workflow_meta is None:
        raise Exception('The workflow({}) of the project({}) is not found.'.format(workflow_name, project_id))
    else:
        return '{}/graph?dag_id={}'.format(airflow, '{}.{}'.format(project_meta.name, workflow_name))


@app.route('/api/workflow-execution')
def workflow_execution_metadata():
    project_name = request.args.get('project_name')
    workflow_name = request.args.get('workflow_name')
    workflow_execution_list = scheduler.list_workflow_executions(project_name,
                                                                 workflow_name) if project_name and workflow_name else None
    return dumps({'data': workflow_execution_list if workflow_execution_list else []})


@app.route('/api/job-execution')
def job_execution_metadata():
    workflow_execution_id = request.args.get('workflow_execution_id')
    job_execution_list = scheduler.list_job_executions(workflow_execution_id) if workflow_execution_id else None
    return dumps({'data': job_execution_list if job_execution_list else []})


@app.route('/api/dataset')
def dataset_metadata():
    dataset_list = store.list_datasets(page_size=int(request.args.get('pageSize')),
                                       offset=(int(request.args.get('pageNo')) - 1) * int(request.args.get('pageSize')),
                                       filters=build_filters(request))
    return dumps({'data': dataset_list if dataset_list else []})


@app.route('/api/model')
def model_metadata():
    model_list = store.list_registered_models(page_size=int(request.args.get('pageSize')),
                                              offset=(int(request.args.get('pageNo')) - 1) * int(
                                                  request.args.get('pageSize')),
                                              filters=build_filters(request))
    return json.dumps({'data': [{'model_name': model.model_name, 'model_desc': model.model_desc} for model in
                                model_list] if model_list else []})


@app.route('/api/model-version')
def model_version_metadata():
    model_version_list = store.list_model_versions(page_size=int(request.args.get('pageSize')),
                                                   offset=(int(request.args.get('pageNo')) - 1) * int(
                                                       request.args.get('pageSize')),
                                                   filters=build_filters(request))
    return json.dumps(
        {'data': [model_version.__dict__ for model_version in model_version_list] if model_version_list else []})


@app.route('/api/artifact')
def artifact_metadata():
    artifact_list = store.list_artifacts(page_size=int(request.args.get('pageSize')),
                                         offset=(int(request.args.get('pageNo')) - 1) * int(
                                             request.args.get('pageSize')),
                                         filters=build_filters(request))
    return dumps({'data': artifact_list if artifact_list else []})


def main(argv):
    port = ''
    store_uri = ''
    scheduler_class = ''
    airflow_web_server_uri = ''
    try:
        opts, args = getopt.getopt(argv, "hp:s:c:a:",
                                   ["port=", "store_uri=", "scheduler_class=", "airflow_web_server_uri="])
    except getopt.GetoptError:
        print('usage: web_server.py -p <port> -s <store_uri> -c <scheduler_class> -a <airflow_web_server_uri>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('usage: web_server.py -p <port> -s <store_uri> -c <scheduler_class> -a <airflow_web_server_uri>')
            sys.exit()
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-s", "--store_uri"):
            store_uri = arg
        elif opt in ("-c", "--scheduler_class"):
            scheduler_class = arg
        elif opt in ("-a", "--airflow_web_server_uri"):
            airflow_web_server_uri = arg
    if not port:
        port = 50053
    if not scheduler_class:
        scheduler_class = 'ai_flow_plugins.scheduler_plugins.airflow.airflow_scheduler.AirFlowScheduler'
    init(store_uri, scheduler_class, airflow_web_server_uri)
    app.run(host='127.0.0.1', port=port)


if __name__ == '__main__':
    main(sys.argv[1:])
