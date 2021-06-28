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
from ai_flow.meta.artifact_meta import ArtifactMeta
from ai_flow.meta.dataset_meta import DatasetMeta, List, DataType, Schema
from ai_flow.meta.job_meta import State
from ai_flow.meta.model_meta import ModelMeta, ModelVersionMeta
from ai_flow.meta.model_relation_meta import ModelRelationMeta, ModelVersionRelationMeta
from ai_flow.meta.project_meta import ProjectMeta
from ai_flow.protobuf.message_pb2 import DatasetProto, ProjectProto, \
    StateProto, ModelRelationProto, ModelVersionRelationProto, ModelProto, ModelVersionProto, \
    ArtifactProto, ModelVersionStage, DataTypeProto


class ProtoToMeta:

    @staticmethod
    def proto_to_dataset_meta(dataset_proto: DatasetProto) -> DatasetMeta:
        properties = dataset_proto.properties
        if properties == {}:
            properties = None
        name_list = dataset_proto.schema.name_list
        if not name_list:
            name_list = None
        type_list = dataset_proto.schema.type_list
        if not type_list:
            data_type_list = None
        else:
            data_type_list = []
            for c in type_list:
                data_type_list.append(DataType(DataTypeProto.Name(c)))
        data_format = dataset_proto.data_format.value if dataset_proto.HasField('data_format') else None
        description = dataset_proto.description.value if dataset_proto.HasField('description') else None
        uri = dataset_proto.uri.value if dataset_proto.HasField('uri') else None
        create_time = dataset_proto.create_time.value if dataset_proto.HasField('create_time') else None
        update_time = dataset_proto.update_time.value if dataset_proto.HasField('update_time') else None
        catalog_name = dataset_proto.catalog_name.value if dataset_proto.HasField('catalog_name') else None
        catalog_type = dataset_proto.catalog_type.value if dataset_proto.HasField('catalog_type') else None
        catalog_database = dataset_proto.catalog_database.value if dataset_proto.HasField('catalog_database') else None
        catalog_connection_uri = dataset_proto.catalog_connection_uri.value \
            if dataset_proto.HasField('catalog_connection_uri') else None
        catalog_table = dataset_proto.catalog_table.value if dataset_proto.HasField('catalog_table') else None
        schema = Schema(name_list=name_list, type_list=data_type_list)
        return DatasetMeta(uuid=dataset_proto.uuid,
                           name=dataset_proto.name,
                           data_format=data_format,
                           description=description,
                           uri=uri,
                           create_time=create_time,
                           update_time=update_time,
                           properties=properties,
                           schema=schema,
                           catalog_name=catalog_name,
                           catalog_type=catalog_type,
                           catalog_database=catalog_database,
                           catalog_connection_uri=catalog_connection_uri,
                           catalog_table=catalog_table)

    @staticmethod
    def proto_to_dataset_meta_list(dataset_proto_list: List[DatasetProto]) -> List[DatasetMeta]:
        list_dataset_meta = []
        for dataset_proto in dataset_proto_list:
            list_dataset_meta.append(ProtoToMeta.proto_to_dataset_meta(dataset_proto))
        return list_dataset_meta

    @staticmethod
    def proto_to_project_meta(project_proto: ProjectProto) -> ProjectMeta:
        properties = project_proto.properties
        if properties == {}:
            properties = None
        return ProjectMeta(
            uuid=project_proto.uuid,
            name=project_proto.name,
            properties=properties,
            uri=project_proto.uri.value if project_proto.HasField('uri') else None)

    @staticmethod
    def proto_to_project_meta_list(projects: List[ProjectProto]) -> List[ProjectMeta]:
        project_meta_list = []
        for project in projects:
            project_meta_list.append(ProtoToMeta.proto_to_project_meta(project))
        return project_meta_list

    @staticmethod
    def proto_to_artifact_meta(artifact_proto: ArtifactProto) -> ArtifactMeta:
        properties = artifact_proto.properties
        if properties == {}:
            properties = None
        return ArtifactMeta(
            uuid=artifact_proto.uuid,
            name=artifact_proto.name,
            properties=properties,
            artifact_type=artifact_proto.artifact_type.value if artifact_proto.HasField('artifact_type') else None,
            description=artifact_proto.description.value if artifact_proto.HasField('description') else None,
            uri=artifact_proto.uri.value if artifact_proto.HasField('uri') else None,
            create_time=artifact_proto.create_time.value if artifact_proto.HasField('create_time') else None,
            update_time=artifact_proto.update_time.value if artifact_proto.HasField('update_time') else None)

    @staticmethod
    def proto_to_artifact_meta_list(artifacts: List[ArtifactProto]) -> List[ArtifactMeta]:
        artifact_meta_list = []
        for artifact in artifacts:
            artifact_meta_list.append(ProtoToMeta.proto_to_artifact_meta(artifact))
        return artifact_meta_list

    @staticmethod
    def proto_to_state(state):
        if state == StateProto.INIT:
            return State.INIT
        elif state == StateProto.STARTING:
            return State.STARTING
        elif state == StateProto.RUNNING:
            return State.RUNNING
        elif state == StateProto.FINISHED:
            return State.FINISHED
        elif state == StateProto.FAILED:
            return State.FAILED
        elif state == StateProto.KILLING:
            return State.KILLING
        elif state == StateProto.KILLED:
            return State.KILLED

    @staticmethod
    def proto_to_model_relation_meta(model_relation_proto: ModelRelationProto) -> ModelRelationMeta:
        return ModelRelationMeta(uuid=model_relation_proto.uuid,
                                 name=model_relation_proto.name,
                                 project_id=model_relation_proto.project_id.value
                                 if model_relation_proto.HasField('project_id') else None)

    @staticmethod
    def proto_to_model_relation_meta_list(model_proto_relation_list: List[ModelRelationProto]) -> List[
        ModelRelationMeta]:
        model_relation_meta_list = []
        for model_proto in model_proto_relation_list:
            model_relation_meta_list.append(ProtoToMeta.proto_to_model_relation_meta(model_proto))
        return model_relation_meta_list

    @staticmethod
    def proto_to_model_meta(model_proto: ModelProto) -> ModelMeta:
        return ModelMeta(uuid=model_proto.uuid, name=model_proto.name,
                         model_desc=model_proto.model_desc.value if model_proto.HasField(
                             'model_desc') else None,
                         project_id=model_proto.project_id.value if model_proto.HasField('project_id') else None)

    @staticmethod
    def proto_to_model_meta_list(model_proto_list: List[ModelProto]) -> List[ModelMeta]:
        model_meta_list = []
        for model_proto in model_proto_list:
            model_meta_list.append(ProtoToMeta.proto_to_model_meta(model_proto))
        return model_meta_list

    @staticmethod
    def proto_to_model_version_relation_meta(
            model_version_proto: ModelVersionRelationProto) -> ModelVersionRelationMeta:
        return ModelVersionRelationMeta(
            version=model_version_proto.version.value if model_version_proto.HasField('version') else None,
            model_id=model_version_proto.model_id.value if model_version_proto.HasField('model_id') else None,
            project_snapshot_id=model_version_proto.project_snapshot_id.value
            if model_version_proto.HasField('project_snapshot_id') else None)

    @staticmethod
    def proto_to_model_version_relation_meta_list(model_version_proto_list: List[ModelVersionRelationProto]) -> List[
        ModelVersionRelationMeta]:
        model_version_relation_meta_list = []
        for model_version_proto in model_version_proto_list:
            model_version_relation_meta_list.append(
                ProtoToMeta.proto_to_model_version_relation_meta(model_version_proto))
        return model_version_relation_meta_list

    @staticmethod
    def proto_to_model_version_meta(
            model_version_proto: ModelVersionProto) -> ModelVersionMeta:
        return ModelVersionMeta(
            version=model_version_proto.version.value if model_version_proto.HasField(
                'version') else None,
            model_id=model_version_proto.model_id.value if model_version_proto.HasField('model_id') else None,
            model_path=model_version_proto.model_path.value if model_version_proto.HasField(
                'model_path') else None,
            model_type=model_version_proto.model_type.value if model_version_proto.HasField(
                'model_type') else None,
            project_snapshot_id=model_version_proto.project_snapshot_id.value if model_version_proto.HasField(
                'project_snapshot_id') else None,
            version_desc=model_version_proto.version_desc.value if model_version_proto.HasField(
                'version_desc') else None,
            current_stage=ModelVersionStage.Name(model_version_proto.current_stage))

    @staticmethod
    def proto_to_model_version_meta_list(model_version_proto_list: List[ModelVersionProto]) -> List[ModelVersionMeta]:
        model_version_meta_list = []
        for model_version_proto in model_version_proto_list:
            model_version_meta_list.append(
                ProtoToMeta.proto_to_model_version_meta(model_version_proto))
        return model_version_meta_list
