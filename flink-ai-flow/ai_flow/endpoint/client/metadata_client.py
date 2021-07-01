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
from ai_flow.meta.workflow_meta import WorkflowMeta
from typing import Optional, Text, List

import grpc

from ai_flow.common.status import Status
from ai_flow.meta.artifact_meta import ArtifactMeta
from ai_flow.meta.dataset_meta import DatasetMeta, Properties, DataType
from ai_flow.meta.model_meta import ModelMeta, ModelVersionMeta
from ai_flow.meta.model_relation_meta import ModelRelationMeta, ModelVersionRelationMeta
from ai_flow.meta.project_meta import ProjectMeta
from ai_flow.metadata_store.utils.MetaToProto import MetaToProto
from ai_flow.protobuf import metadata_service_pb2_grpc, metadata_service_pb2
from ai_flow.protobuf.message_pb2 import DatasetProto, SchemaProto, ModelRelationProto, ModelProto, \
    ModelVersionRelationProto, ModelVersionProto, ProjectProto, \
    ArtifactProto, ModelVersionStage, WorkflowMetaProto
from ai_flow.protobuf.metadata_service_pb2 import ModelNameRequest
from ai_flow.endpoint.server import stringValue, int64Value
from ai_flow.endpoint.client.base_client import BaseClient
from ai_flow.endpoint.server.util import _unwrap_dataset_response, \
    transform_dataset_type_list_to_proto, _unwrap_dataset_list_response, _unwrap_delete_response, \
    _unwrap_model_relation_response, _unwrap_model_relation_list_response, _unwrap_model_response, \
    _unwrap_model_version_relation_response, _unwrap_model_version_relation_list_response, \
    _unwrap_model_version_response, \
    _unwrap_project_response, _unwrap_project_list_response, \
    _unwrap_artifact_response, _unwrap_artifact_list_response, _unwrap_workflow_response, _unwrap_workflow_list_response


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
                         uri: Text = None, properties: Properties = None, name_list: List[Text] = None,
                         type_list: List[DataType] = None) -> DatasetMeta:
        """
        register an dataset in metadata store.

        :param name: the name of the dataset
        :param data_format: the data format of the dataset
        :param description: the description of the dataset
        :param uri: the uri of the dataset
        :param properties: the properties of the dataset
        :param name_list: the name list of dataset's schema
        :param type_list: the type list corresponded to the name list of dataset's schema
        :return: A single :py:class:`ai_flow.meta.dataset_meta.DatasetMeta` object.
        """
        request = metadata_service_pb2.RegisterDatasetRequest(
            dataset=DatasetProto(name=name,  data_format=stringValue(data_format),
                                 description=stringValue(description), uri=stringValue(uri),
                                 properties=properties,
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
                       description: Text = None, uri: Text = None,
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

    def register_model(self, model_name, project_id, model_desc=None) -> ModelMeta:
        """
        register a model in metadata store

        :param model_name: Name of registered model
        :param project_id: Project id which registered model corresponded to.
        :param model_desc: Description of registered model
        :return: A single :py:class:`ai_flow.meta.model_meta.ModelMeta` object.
        """
        model_request = ModelProto(name=model_name,
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
                                        project_snapshot_id=None) -> ModelVersionRelationMeta:
        """
        register a model version relation in metadata store.

        :param version: the specific model version
        :param model_id: the model id corresponded to the model version
        :param project_snapshot_id: the project snapshot id corresponded to the model version
        :return: A single :py:class:`ai_flow.meta.model_relation_meta.ModelVersionRelationMeta` object.
        """
        model_version = ModelVersionRelationProto(version=stringValue(version), model_id=int64Value(model_id),
                                                  project_snapshot_id=int64Value(project_snapshot_id))
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
        Get a specific model version in metadata store by model version name.

        :param version: User-defined version of registered model
        :param model_id: The model id corresponded to the model version
        :return: A single :py:class:`ai_flow.meta.model_meta.ModelVersionMeta` object if the model version exists,
        Otherwise, returns None if the model version does not exist.
        """
        request = metadata_service_pb2.ModelVersionNameRequest(name=version, model_id=model_id)
        response = self.metadata_store_stub.getModelVersionByVersion(request)
        return _unwrap_model_version_response(response)

    def register_model_version(self, model, model_path, project_snapshot_id=None,
                               model_type=None, version_desc=None,
                               current_stage=ModelVersionStage.GENERATED) -> ModelVersionMeta:
        """
        register a model version in metadata store.

        :param model: Model id or model meta of registered model corresponded to model version
        :param model_path: Source path where the AIFlow model is stored.
        :param project_snapshot_id: Id of project snapshot corresponded to model version
        :param model_type: (Optional) Type of AIFlow registered model option.
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
                                          project_snapshot_id=int64Value(project_snapshot_id),
                                          model_path=stringValue(model_path),
                                          model_type=stringValue(model_type),
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

    '''workflow api'''

    def register_workflow(self, name: Text, project_id: int, properties: Properties = None) -> WorkflowMeta:
        """
        Register a workflow in metadata store.

        :param name: the workflow name
        :param project_id: the id of project which contains the workflow
        :param properties: the workflow properties
        """
        workflow_request = WorkflowMetaProto(name=name,
                                             project_id=int64Value(project_id),
                                             properties=properties)
        request = metadata_service_pb2.RegisterWorkflowRequest(workflow=workflow_request)
        response = self.metadata_store_stub.registerWorkflow(request)
        return _unwrap_workflow_response(response)

    def get_workflow_by_name(self, project_name: Text, workflow_name: Text) -> Optional[WorkflowMeta]:
        """
        Get a workflow by specific project name and workflow name

        :param project_name: the name of project which contains the workflow
        :param workflow_name: the workflow name
        """
        request = metadata_service_pb2.WorkflowNameRequest(workflow_name=workflow_name,
                                                           project_name=project_name)
        response = self.metadata_store_stub.getWorkflowByName(request)
        return _unwrap_workflow_response(response)

    def get_workflow_by_id(self, workflow_id: int) -> Optional[WorkflowMeta]:
        """
        Get a workflow by specific uuid

        :param workflow_id: the uuid of workflow
        """
        request = metadata_service_pb2.IdRequest(id=workflow_id)
        response = self.metadata_store_stub.getWorkflowById(request)
        return _unwrap_workflow_response(response)

    def list_workflows(self, project_name: Text, page_size: int, offset: int) -> Optional[List[WorkflowMeta]]:
        """
        List all workflows of the specific project

        :param project_name: the name of project which contains the workflow
        :param page_size      Limitation of listed workflows.
        :param offset        Offset of listed workflows.
        """
        request = metadata_service_pb2.ListWorkflowsRequest(project_name=project_name,
                                                            page_size=page_size,
                                                            offset=offset)
        response = self.metadata_store_stub.listWorkflows(request)
        return _unwrap_workflow_list_response(response)

    def delete_workflow_by_name(self, project_name: Text, workflow_name: Text) -> Status:
        """
        Delete the workflow by specific project and workflow name

        :param project_name: the name of project which contains the workflow
        :param workflow_name: the workflow name
        """
        request = metadata_service_pb2.WorkflowNameRequest(workflow_name=workflow_name,
                                                           project_name=project_name)
        response = self.metadata_store_stub.deleteWorkflowByName(request)
        return _unwrap_delete_response(response)

    def delete_workflow_by_id(self, workflow_id: int) -> Status:
        """
        Delete the workflow by specific id

        :param workflow_id: the uuid of workflow
        """
        request = metadata_service_pb2.IdRequest(id=workflow_id)
        response = self.metadata_store_stub.deleteWorkflowById(request)
        return _unwrap_delete_response(response)

    def update_workflow(self, workflow_name: Text, project_name: Text,
                        properties: Properties = None) -> Optional[WorkflowMeta]:
        """
        Update the workflow

        :param workflow_name: the workflow name
        :param project_name: the name of project which contains the workflow
        :param properties: (Optional) the properties need to be updated
        """
        request = metadata_service_pb2.UpdateWorkflowRequest(workflow_name=workflow_name,
                                                             project_name=project_name,
                                                             properties=properties)
        response = self.metadata_store_stub.updateWorkflow(request)
        return _unwrap_workflow_response(response)
