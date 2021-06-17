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
import time

from ai_flow.common.status import Status
from ai_flow.meta.dataset_meta import DataType
from ai_flow.meta.job_meta import State
from ai_flow.metadata_store.utils.MetaToProto import MetaToProto
from ai_flow.metadata_store.utils.ProtoToMeta import ProtoToMeta
from ai_flow.protobuf import metadata_service_pb2_grpc
from ai_flow.protobuf.message_pb2 import DataTypeProto, StateProto, ModelType
from ai_flow.endpoint.client.model_center_client import ModelCenterClient
from ai_flow.endpoint.server.util import _wrap_meta_response, transform_dataset_meta, \
    _warp_dataset_list_response, _wrap_delete_response, transform_model_relation_meta, \
    _warp_model_relation_list_response, _warp_model_version_relation_list_response, \
    transform_model_version_relation_meta, _warp_job_list_response, \
    transform_job_meta, _wrap_update_response, _warp_workflow_execution_list_response, \
    transform_workflow_execution_meta, _warp_project_list_response, transform_project_meta, catch_exception, \
    transform_model_meta, transform_model_version_meta, transform_artifact_meta, _warp_artifact_list_response
from ai_flow.store.sqlalchemy_store import SqlAlchemyStore
from ai_flow.store.mongo_store import MongoStore
from ai_flow.store.db.db_util import extract_db_engine_from_uri, parse_mongo_uri
from ai_flow.application_master.master_config import DBType


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
                                                   create_time=dataset.create_time,
                                                   update_time=dataset.update_time,
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
                                                 update_time=request.update_time.value if request.HasField(
                                                     'update_time') else None,
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
        model_detail = self.model_center_client.create_registered_model(model.name, ModelType.Name(model.model_type),
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
                                                              workflow_execution_id=model_version.workflow_execution_id)
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
                                                                             model_version.model_metric,
                                                                             model_version.model_flavor,
                                                                             model_version.version_desc,
                                                                             request.model_version.current_stage)
        model_version_relation = self.store.register_model_version_relation(version=model_version_detail.model_version,
                                                                            model_id=model_version.model_id,
                                                                            workflow_execution_id=
                                                                            model_version.workflow_execution_id)
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

    '''job api'''

    @catch_exception
    def getJobById(self, request, context):
        job_meta = self.store.get_job_by_id(request.id)
        return _wrap_meta_response(MetaToProto.job_meta_to_proto(job_meta))

    @catch_exception
    def getJobByName(self, request, context):
        job_meta = self.store.get_job_by_name(request.name)
        return _wrap_meta_response(MetaToProto.job_meta_to_proto(job_meta))

    @catch_exception
    def updateJob(self, request, context):
        properties = None if request.properties == {} else request.properties
        job_state = None if request.job_state == 0 else State(StateProto.Name(request.job_state))
        job = self.store.update_job(job_name=request.name, job_state=job_state,
                                    properties=properties,
                                    job_id=request.job_id.value if request.HasField('job_id') else None,
                                    workflow_execution_id=request.workflow_execution_id.value
                                    if request.HasField('workflow_execution_id') else None,
                                    end_time=request.end_time.value if request.HasField('end_time') else None,
                                    log_uri=request.log_uri.value if request.HasField('log_uri') else None,
                                    signature=request.signature.value if request.HasField('signature') else None)
        return _wrap_meta_response(MetaToProto.job_meta_to_proto(job))

    @catch_exception
    def listJob(self, request, context):
        job_meta_list = self.store.list_job(request.page_size, request.offset)
        return _warp_job_list_response(job_meta_list)

    @catch_exception
    def registerJob(self, request, context):
        job = transform_job_meta(request.job)
        response = self.store.register_job(name=job.name, workflow_execution_id=job.workflow_execution_id,
                                           job_state=job.job_state, properties=job.properties, job_id=job.job_id,
                                           start_time=job.start_time, end_time=job.end_time, log_uri=job.log_uri,
                                           signature=job.signature)
        return _wrap_meta_response(MetaToProto.job_meta_to_proto(response))

    @catch_exception
    def updateJobState(self, request, context):
        _state = ProtoToMeta.proto_to_state(request.state)
        uuid = self.store.update_job_state(_state, request.name)
        return _wrap_update_response(uuid)

    @catch_exception
    def updateJobEndTime(self, request, context):
        uuid = self.store.update_job_end_time(request.end_time, request.name)
        return _wrap_update_response(uuid)

    @catch_exception
    def deleteJobById(self, request, context):
        status = self.store.delete_job_by_id(request.id)
        return _wrap_delete_response(status)

    @catch_exception
    def deleteJobByName(self, request, context):
        status = self.store.delete_job_by_name(request.name)
        return _wrap_delete_response(status)

    '''workflow execution api'''

    @catch_exception
    def getWorkFlowExecutionById(self, request, context):
        execution_meta = self.store.get_workflow_execution_by_id(request.id)
        return _wrap_meta_response(MetaToProto.workflow_execution_meta_to_proto(execution_meta))

    @catch_exception
    def getWorkFlowExecutionByName(self, request, context):
        execution_meta = self.store.get_workflow_execution_by_name(request.name)
        return _wrap_meta_response(MetaToProto.workflow_execution_meta_to_proto(execution_meta))

    @catch_exception
    def updateWorkflowExecution(self, request, context):
        properties = None if request.properties == {} else request.properties
        execution_state = None if request.execution_state == 0 else State(StateProto.Name(request.execution_state))
        workflow_execution = self.store.update_workflow_execution(execution_name=request.name,
                                                                  execution_state=execution_state,
                                                                  project_id=request.project_id.value if request.HasField(
                                                                      'project_id') else None,
                                                                  properties=properties,
                                                                  end_time=request.end_time.value if request.HasField(
                                                                      'end_time') else None,
                                                                  log_uri=request.log_uri_value if request.HasField(
                                                                      'log_uri') else None,
                                                                  workflow_json=request.workjson.value if request.HasField(
                                                                      'workflow_json') else None,
                                                                  signature=request.signature.value if request.HasField(
                                                                      'signature') else None)
        return _wrap_meta_response(MetaToProto.workflow_execution_meta_to_proto(workflow_execution))

    @catch_exception
    def listWorkFlowExecution(self, request, context):
        workflow_execution_meta_list = self.store.list_workflow_execution(request.page_size, request.offset)
        return _warp_workflow_execution_list_response(workflow_execution_meta_list)

    @catch_exception
    def registerWorkFlowExecution(self, request, context):
        workflow_execution = transform_workflow_execution_meta(request.workflow_execution)
        response = self.store.register_workflow_execution(name=workflow_execution.name,
                                                          project_id=workflow_execution.project_id,
                                                          execution_state=workflow_execution.execution_state,
                                                          properties=workflow_execution.properties,
                                                          start_time=workflow_execution.start_time,
                                                          end_time=workflow_execution.end_time,
                                                          log_uri=workflow_execution.log_uri,
                                                          workflow_json=workflow_execution.workflow_json,
                                                          signature=workflow_execution.signature
                                                          )
        return _wrap_meta_response(MetaToProto.workflow_execution_meta_to_proto(response))

    @catch_exception
    def updateWorkflowExecutionEndTime(self, request, context):
        uuid = self.store.update_workflow_execution_end_time(request.end_time, request.name)
        return _wrap_update_response(uuid)

    @catch_exception
    def updateWorkflowExecutionState(self, request, context):
        _state = ProtoToMeta.proto_to_state(request.state)
        uuid = self.store.update_workflow_execution_state(_state, request.name)
        return _wrap_update_response(uuid)

    @catch_exception
    def deleteWorkflowExecutionById(self, request, context):
        status = self.store.delete_workflow_execution_by_id(request.id)
        return _wrap_delete_response(status)

    @catch_exception
    def deleteWorkflowExecutionByName(self, request, context):
        status = self.store.delete_workflow_execution_by_name(request.name)
        return _wrap_delete_response(status)

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
        create_time = int(time.time() * 1000)
        response = self.store.register_artifact(name=artifact.name, artifact_type=artifact.artifact_type,
                                                description=artifact.description,
                                                uri=artifact.uri,
                                                create_time=create_time,
                                                properties=artifact.properties)
        return _wrap_meta_response(MetaToProto.artifact_meta_to_proto(response))

    @catch_exception
    def updateArtifact(self, request, context):
        properties = None if request.properties == {} else request.properties
        updata_time = int(time.time() * 1000)
        artifact = self.store.update_artifact(name=request.name,
                                              artifact_type=request.artifact_type.value if request.HasField(
                                                  'artifact_type') else None,
                                              properties=properties,
                                              description=request.description.value if request.HasField(
                                                  'description') else None,
                                              uri=request.uri.value if request.HasField('uri') else None,
                                              update_time=updata_time
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
