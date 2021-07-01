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

from ai_flow.common.status import Status
from ai_flow.meta.dataset_meta import DataType
from ai_flow.metadata_store.utils.MetaToProto import MetaToProto
from ai_flow.metadata_store.utils.ProtoToMeta import ProtoToMeta
from ai_flow.protobuf import metadata_service_pb2_grpc
from ai_flow.protobuf.message_pb2 import DataTypeProto
from ai_flow.endpoint.client.model_center_client import ModelCenterClient
from ai_flow.endpoint.server.util import _wrap_meta_response, transform_dataset_meta, \
    _warp_dataset_list_response, _wrap_delete_response, transform_model_relation_meta, \
    _warp_model_relation_list_response, _warp_model_version_relation_list_response, \
    transform_model_version_relation_meta, _warp_project_list_response, transform_project_meta, catch_exception, \
    transform_model_meta, transform_model_version_meta, transform_artifact_meta, _warp_artifact_list_response, \
    transform_workflow_meta, _wrap_workflow_list_response
from ai_flow.store.sqlalchemy_store import SqlAlchemyStore
from ai_flow.store.mongo_store import MongoStore
from ai_flow.store.db.db_util import extract_db_engine_from_uri, parse_mongo_uri
from ai_flow.endpoint.server.server_config import DBType


