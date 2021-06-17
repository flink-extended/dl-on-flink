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
from typing import Optional, Text, List

import grpc

from ai_flow.common.status import Status
from ai_flow.meta.artifact_meta import ArtifactMeta
from ai_flow.meta.dataset_meta import DatasetMeta, Properties, DataType
from ai_flow.meta.job_meta import JobMeta, State
from ai_flow.meta.model_meta import ModelMeta, ModelVersionMeta
from ai_flow.meta.model_relation_meta import ModelRelationMeta, ModelVersionRelationMeta
from ai_flow.meta.project_meta import ProjectMeta
from ai_flow.meta.workflow_execution_meta import WorkflowExecutionMeta
from ai_flow.metadata_store.utils.MetaToProto import MetaToProto
from ai_flow.protobuf import metadata_service_pb2_grpc, metadata_service_pb2
from ai_flow.protobuf.message_pb2 import DatasetProto, SchemaProto, ModelRelationProto, ModelProto, \
    ModelVersionRelationProto, ModelVersionProto, WorkflowExecutionProto, StateProto, JobProto, ProjectProto, \
    ArtifactProto, ModelVersionStage, ModelType
from ai_flow.protobuf.metadata_service_pb2 import ModelNameRequest
from ai_flow.endpoint.server import stringValue, int64Value
from ai_flow.endpoint.client.base_client import BaseClient
from ai_flow.endpoint.server.util import _unwrap_dataset_response, \
    transform_dataset_type_list_to_proto, _unwrap_dataset_list_response, _unwrap_delete_response, \
    _unwrap_model_relation_response, _unwrap_model_relation_list_response, _unwrap_model_response, \
    _unwrap_model_version_relation_response, _unwrap_model_version_relation_list_response, \
    _unwrap_model_version_response, _unwrap_workflow_execution_response, \
    _unwrap_workflow_execution_list_response, _unwrap_update_response, _unwrap_job_response, \
    _unwrap_job_list_response, _unwrap_project_response, _unwrap_project_list_response, \
    _unwrap_artifact_response, _unwrap_artifact_list_response