class MetadataService(metadata_service_pb2_grpc.MetadataServiceServicer):
    def __init__(self, db_uri, server_uri):
        db_engine = extract_db_engine_from_uri(db_uri)
        if DBType.value_of(db_engine) == DBType.MONGODB:
            username, password, host, port, db = parse_mongo_uri(db_uri)
            self.store = MongoStore(host=host,
                                    port=int(port),
                                    username=username,
                                    password=password,
                                    db=db)
        else:
            self.store = SqlAlchemyStore(db_uri)
        self.model_center_client = ModelCenterClient(server_uri)

    '''dataset api'''

    @catch_exception
    def getDatasetById(self, request, context):
        dataset = self.store.get_dataset_by_id(request.id)
        return _wrap_meta_response(MetaToProto.dataset_meta_to_proto(dataset))

    @catch_exception
    def getDatasetByName(self, request, context):
        dataset = self.store.get_dataset_by_name(request.name)
        return _wrap_meta_response(MetaToProto.dataset_meta_to_proto(dataset))

    @catch_exception
    def registerDataset(self, request, context):
        dataset = transform_dataset_meta(request.dataset)
        dataset_meta = self.store.register_dataset(name=dataset.name,
                                                   data_format=dataset.data_format,
                                                   description=dataset.description,
                                                   uri=dataset.uri,
                                                   properties=dataset.properties,
                                                   name_list=dataset.schema.name_list,
                                                   type_list=dataset.schema.type_list)
        return _wrap_meta_response(MetaToProto.dataset_meta_to_proto(dataset_meta))

    @catch_exception
    def registerDatasetWithCatalog(self, request, context):
        dataset = transform_dataset_meta(request.dataset)
        dataset_meta = self.store.register_dataset_with_catalog(name=dataset.name,
                                                                catalog_name=dataset.catalog_name,
                                                                catalog_type=dataset.catalog_type,
                                                                catalog_database=dataset.catalog_database,
                                                                catalog_connection_uri=dataset.catalog_connection_uri,
                                                                catalog_table=dataset.catalog_table)
        return _wrap_meta_response(MetaToProto.dataset_meta_to_proto(dataset_meta))

    @catch_exception
    def registerDatasets(self, request, context):
        _datasets = ProtoToMeta.proto_to_dataset_meta_list(request.datasets)
        response = self.store.register_datasets(_datasets)
        return _warp_dataset_list_response(response)

    @catch_exception
    def updateDataset(self, request, context):
        properties = None if request.properties == {} else request.properties
        name_list = request.name_list
        type_list = request.type_list
        if not name_list:
            name_list = None
        if not type_list:
            data_type_list = None
        else:
            data_type_list = []
            for data_type in type_list:
                data_type_list.append(DataType(DataTypeProto.Name(data_type)))
        dataset_meta = self.store.update_dataset(dataset_name=request.name,
                                                 data_format=request.data_format.value if request.HasField(
                                                     'data_format') else None,
                                                 description=request.description.value if request.HasField(
                                                     'description') else None,
                                                 uri=request.uri.value if request.HasField('uri') else None,
                                                 properties=properties,
                                                 name_list=name_list,
                                                 type_list=data_type_list,
                                                 catalog_name=request.catalog_name.value if request.HasField(
                                                     'catalog_name') else None,
                                                 catalog_type=request.catalog_type.value if request.HasField(
                                                     'catalog_type') else None,
                                                 catalog_database=request.catalog_database.value if request.HasField(
                                                     'catalog_database') else None,
                                                 catalog_connection_uri=request.catalog_connection_uri.value \
                                                     if request.HasField('catalog_connection_uri') else None,
                                                 catalog_table=request.catalog_table.value if request.HasField(
                                                     'catalog_table') else None)
        return _wrap_meta_response(MetaToProto.dataset_meta_to_proto(dataset_meta))

    @catch_exception
    def listDatasets(self, request, context):
        dataset_meta_list = self.store.list_datasets(request.page_size, request.offset)
        return _warp_dataset_list_response(dataset_meta_list)

    @catch_exception
    def deleteDatasetById(self, request, context):
        status = self.store.delete_dataset_by_id(request.id)
        return _wrap_delete_response(status)

    @catch_exception
    def deleteDatasetByName(self, request, context):
        status = self.store.delete_dataset_by_name(request.name)
        return _wrap_delete_response(status)

    '''model relation api'''

    @catch_exception
    def getModelRelationById(self, request, context):
        model_meta = self.store.get_model_relation_by_id(request.id)
        return _wrap_meta_response(MetaToProto.model_relation_meta_to_proto(model_meta))

    @catch_exception
    def getModelRelationByName(self, request, context):
        model_meta = self.store.get_model_relation_by_name(request.name)
        return _wrap_meta_response(MetaToProto.model_relation_meta_to_proto(model_meta))

    @catch_exception
    def registerModelRelation(self, request, context):
        model = transform_model_relation_meta(request.model_relation)
        response = self.store.register_model_relation(name=model.name, project_id=model.project_id)
        return _wrap_meta_response(MetaToProto.model_relation_meta_to_proto(response))

    @catch_exception
    def listModelRelation(self, request, context):
        model_list = self.store.list_model_relation(request.page_size, request.offset)
        return _warp_model_relation_list_response(model_list)

    @catch_exception
    def deleteModelRelationById(self, request, context):
        status = self.store.delete_model_relation_by_id(request.id)
        return _wrap_delete_response(status)

    @catch_exception
    def deleteModelRelationByName(self, request, context):
        status = self.store.delete_model_relation_by_name(request.name)
        return _wrap_delete_response(status)

    '''model api'''

    @catch_exception
    def getModelById(self, request, context):
        model_relation = self.store.get_model_relation_by_id(request.id)
        if model_relation is None:
            model_detail = None
        else:
            model_detail = self.model_center_client.get_registered_model_detail(model_relation.name)
        return _wrap_meta_response(MetaToProto.model_meta_to_proto(model_relation, model_detail))

    @catch_exception
    def getModelByName(self, request, context):
        model_relation = self.store.get_model_relation_by_name(request.name)
        model_detail = self.model_center_client.get_registered_model_detail(request.name)
        return _wrap_meta_response(MetaToProto.model_meta_to_proto(model_relation, model_detail))

    @catch_exception
    def registerModel(self, request, context):
        model = transform_model_meta(request.model)
        model_detail = self.model_center_client.create_registered_model(model.name,
                                                                        model.model_desc)
        model_relation = self.store.register_model_relation(name=model.name, project_id=model.project_id)
        return _wrap_meta_response(MetaToProto.model_meta_to_proto(model_relation, model_detail))

    @catch_exception
    def deleteModelById(self, request, context):
        model_relation = self.store.get_model_relation_by_id(request.id)
        if model_relation is None:
            return _wrap_delete_response(Status.ERROR)
        else:
            model_relation_status = self.store.delete_model_relation_by_id(request.id)
            self.model_center_client.delete_registered_model(model_relation.name)
            return _wrap_delete_response(model_relation_status)

    @catch_exception
    def deleteModelByName(self, request, context):
        model_relation_status = self.store.delete_model_relation_by_name(request.name)
        self.model_center_client.delete_registered_model(request.name)
        return _wrap_delete_response(model_relation_status)

    '''model version relation api'''

    @catch_exception
    def getModelVersionRelationByVersion(self, request, context):
        model_version_meta = self.store.get_model_version_relation_by_version(request.name, request.model_id)
        return _wrap_meta_response(MetaToProto.model_version_relation_meta_to_proto(model_version_meta))

    @catch_exception
    def listModelVersionRelation(self, request, context):
        model_version_meta_list = self.store.list_model_version_relation(request.model_id, request.page_size,
                                                                         request.offset)
        return _warp_model_version_relation_list_response(model_version_meta_list)

    @catch_exception
    def registerModelVersionRelation(self, request, context):
        model_version = transform_model_version_relation_meta(request.model_version_relation)
        response = self.store.register_model_version_relation(version=model_version.version,
                                                              model_id=model_version.model_id,
                                                              project_snapshot_id=model_version.project_snapshot_id)
        return _wrap_meta_response(MetaToProto.model_version_relation_meta_to_proto(response))

    @catch_exception
    def deleteModelVersionRelationByVersion(self, request, context):
        status = self.store.delete_model_version_relation_by_version(request.name, request.model_id)
        return _wrap_delete_response(status)

    '''model version api'''

    @catch_exception
    def getModelVersionByVersion(self, request, context):
        model_version_relation = self.store.get_model_version_relation_by_version(request.name, request.model_id)
        if model_version_relation is None:
            model_version_detail = None
        else:
            model_relation = self.store.get_model_relation_by_id(model_version_relation.model_id)
            model_version_detail = self.model_center_client.get_model_version_detail(model_relation.name, request.name)
        return _wrap_meta_response(
            MetaToProto.model_version_meta_to_proto(model_version_relation, model_version_detail))

    @catch_exception
    def registerModelVersion(self, request, context):
        model_version = transform_model_version_meta(request.model_version)
        model_relation = self.store.get_model_relation_by_id(model_version.model_id)
        model_version_detail = self.model_center_client.create_model_version(model_relation.name,
                                                                             model_version.model_path,
                                                                             model_version.model_type,
                                                                             model_version.version_desc,
                                                                             request.model_version.current_stage)
        model_version_relation = self.store.register_model_version_relation(version=model_version_detail.model_version,
                                                                            model_id=model_version.model_id,
                                                                            project_snapshot_id=
                                                                            model_version.project_snapshot_id)
        return _wrap_meta_response(
            MetaToProto.model_version_meta_to_proto(model_version_relation, model_version_detail))

    @catch_exception
    def deleteModelVersionByVersion(self, request, context):
        model_version_relation = self.store.get_model_version_relation_by_version(request.name, request.model_id)
        if model_version_relation is None:
            return _wrap_delete_response(Status.ERROR)
        else:
            model_version__status = self.store.delete_model_version_relation_by_version(request.name, request.model_id)
            model_relation = self.store.get_model_relation_by_id(model_version_relation.model_id)
            if model_relation is not None:
                self.model_center_client.delete_model_version(model_relation.name, request.name)
            return _wrap_delete_response(model_version__status)

    @catch_exception
    def getDeployedModelVersion(self, request, context):
        model_version_detail = self.store.get_deployed_model_version(request.name)
        if model_version_detail is None:
            model_version_relation = None
        else:
            model_relation = self.store.get_model_relation_by_name(request.name)
            model_version_relation = self.store.get_model_version_relation_by_version(
                model_version_detail.model_version,
                model_relation.uuid)
        return _wrap_meta_response(
            MetaToProto.model_version_store_to_proto(model_version_relation, model_version_detail))

    @catch_exception
    def getLatestValidatedModelVersion(self, request, context):
        model_version_detail = self.store.get_latest_validated_model_version(request.name)
        if model_version_detail is None:
            model_version_relation = None
        else:
            model_relation = self.store.get_model_relation_by_name(request.name)
            model_version_relation = self.store.get_model_version_relation_by_version(
                model_version_detail.model_version,
                model_relation.uuid)
        return _wrap_meta_response(
            MetaToProto.model_version_store_to_proto(model_version_relation, model_version_detail))

    @catch_exception
    def getLatestGeneratedModelVersion(self, request, context):
        model_version_detail = self.store.get_latest_generated_model_version(request.name)
        if model_version_detail is None:
            model_version_relation = None
        else:
            model_relation = self.store.get_model_relation_by_name(request.name)
            model_version_relation = self.store.get_model_version_relation_by_version(
                model_version_detail.model_version,
                model_relation.uuid)
        return _wrap_meta_response(
            MetaToProto.model_version_store_to_proto(model_version_relation, model_version_detail))

    '''project api'''

    @catch_exception
    def getProjectById(self, request, context):
        project_meta = self.store.get_project_by_id(request.id)
        return _wrap_meta_response(MetaToProto.project_meta_to_proto(project_meta))

    @catch_exception
    def getProjectByName(self, request, context):
        project_meta = self.store.get_project_by_name(request.name)
        return _wrap_meta_response(MetaToProto.project_meta_to_proto(project_meta))

    @catch_exception
    def listProject(self, request, context):
        project_meta_list = self.store.list_project(request.page_size, request.offset)
        return _warp_project_list_response(project_meta_list)

    @catch_exception
    def registerProject(self, request, context):
        project = transform_project_meta(request.project)
        response = self.store.register_project(name=project.name, uri=project.uri, properties=project.properties)
        return _wrap_meta_response(MetaToProto.project_meta_to_proto(response))

    @catch_exception
    def updateProject(self, request, context):
        properties = None if request.properties == {} else request.properties
        project = self.store.update_project(project_name=request.name,
                                            uri=request.uri.value if request.HasField('uri') else None,
                                            properties=properties)
        return _wrap_meta_response(MetaToProto.project_meta_to_proto(project))

    @catch_exception
    def deleteProjectById(self, request, context):
        status = self.store.delete_project_by_id(request.id)
        return _wrap_delete_response(status)

    @catch_exception
    def deleteProjectByName(self, request, context):
        status = self.store.delete_project_by_name(request.name)
        return _wrap_delete_response(status)

    '''artifact api'''

    @catch_exception
    def getArtifactById(self, request, context):
        artifact_meta = self.store.get_artifact_by_id(request.id)
        return _wrap_meta_response(MetaToProto.artifact_meta_to_proto(artifact_meta))

    @catch_exception
    def getArtifactByName(self, request, context):
        artifact_meta = self.store.get_artifact_by_name(request.name)
        return _wrap_meta_response(MetaToProto.artifact_meta_to_proto(artifact_meta))

    @catch_exception
    def registerArtifact(self, request, context):
        artifact = transform_artifact_meta(request.artifact)
        response = self.store.register_artifact(name=artifact.name, artifact_type=artifact.artifact_type,
                                                description=artifact.description, uri=artifact.uri,
                                                properties=artifact.properties)
        return _wrap_meta_response(MetaToProto.artifact_meta_to_proto(response))

    @catch_exception
    def updateArtifact(self, request, context):
        properties = None if request.properties == {} else request.properties
        artifact = self.store.update_artifact(name=request.name,
                                              artifact_type=request.artifact_type.value if request.HasField(
                                                  'artifact_type') else None,
                                              properties=properties,
                                              description=request.description.value if request.HasField(
                                                  'description') else None,
                                              uri=request.uri.value if request.HasField('uri') else None,
                                              )
        return _wrap_meta_response(MetaToProto.artifact_meta_to_proto(artifact))

    @catch_exception
    def listArtifact(self, request, context):
        artifact_meta_list = self.store.list_artifact(request.page_size, request.offset)
        return _warp_artifact_list_response(artifact_meta_list)

    @catch_exception
    def deleteArtifactById(self, request, context):
        status = self.store.delete_artifact_by_id(request.id)
        return _wrap_delete_response(status)

    @catch_exception
    def deleteArtifactByName(self, request, context):
        status = self.store.delete_artifact_by_name(request.name)
        return _wrap_delete_response(status)

    @catch_exception
    def registerWorkflow(self, request, context):
        workflow = transform_workflow_meta(request.workflow)
        response = self.store.register_workflow(name=workflow.name,
                                                project_id=workflow.project_id,
                                                properties=workflow.properties)
        return _wrap_meta_response(MetaToProto.workflow_meta_to_proto(response))

    @catch_exception
    def updateWorkflow(self, request, context):
        properties = None if request.properties == {} else request.properties
        workflow = self.store.update_workflow(workflow_name=request.workflow_name,
                                              project_name=request.project_name,
                                              properties=properties)
        return _wrap_meta_response(MetaToProto.workflow_meta_to_proto(workflow))

    def getWorkflowById(self, request, context):
        workflow = self.store.get_workflow_by_id(workflow_id=request.id)
        return _wrap_meta_response(MetaToProto.workflow_meta_to_proto(workflow))

    def getWorkflowByName(self, request, context):
        workflow = self.store.get_workflow_by_name(project_name=request.project_name,
                                                   workflow_name=request.workflow_name)
        return _wrap_meta_response(MetaToProto.workflow_meta_to_proto(workflow))

    def deleteWorkflowById(self, request, context):
        status = self.store.delete_workflow_by_id(workflow_id=request.id)
        return _wrap_delete_response(status)

    def deleteWorkflowByName(self, request, context):
        status = self.store.delete_workflow_by_name(project_name=request.project_name,
                                                    workflow_name=request.workflow_name)
        return _wrap_delete_response(status)

    def listWorkflows(self, request, context):
        workflow_meta_list = self.store.list_workflows(project_name=request.project_name,
                                                       page_size=request.page_size,
                                                       offset=request.offset)
        return _wrap_workflow_list_response(workflow_meta_list)