class MetadataClient(BaseClient):
    def __init__(self, server_uri):
        super(MetadataClient, self).__init__(server_uri)
        channel = grpc.insecure_channel(server_uri)
        self.metadata_store_stub = metadata_service_pb2_grpc.MetadataServiceStub(channel)

    '''dataset api'''

    def get_dataset_by_id(self, dataset_id) -> Optional[DatasetMeta]:
        """
        get a specific dataset in metadata store by dataset id.

        :param dataset_id: the dataset id
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object if the dataset exists,
                 Otherwise, returns None if the dataset does not exist.
        """
        request = metadata_service_pb2.IdRequest(id=dataset_id)
        response = self.metadata_store_stub.getDatasetById(request)
        return _unwrap_dataset_response(response)

    def get_dataset_by_name(self, dataset_name) -> Optional[DatasetMeta]:
        """
        get a specific dataset in metadata store by dataset name.

        :param dataset_name: the dataset name
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object if the dataset exists,,
                 Otherwise, returns None if the dataset does not exist.
        """
        request = metadata_service_pb2.NameRequest(name=dataset_name)
        response = self.metadata_store_stub.getDatasetByName(request)
        return _unwrap_dataset_response(response)

    def register_dataset(self, name: Text, data_format: Text = None, description: Text = None,
                         uri: Text = None, create_time: int = None, update_time: int = None,
                         properties: Properties = None, name_list: List[Text] = None,
                         type_list: List[DataType] = None) -> DatasetMeta:
        """
        register an dataset in metadata store.

        :param name: the name of the dataset
        :param data_format: the data format of the dataset
        :param description: the description of the dataset
        :param uri: the uri of the dataset
        :param create_time: the time when the dataset is created
        :param update_time: the time when the dataset is updated
        :param properties: the properties of the dataset
        :param name_list: the name list of dataset's schema
        :param type_list: the type list corresponded to the name list of dataset's schema
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object.
        """
        request = metadata_service_pb2.RegisterDatasetRequest(
            dataset=DatasetProto(name=name,  data_format=stringValue(data_format),
                                 description=stringValue(description), uri=stringValue(uri),
                                 create_time=int64Value(create_time),
                                 update_time=int64Value(update_time), properties=properties,
                                 schema=SchemaProto(name_list=name_list, type_list=transform_dataset_type_list_to_proto(
                                     type_list)),
                                 catalog_name=stringValue(None), catalog_type=stringValue(None),
                                 catalog_database=stringValue(None), catalog_connection_uri=stringValue(None),
                                 catalog_table=stringValue(None)))
        response = self.metadata_store_stub.registerDataset(request)
        return _unwrap_dataset_response(response)

    def register_dataset_with_catalog(self, name: Text,
                                      catalog_name: Text, catalog_type: Text,
                                      catalog_connection_uri: Text,
                                      catalog_table: Text, catalog_database: Text = None) -> DatasetMeta:
        """
        register dataset with catalog in metadata store.

        :param name: the name of the dataset
        :param catalog_name: the name of the dataset catalog
        :param catalog_type: the type of the dataset catalog
        :param catalog_connection_uri: the connection uri of the dataset catalog
        :param catalog_table: the table of the dataset catalog
        :param catalog_database: the database of the dataset catalog
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object.
        """
        request = metadata_service_pb2.RegisterDatasetRequest(
            dataset=DatasetProto(name=name,
                                 data_format=stringValue(None), description=stringValue(None),
                                 uri=stringValue(None),
                                 create_time=int64Value(None), update_time=int64Value(None),
                                 properties=None,
                                 schema=SchemaProto(name_list=None, type_list=transform_dataset_type_list_to_proto(
                                     None)),
                                 catalog_name=stringValue(catalog_name), catalog_type=stringValue(catalog_type),
                                 catalog_database=stringValue(catalog_database),
                                 catalog_connection_uri=stringValue(catalog_connection_uri),
                                 catalog_table=stringValue(catalog_table)))
        response = self.metadata_store_stub.registerDatasetWithCatalog(request)
        return _unwrap_dataset_response(response)

    def register_datasets(self, datasets: List[DatasetMeta]) -> List[DatasetMeta]:
        """
        register multiple datasets in metadata store.

        :param datasets: A list of datasets
        :return: List of :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` objects.
        """
        request = metadata_service_pb2.RegisterDatasetsRequest(
            datasets=MetaToProto.dataset_meta_list_to_proto(datasets))
        response = self.metadata_store_stub.registerDatasets(request)
        return _unwrap_dataset_list_response(response)

    def update_dataset(self, dataset_name: Text, data_format: Text = None,
                       description: Text = None, uri: Text = None, update_time: int = None,
                       properties: Properties = None, name_list: List[Text] = None,
                       type_list: List[DataType] = None, catalog_name: Text = None,
                       catalog_type: Text = None, catalog_database: Text = None,
                       catalog_connection_uri: Text = None,
                       catalog_table: Text = None) -> Optional[DatasetMeta]:
        """
        update dataset in metadata store.

        :param dataset_name: the name of the dataset
        :param data_format: the data format of the dataset
        :param description: the description of the dataset
        :param uri: the uri of the dataset
        :param update_time: the time when the dataset is updated
        :param properties: the properties of the dataset
        :param name_list: the name list of dataset's schema
        :param type_list: the type list corresponded to the name list of dataset's schema
        :param catalog_name: the name of the dataset catalog
        :param catalog_type: the type of the dataset catalog
        :param catalog_database: :param catalog_database: the database of the dataset catalog
        :param catalog_connection_uri: the connection uri of the dataset catalog
        :param catalog_table: the table of the dataset catalog
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object if update successfully.
        """
        request = metadata_service_pb2.UpdateDatasetRequest(name=dataset_name,
                                                            data_format=stringValue(data_format),
                                                            description=stringValue(description),
                                                            uri=stringValue(uri),
                                                            update_time=int64Value(update_time),
                                                            properties=properties,
                                                            name_list=name_list,
                                                            type_list=transform_dataset_type_list_to_proto(
                                                                type_list),
                                                            catalog_name=stringValue(catalog_name),
                                                            catalog_type=stringValue(catalog_type),
                                                            catalog_database=stringValue(catalog_database),
                                                            catalog_connection_uri=stringValue(catalog_connection_uri),
                                                            catalog_table=stringValue(catalog_table))
        response = self.metadata_store_stub.updateDataset(request)
        return _unwrap_dataset_response(response)

    def list_datasets(self, page_size, offset) -> Optional[List[DatasetMeta]]:
        """
        List registered datasets in metadata store.

        :param page_size: the limitation of the listed datasets.
        :param offset: the offset of listed datasets.
        :return: List of :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` objects,
                 return None if no datasets to be listed.
        """
        request = metadata_service_pb2.ListRequest(page_size=page_size, offset=offset)
        response = self.metadata_store_stub.listDatasets(request)
        return _unwrap_dataset_list_response(response)

    def delete_dataset_by_name(self, dataset_name) -> Status:
        """
        Delete the registered dataset by dataset name .

        :param dataset_name: the dataset name
        :return: Status.OK if the dataset is successfully deleted, Status.ERROR if the dataset does not exist otherwise.
        """
        request = metadata_service_pb2.NameRequest(name=dataset_name)
        response = self.metadata_store_stub.deleteDatasetByName(request)
        return _unwrap_delete_response(response)

    def delete_dataset_by_id(self, dataset_id):
        """
        Delete the registered dataset by dataset id .

        :param dataset_id: the dataset id
        :return: Status.OK if the dataset is successfully deleted, Status.ERROR if the dataset does not exist otherwise.
        """
        request = metadata_service_pb2.IdRequest(id=dataset_id)
        response = self.metadata_store_stub.deleteDatasetByName(request)
        return _unwrap_delete_response(response)

    '''model relation api'''

    def get_model_relation_by_id(self, model_id) -> Optional[ModelRelationMeta]:
        """
        get a specific model relation in metadata store by model id.

        :param model_id: the model id
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` object if the model relation
                 exists, Otherwise, returns None if the model relation does not exist.
        """
        request = metadata_service_pb2.IdRequest(id=model_id)
        response = self.metadata_store_stub.getModelRelationById(request)
        return _unwrap_model_relation_response(response)

    def get_model_relation_by_name(self, model_name) -> Optional[ModelRelationMeta]:
        """
        get a specific model relation in metadata store by model name.

        :param model_name: the model name
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` object if the model relation
                 exists, Otherwise, returns None if the model relation does not exist.
        """
        request = metadata_service_pb2.NameRequest(name=model_name)
        response = self.metadata_store_stub.getModelRelationByName(request)
        return _unwrap_model_relation_response(response)

    def register_model_relation(self, name, project_id) -> ModelRelationMeta:
        """
        register a model relation in metadata store

        :param name: the name of the model
        :param project_id: the project id which the model corresponded to.
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` object.
        """
        request = metadata_service_pb2.RegisterModelRelationRequest(
            model_relation=ModelRelationProto(name=name, project_id=int64Value(project_id)))
        response = self.metadata_store_stub.registerModelRelation(request)
        return _unwrap_model_relation_response(response)

    def list_model_relation(self, page_size, offset) -> List[ModelRelationMeta]:
        """
        List registered model relations in metadata store.

        :param page_size: the limitation of the listed model relations.
        :param offset: the offset of listed model relations.
        :return: List of :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` objects,
                 return None if no model relations to be listed.
        """
        request = metadata_service_pb2.ListRequest(page_size=page_size, offset=offset)
        response = self.metadata_store_stub.listModelRelation(request)
        return _unwrap_model_relation_list_response(response)

    def delete_model_relation_by_id(self, model_id) -> Status:
        """
        Delete the registered model by model id .

        :param model_id: the model id
        :return: Status.OK if the model is successfully deleted, Status.ERROR if the model does not exist otherwise.
        """
        request = metadata_service_pb2.IdRequest(id=model_id)
        response = self.metadata_store_stub.deleteModelRelationById(request)
        return _unwrap_delete_response(response)

    def delete_model_relation_by_name(self, model_name) -> Status:
        """
        Delete the registered model by model name .

        :param model_name: the model name
        :return: Status.OK if the model is successfully deleted, Status.ERROR if the model does not exist otherwise.
        """
        request = metadata_service_pb2.NameRequest(name=model_name)
        response = self.metadata_store_stub.deleteModelRelationByName(request)
        return _unwrap_delete_response(response)

    '''model api'''

    def get_model_by_id(self, model_id) -> Optional[ModelMeta]:
        """
        get a specific model in metadata store by model id.

        :param model_id: Id of registered model
        :return: A single :py:class:`ai_flow.meta.model_meta.ModelMeta` object if the model relation exists,
        Otherwise, returns None if the model relation does not exist.
        """
        request = metadata_service_pb2.IdRequest(id=model_id)
        response = self.metadata_store_stub.getModelById(request)
        return _unwrap_model_response(response)

    def get_model_by_name(self, model_name) -> Optional[ModelMeta]:
        """
        get a specific model in metadata store by model name.

        :param model_name: Name of registered model
        :return: A single :py:class:`ai_flow.meta.model_meta.ModelMeta` object if the model relation exists,
        Otherwise, returns None if the model relation does not exist.
        """
        request = metadata_service_pb2.NameRequest(name=model_name)
        response = self.metadata_store_stub.getModelByName(request)
        return _unwrap_model_response(response)

    def register_model(self, model_name, project_id, model_type, model_desc=None) -> ModelMeta:
        """
        register a model in metadata store

        :param model_name: Name of registered model
        :param project_id: Project id which registered model corresponded to.
        :param model_type: Type of registered model
        :param model_desc: Description of registered model
        :return: A single :py:class:`ai_flow.meta.model_meta.ModelMeta` object.
        """
        model_request = ModelProto(name=model_name, model_type=ModelType.Value(model_type),
                                   model_desc=stringValue(model_desc),
                                   project_id=int64Value(project_id))
        request = metadata_service_pb2.RegisterModelRequest(model=model_request)
        response = self.metadata_store_stub.registerModel(request)
        return _unwrap_model_response(response)

    def delete_model_by_id(self, model_id) -> Status:
        """
        delete registered model by model id.

        :param model_id: Id of registered model
        :return: Status.OK if registered model is successfully deleted,
                 Status.ERROR if registered model does not exist otherwise.
        """
        request = metadata_service_pb2.IdRequest(id=model_id)
        response = self.metadata_store_stub.deleteModelById(request)
        return _unwrap_delete_response(response)

    def delete_model_by_name(self, model_name) -> Status:
        """
        delete registered model by model name.

        :param model_name: Name of registered model
        :return: Status.OK if registered model is successfully deleted,
                 Status.ERROR if registered model does not exist otherwise.
        """
        request = metadata_service_pb2.NameRequest(name=model_name)
        response = self.metadata_store_stub.deleteModelByName(request)
        return _unwrap_delete_response(response)

    '''model version relation api'''

    def get_model_version_relation_by_version(self, version, model_id) -> Optional[ModelVersionRelationMeta]:
        """
        get a specific model version relation in metadata store by the model version name.

        :param version: the model version name
        :param model_id: the model id corresponded to the model version
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelVersionRelationMeta` object
                 if the model version exists, Otherwise, returns None if the model version does not exist.
        """
        request = metadata_service_pb2.ModelVersionNameRequest(name=version, model_id=model_id)
        response = self.metadata_store_stub.getModelVersionRelationByVersion(request)
        return _unwrap_model_version_relation_response(response)

    def register_model_version_relation(self, version, model_id,
                                        workflow_execution_id=None) -> ModelVersionRelationMeta:
        """
        register a model version relation in metadata store.

        :param version: the specific model version
        :param model_id: the model id corresponded to the model version
        :param workflow_execution_id: the workflow execution id corresponded to the model version
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelVersionRelationMeta` object.
        """
        model_version = ModelVersionRelationProto(version=stringValue(version), model_id=int64Value(model_id),
                                                  workflow_execution_id=int64Value(workflow_execution_id))
        request = metadata_service_pb2.RegisterModelVersionRelationRequest(model_version_relation=model_version)
        response = self.metadata_store_stub.registerModelVersionRelation(request)
        return _unwrap_model_version_relation_response(response)

    def list_model_version_relation(self, model_id, page_size, offset) -> List[ModelVersionRelationMeta]:
        """
        List registered model version relations in metadata store.

        :param model_id: the model id corresponded to the model version
        :param page_size: the limitation of the listed model version relations.
        :param offset: the offset of listed model version relations.
        :return: List of :py:class:`ai_flow.meta.model_relation_meta.ModelRelationMeta` objects,
                 return None if no model version relations to be listed.
        """
        request = metadata_service_pb2.ListModelVersionRelationRequest(model_id=model_id, page_size=page_size,
                                                                       offset=offset)
        response = self.metadata_store_stub.listModelVersionRelation(request)
        return _unwrap_model_version_relation_list_response(response)

    def delete_model_version_relation_by_version(self, version, model_id) -> Status:
        """
        Delete the registered model version by model version name .

        :param version: the model version name
        :param model_id: the model id corresponded to the model version
        :return: Status.OK if the model version is successfully deleted,
                 Status.ERROR if the model version does not exist otherwise.
        """
        request = metadata_service_pb2.ModelVersionNameRequest(name=version, model_id=model_id)
        response = self.metadata_store_stub.deleteModelVersionRelationByVersion(request)
        return _unwrap_delete_response(response)

    '''model version api'''

    def get_model_version_by_version(self, version, model_id) -> Optional[ModelVersionMeta]:
        """
        get a specific model version in metadata store by model version name.

        :param version: User-defined version of registered model
        :param model_id: the model id corresponded to the model version
        :return: A single :py:class:`ai_flow.meta.model_meta.ModelVersionMeta` object if the model version exists,
        Otherwise, returns None if the model version does not exist.
        """
        request = metadata_service_pb2.ModelVersionNameRequest(name=version, model_id=model_id)
        response = self.metadata_store_stub.getModelVersionByVersion(request)
        return _unwrap_model_version_response(response)

    def register_model_version(self, model, model_path, workflow_execution_id=None, model_metric=None,
                               model_flavor=None, version_desc=None,
                               current_stage=ModelVersionStage.GENERATED) -> ModelVersionMeta:
        """
        register a model version in metadata store.

        :param model:  model id or model meta of registered model corresponded to model version
        :param model_path: Source path where the AIFlow model is stored.
        :param workflow_execution_id: id of workflow execution corresponded to model version
        :param model_metric: Metric address from AIFlow metric server of registered model.
        :param model_flavor: (Optional) Flavor feature of AIFlow registered model option.
        :param version_desc: (Optional) Description of registered model version.
        :param current_stage: (Optional) Stage of registered model version
        :return: A single :py:class:`ai_flow.meta.model_meta.ModelVersionMeta` object.
        """

        if isinstance(model, int):
            model_id = model
        elif isinstance(model, ModelMeta):
            model_id = model.uuid
        else:
            raise Exception("can not recognize model {}".format(model))
        model_version = ModelVersionProto(version=None,
                                          model_id=int64Value(model_id),
                                          workflow_execution_id=int64Value(workflow_execution_id),
                                          model_path=stringValue(model_path),
                                          model_metric=stringValue(model_metric),
                                          model_flavor=stringValue(model_flavor),
                                          version_desc=stringValue(version_desc),
                                          current_stage=current_stage)
        request = metadata_service_pb2.RegisterModelVersionRequest(model_version=model_version)
        response = self.metadata_store_stub.registerModelVersion(request)
        return _unwrap_model_version_response(response)

    def delete_model_version_by_version(self, version, model_id) -> Status:
        """
        Delete registered model version by model version name .

        :param version: the model version name
        :param model_id: the model id corresponded to the model version
        :return: Status.OK if the model version is successfully deleted,
                 Status.ERROR if the model version does not exist otherwise.
        """
        request = metadata_service_pb2.ModelVersionNameRequest(name=version, model_id=model_id)
        response = self.metadata_store_stub.deleteModelVersionByVersion(request)
        return _unwrap_delete_response(response)

    def get_deployed_model_version(self, model_name) -> ModelVersionMeta:
        request = ModelNameRequest(name=model_name)
        response = self.metadata_store_stub.getDeployedModelVersion(request)
        return _unwrap_model_version_response(response)

    def get_latest_validated_model_version(self, model_name) -> ModelVersionMeta:
        request = ModelNameRequest(name=model_name)
        response = self.metadata_store_stub.getLatestValidatedModelVersion(request)
        return _unwrap_model_version_response(response)

    def get_latest_generated_model_version(self, model_name) -> ModelVersionMeta:
        request = ModelNameRequest(name=model_name)
        response = self.metadata_store_stub.getLatestGeneratedModelVersion(request)
        return _unwrap_model_version_response(response)

    '''workflow execution api'''

    def get_workflow_execution_by_id(self, execution_id) -> Optional[WorkflowExecutionMeta]:
        """
        get a specific workflow execution in metadata store by workflow execution id.

        :param execution_id: the workflow execution id
        :return: A single :py:class:`ai_flow.meta.workflow_execution_meta.WorkflowExecutionMeta` object
                 if the workflow execution exists, Otherwise, returns None if the workflow execution does not exist.
        """
        request = metadata_service_pb2.IdRequest(id=execution_id)
        response = self.metadata_store_stub.getWorkFlowExecutionById(request)
        return _unwrap_workflow_execution_response(response)

    def get_workflow_execution_by_name(self, execution_name) -> Optional[WorkflowExecutionMeta]:
        """
        get a specific workflow execution in metadata store by workflow execution name.

        :param execution_name: the workflow execution name
        :return: A single :py:class:`ai_flow.meta.workflow_execution_meta.WorkflowExecutionMeta` object
                 if the workflow execution exists, Otherwise, returns None if the workflow execution does not exist.
        """
        request = metadata_service_pb2.NameRequest(name=execution_name)
        response = self.metadata_store_stub.getWorkFlowExecutionByName(request)
        return _unwrap_workflow_execution_response(response)

    def register_workflow_execution(self, name, execution_state, project_id, properties=None,
                                    start_time=None, end_time=None, log_uri=None, workflow_json=None,
                                    signature=None) -> WorkflowExecutionMeta:
        """
        register a workflow execution in metadata store.

        :param name: the name of the workflow execution
        :param execution_state: the state of the workflow execution
        :param project_id: the project id corresponded to the workflow execution
        :param properties: the properties of the workflow execution
        :param start_time: the time when the workflow execution started
        :param end_time: the time when the workflow execution ended
        :param log_uri: the log uri of the workflow execution
        :param workflow_json: the workflow json of the workflow execution
        :param signature: the signature of the workflow execution
        :return: A single :py:class:`ai_flow.meta.workflow_execution_meta.WorkflowExecutionMeta` object.
        """
        execution_request = WorkflowExecutionProto(name=name, project_id=int64Value(project_id),
                                                   execution_state=StateProto.Value(execution_state),
                                                   properties=properties, start_time=int64Value(start_time),
                                                   end_time=int64Value(end_time), log_uri=stringValue(log_uri),
                                                   workflow_json=stringValue(workflow_json),
                                                   signature=stringValue(signature))
        request = metadata_service_pb2.RegisterWorkFlowExecutionRequest(workflow_execution=execution_request)
        response = self.metadata_store_stub.registerWorkFlowExecution(request)
        return _unwrap_workflow_execution_response(response)

    def update_workflow_execution(self, execution_name, execution_state=None, project_id=None,
                                  properties=None, end_time=None, log_uri=None, workflow_json=None,
                                  signature=None) -> Optional[WorkflowExecutionMeta]:
        """
        update workflow execution in metadata store.

        :param execution_name: the name of the workflow execution
        :param execution_state: the state of the workflow execution
        :param project_id: the project id corresponded to the workflow execution
        :param properties: the properties of the workflow execution
        :param end_time: the time when the workflow execution ended
        :param log_uri: the log uri of the workflow execution
        :param workflow_json: the workflow json of the workflow execution
        :param signature: the signature of the workflow execution
        :return: A single :py:class:`ai_flow.meta.workflow_execution_meta.WorkflowExecutionMeta` object
                 if update sucessfully.
        """
        execution_state = 0 if execution_state is None else StateProto.Value(execution_state)
        request = metadata_service_pb2.UpdateWorkflowExecutionRequest(name=execution_name,
                                                                      project_id=int64Value(project_id),
                                                                      execution_state=execution_state,
                                                                      properties=properties,
                                                                      end_time=int64Value(end_time),
                                                                      log_uri=stringValue(log_uri),
                                                                      workflow_json=stringValue(workflow_json),
                                                                      signature=stringValue(signature))
        response = self.metadata_store_stub.updateWorkflowExecution(request)
        return _unwrap_workflow_execution_response(response)

    def list_workflow_execution(self, page_size, offset) -> Optional[List[WorkflowExecutionMeta]]:
        """
        List registered workflow executions in metadata store.

        :param page_size: the limitation of the listed workflow executions.
        :param offset: the offset of listed workflow executions.
        :return: List of :py:class:`ai_flow.meta.workflow_execution_meta.WorkflowExecutionMeta` object,
                 return None if no workflow executions to be listed.
        """
        request = metadata_service_pb2.ListRequest(page_size=page_size, offset=offset)
        response = self.metadata_store_stub.listWorkFlowExecution(request)
        return _unwrap_workflow_execution_list_response(response)

    def update_workflow_execution_end_time(self, end_time, execution_name):
        """
        update the workflow execution end time in metadata store.

        :param end_time: the time when the workflow execution ended.
        :param execution_name: the execution name
        :return: the workflow execution uuid if the workflow execution is successfully updated, raise an exception
                 if fail to update otherwise.
        """
        request = metadata_service_pb2.UpdateWorkflowExecutionEndTimeRequest(end_time=end_time,
                                                                             name=execution_name)
        response = self.metadata_store_stub.updateWorkflowExecutionEndTime(request)
        return _unwrap_update_response(response)

    def update_workflow_execution_state(self, execution_state, execution_name):
        """
        update the workflow execution end time in metadata store.

        :param execution_state: the state of the workflow execution
        :param execution_name: the execution name
        :return: the workflow execution uuid if the workflow execution is successfully updated, raise an exception
                 if fail to update otherwise.
        """
        request = metadata_service_pb2.UpdateWorkflowExecutionStateRequest(
            state=StateProto.Value(execution_state),
            name=execution_name)
        response = self.metadata_store_stub.updateWorkflowExecutionState(request)
        return _unwrap_update_response(response)

    def delete_workflow_execution_by_id(self, execution_id) -> Status:
        """
        Delete the registered workflow execution by workflow execution id .

        :param execution_id: the workflow execution id
        :return: Status.OK if the workflow execution is successfully deleted,
                 Status.ERROR if the workflow execution does not exist otherwise.
        """
        request = metadata_service_pb2.IdRequest(id=execution_id)
        response = self.metadata_store_stub.deleteWorkflowExecutionById(request)
        return _unwrap_delete_response(response)

    def delete_workflow_execution_by_name(self, execution_name) -> Status:
        """
        Delete the registered workflow execution by workflow execution name .

        :param execution_name: the workflow execution name
        :return: Status.OK if the workflow execution is successfully deleted,
                 Status.ERROR if the workflow execution does not exist otherwise.
        """
        request = metadata_service_pb2.NameRequest(name=execution_name)
        response = self.metadata_store_stub.deleteWorkflowExecutionByName(request)
        return _unwrap_delete_response(response)

    '''job api'''

    def get_job_by_id(self, job_id) -> Optional[JobMeta]:
        """
        get a specific job in metadata store by job id.

        :param job_id: the job id
        :return: A single :py:class:`ai_flow.meta.job_meta.JobMeta` object
                 if the job exists, Otherwise, returns None if the job does not exist.
        """
        request = metadata_service_pb2.IdRequest(id=job_id)
        response = self.metadata_store_stub.getJobById(request)
        return _unwrap_job_response(response)

    def get_job_by_name(self, job_name) -> Optional[JobMeta]:
        """
        get a specific job in metadata store by job name.

        :param job_name: the job name
        :return: A single :py:class:`ai_flow.meta.job_meta.JobMeta` object
                 if the job exists, Otherwise, returns None if the job does not exist.
        """
        request = metadata_service_pb2.NameRequest(name=job_name)
        response = self.metadata_store_stub.getJobByName(request)
        return _unwrap_job_response(response)

    def register_job(self, name, workflow_execution_id, job_state=State.INIT, properties=None,
                     job_id=None, start_time=None, end_time=None, log_uri=None, signature=None) -> JobMeta:
        """
        register a job in metadata store.

        :param name: the name of the job
        :param workflow_execution_id: the workflow execution id corresponded to the job
        :param job_state: the state of the job
        :param properties: the properties of the job
        :param job_id: the job_id of the job
        :param start_time: the time when the job started
        :param end_time: the time when the job ended
        :param log_uri: the log uri of the job
        :param signature: the signature of the job
        :return: A single :py:class:`ai_flow.meta.job_meta.JobMeta` object.
        """
        job_request = JobProto(name=name, workflow_execution_id=int64Value(workflow_execution_id),
                               job_state=StateProto.Value(job_state), properties=properties,
                               job_id=stringValue(job_id), start_time=int64Value(start_time),
                               end_time=int64Value(end_time), log_uri=stringValue(log_uri),
                               signature=stringValue(signature))
        request = metadata_service_pb2.RegisterJobRequest(job=job_request)
        response = self.metadata_store_stub.registerJob(request)
        return _unwrap_job_response(response)

    def update_job(self, job_name, job_state=None, workflow_execution_id=None, properties=None,
                   job_id=None, end_time=None, log_uri=None, signature=None) -> Optional[JobMeta]:
        """
        update job in metadata store.

        :param job_name: the name of the job
        :param job_state: the state of the job
        :param workflow_execution_id: the workflow execution id of the job
        :param properties: the properties of the job
        :param job_id: the job_id of the job
        :param end_time: the time when the job ended
        :param log_uri: the log uri of the job
        :param signature: the signature of the job
        :return: A single :py:class:`ai_flow.meta.job_meta.JobMeta` object if update successfully.
        """
        job_state = 0 if job_state is None else StateProto.Value(job_state)
        request = metadata_service_pb2.UpdateJobRequest(name=job_name,
                                                        workflow_execution_id=int64Value(workflow_execution_id),
                                                        job_state=job_state, properties=properties,
                                                        job_id=stringValue(job_id), end_time=int64Value(end_time),
                                                        log_uri=stringValue(log_uri),
                                                        signature=stringValue(signature))
        response = self.metadata_store_stub.updateJob(request)
        return _unwrap_job_response(response)

    def update_job_state(self, state, job_name):
        """
        update the job state in metadata store.

        :param state: the state of the job.
        :param job_name: the job name
        :return: the job uuid if the job is successfully updated, raise an exception if fail to update otherwise.
        """
        request = metadata_service_pb2.UpdateJobStateRequest(state=StateProto.Value(state),
                                                             name=job_name)
        response = self.metadata_store_stub.updateJobState(request)
        return _unwrap_update_response(response)

    def update_job_end_time(self, end_time, job_name):
        """
        update the job end time in metadata store.

        :param end_time: the time when the job ended.
        :param job_name: the job name
        :return: the job uuid if the job is successfully updated, raise an exception if fail to update otherwise.
        """
        request = metadata_service_pb2.UpdateJobEndTimeRequest(end_time=end_time, name=job_name)
        response = self.metadata_store_stub.updateJobEndTime(request)
        return _unwrap_update_response(response)

    def list_job(self, page_size, offset) -> Optional[List[JobMeta]]:
        """
        List registered jobs in metadata store.

        :param page_size: the limitation of the listed jobs.
        :param offset: the offset of listed jobs.
        :return: List of :py:class:`ai_flow.meta.job_meta.JobMeta` objects,
                 return None if no jobs to be listed.
        """
        request = metadata_service_pb2.ListRequest(page_size=page_size, offset=offset)
        response = self.metadata_store_stub.listJob(request)
        return _unwrap_job_list_response(response)

    def delete_job_by_id(self, job_id) -> Status:
        """
        Delete the registered job by job id .

        :param job_id: the job id
        :return: Status.OK if the job is successfully deleted,
                 Status.ERROR if the job does not exist otherwise.
        """
        request = metadata_service_pb2.IdRequest(id=job_id)
        response = self.metadata_store_stub.deleteJobById(request)
        return _unwrap_delete_response(response)

    def delete_job_by_name(self, job_name) -> Status:
        """
        Delete the registered job by job name .

        :param job_name: the job name
        :return: Status.OK if the job is successfully deleted,
                 Status.ERROR if the job does not exist otherwise.
        """
        request = metadata_service_pb2.NameRequest(name=job_name)
        response = self.metadata_store_stub.deleteJobByName(request)
        return _unwrap_delete_response(response)

    '''project api'''

    def get_project_by_id(self, project_id) -> Optional[ProjectMeta]:
        """
        get a specific project in metadata store by project id

        :param project_id: the project id
        :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object if the project exists,
                 Otherwise, returns None if the project does not exist.
        """
        request = metadata_service_pb2.IdRequest(id=project_id)
        response = self.metadata_store_stub.getProjectById(request)
        return _unwrap_project_response(response)

    def get_project_by_name(self, project_name) -> Optional[ProjectMeta]:
        """
        get a specific project in metadata store by project name
        :param project_name: the project name
        :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object if the project exists,
                 Otherwise, returns None if the project does not exist.
        """
        request = metadata_service_pb2.NameRequest(name=project_name)
        response = self.metadata_store_stub.getProjectByName(request)
        return _unwrap_project_response(response)

    def register_project(self, name, uri: Text = None, properties: Properties = None) -> ProjectMeta:
        """
        register a project in metadata store.

        :param name: the name of the project
        :param uri: the uri of the project
        :param properties: the properties of the project
        :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object.
        """
        project_request = ProjectProto(name=name, uri=stringValue(uri), properties=properties)
        request = metadata_service_pb2.RegisterProjectRequest(project=project_request)
        response = self.metadata_store_stub.registerProject(request)
        return _unwrap_project_response(response)

    def update_project(self, project_name: Text, uri: Text = None, properties: Properties = None) -> Optional[ProjectMeta]:
        """
        update project in metadata store.

        :param project_name: the name of the project
        :param uri: the uri of the project
        :param properties: the properties of the project
        :return: A single :py:class:`ai_flow.meta.project.ProjectMeta` object if update successfully.
        """
        request = metadata_service_pb2.UpdateProjectRequest(name=project_name, uri=stringValue(uri),
                                                            properties=properties)
        response = self.metadata_store_stub.updateProject(request)
        return _unwrap_project_response(response)

    def list_project(self, page_size, offset) -> Optional[List[ProjectMeta]]:
        """
        List registered projects in metadata store.

        :param page_size: the limitation of the listed projects.
        :param offset: the offset of listed projects.
        :return: List of :py:class:`ai_flow.meta.project_meta.ProjectMeta` objects,
                 return None if no projects to be listed.
        """
        request = metadata_service_pb2.ListRequest(page_size=page_size, offset=offset)
        response = self.metadata_store_stub.listProject(request)
        return _unwrap_project_list_response(response)

    def delete_project_by_id(self, project_id) -> Status:
        """
        Delete the registered project by project id .

        :param project_id: the project id
        :return: Status.OK if the project is successfully deleted, Status.ERROR if the project does not exist otherwise.
        """
        request = metadata_service_pb2.IdRequest(id=project_id)
        response = self.metadata_store_stub.deleteProjectById(request)
        return _unwrap_delete_response(response)

    def delete_project_by_name(self, project_name) -> Status:
        """
        Delete the registered project by project name .

        :param project_name: the project name
        :return: Status.OK if the project is successfully deleted, Status.ERROR if the project does not exist otherwise.
        """
        request = metadata_service_pb2.NameRequest(name=project_name)
        response = self.metadata_store_stub.deleteProjectByName(request)
        return _unwrap_delete_response(response)

    '''artifact api'''

    def get_artifact_by_id(self, artifact_id) -> Optional[ArtifactMeta]:
        """
        get a specific artifact in metadata store by artifact id.

        :param artifact_id: the artifact id
        :return: A single :py:class:`ai_flow.meta.artifact_meta.ArtifactMeta` object
                 if the artifact exists, Otherwise, returns None if the artifact does not exist.
        """
        request = metadata_service_pb2.IdRequest(id=artifact_id)
        response = self.metadata_store_stub.getArtifactById(request)
        return _unwrap_artifact_response(response)

    def get_artifact_by_name(self, artifact_name) -> Optional[ArtifactMeta]:
        """
        get a specific artifact in metadata store by artifact name.

        :param artifact_name: the artifact name
        :return: A single :py:class:`ai_flow.meta.artifact_meta.ArtifactMeta` object
                 if the artifact exists, Otherwise, returns None if the artifact does not exist.
        """
        request = metadata_service_pb2.NameRequest(name=artifact_name)
        response = self.metadata_store_stub.getArtifactByName(request)
        return _unwrap_artifact_response(response)

    def register_artifact(self, name: Text, artifact_type: Text = None, description: Text = None,
                          uri: Text = None, properties: Properties = None) -> ArtifactMeta:
        """
        register an artifact in metadata store.

        :param name: the name of the artifact
        :param artifact_type: the type of the artifact
        :param description: the description of the artifact
        :param uri: the uri of the artifact
        :param properties: the properties of the artifact
        :return: A single :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` object.
        """
        artifact_request = ArtifactProto(name=name, artifact_type=stringValue(artifact_type),
                                         description=stringValue(description), uri=stringValue(uri),
                                         properties=properties)
        request = metadata_service_pb2.RegisterArtifactRequest(artifact=artifact_request)
        response = self.metadata_store_stub.registerArtifact(request)
        return _unwrap_artifact_response(response)

    def update_artifact(self, artifact_name: Text, artifact_type: Text = None,
                        description: Text = None, uri: Text = None,
                        properties: Properties = None) -> Optional[ArtifactMeta]:
        """
        update artifact in metadata store.

        :param artifact_name: the name of the artifact
        :param artifact_type: the type of the artifact
        :param description: the description of the artifact
        :param uri: the batch uri of the artifact
        :param properties: the properties of the artifact
        :return: A single :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` object if update successfully.
        """
        request = metadata_service_pb2.UpdateArtifactRequest(name=artifact_name,
                                                             artifact_type=stringValue(artifact_type),
                                                             description=stringValue(description),
                                                             uri=stringValue(uri),
                                                             properties=properties)
        response = self.metadata_store_stub.updateArtifact(request)
        return _unwrap_artifact_response(response)

    def list_artifact(self, page_size, offset) -> Optional[List[ArtifactMeta]]:
        """
        List registered artifacts in metadata store.

        :param page_size: the limitation of the listed artifacts.
        :param offset: the offset of listed artifacts.
        :return: List of :py:class:`ai_flow.meta.artifact_meta.py.ArtifactMeta` objects,
                 return None if no artifacts to be listed.
        """
        request = metadata_service_pb2.ListRequest(page_size=page_size, offset=offset)
        response = self.metadata_store_stub.listArtifact(request)
        return _unwrap_artifact_list_response(response)

    def delete_artifact_by_id(self, artifact_id) -> Status:
        """
        Delete the registered artifact by artifact id .

        :param artifact_id: the artifact id
        :return: Status.OK if the artifact is successfully deleted,
                 Status.ERROR if the artifact does not exist otherwise.
        """
        request = metadata_service_pb2.IdRequest(id=artifact_id)
        response = self.metadata_store_stub.deleteArtifactById(request)
        return _unwrap_delete_response(response)

    def delete_artifact_by_name(self, artifact_name) -> Status:
        """
        Delete the registered artifact by artifact name .

        :param artifact_name: the artifact name
        :return: Status.OK if the artifact is successfully deleted,
                 Status.ERROR if the artifact does not exist otherwise.
        """
        request = metadata_service_pb2.NameRequest(name=artifact_name)
        response = self.metadata_store_stub.deleteArtifactByName(request)
        return _unwrap_delete_response(response)
