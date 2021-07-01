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
from typing import List

from ai_flow.meta.artifact_meta import ArtifactMeta
from ai_flow.meta.dataset_meta import DatasetMeta
from ai_flow.meta.model_relation_meta import ModelRelationMeta, ModelVersionRelationMeta
from ai_flow.meta.project_meta import ProjectMeta
from ai_flow.protobuf.message_pb2 import DatasetProto, DataTypeProto, \
    SchemaProto, ProjectProto, \
    ModelRelationProto, ModelVersionRelationProto, ModelProto, ModelVersionProto, ArtifactProto, \
    ModelVersionStage, WorkflowMetaProto
from ai_flow.endpoint.server import stringValue, int64Value


class MetaToProto:
    @staticmethod
    def dataset_meta_to_proto(dataset_mata) -> DatasetMeta:
        if dataset_mata is None:
            return None
        else:
            if dataset_mata.schema is not None:
                name_list = dataset_mata.schema.name_list
                type_list = dataset_mata.schema.type_list
                data_type_list = []
                if type_list is not None:
                    for data_type in type_list:
                        data_type_list.append(DataTypeProto.Value(data_type))
                else:
                    data_type_list = None
            else:
                name_list = None
                data_type_list = None
            schema = SchemaProto(name_list=name_list,
                                 type_list=data_type_list)
        return DatasetProto(
            uuid=dataset_mata.uuid,
            name=dataset_mata.name,
            properties=dataset_mata.properties,
            data_format=stringValue(dataset_mata.data_format),
            description=stringValue(dataset_mata.description),
            uri=stringValue(dataset_mata.uri),
            create_time=int64Value(dataset_mata.create_time),
            update_time=int64Value(dataset_mata.update_time),
            schema=schema,
            catalog_name=stringValue(dataset_mata.catalog_name),
            catalog_type=stringValue(dataset_mata.catalog_type),
            catalog_database=stringValue(dataset_mata.catalog_database),
            catalog_connection_uri=stringValue(dataset_mata.catalog_connection_uri),
            catalog_table=stringValue(dataset_mata.catalog_table))

    @staticmethod
    def dataset_meta_list_to_proto(datasets: List[DatasetMeta]) -> List[DatasetProto]:
        list_dataset_proto = []
        for dataset in datasets:
            list_dataset_proto.append(MetaToProto.dataset_meta_to_proto(dataset))
        return list_dataset_proto

    @staticmethod
    def project_meta_to_proto(project_meta: ProjectMeta) -> ProjectProto:
        if project_meta is None:
            return None
        else:
            return ProjectProto(
                uuid=project_meta.uuid,
                name=project_meta.name,
                properties=project_meta.properties,
                uri=stringValue(project_meta.uri))

    @staticmethod
    def project_meta_list_to_proto(projects: List[ProjectMeta]) -> List[ProjectProto]:
        project_proto_list = []
        for project in projects:
            project_proto_list.append(MetaToProto.project_meta_to_proto(project))
        return project_proto_list

    @staticmethod
    def workflow_meta_to_proto(workflow_meta: WorkflowMeta) -> WorkflowMetaProto:
        if workflow_meta is None:
            return None
        else:
            return WorkflowMetaProto(
                name=workflow_meta.name,
                project_id=int64Value(workflow_meta.project_id),
                properties=workflow_meta.properties,
                create_time=int64Value(workflow_meta.create_time),
                update_time=int64Value(workflow_meta.update_time),
                uuid=workflow_meta.uuid)

    @staticmethod
    def workflow_meta_list_to_proto(workflows: List[WorkflowMeta]) -> List[WorkflowMetaProto]:
        workflow_proto_list = []
        for workflow in workflows:
            workflow_proto_list.append(MetaToProto.workflow_meta_to_proto(workflow))
        return workflow_proto_list

    @staticmethod
    def artifact_meta_to_proto(artifact_meta: ArtifactMeta) -> ArtifactProto:
        if artifact_meta is None:
            return None
        else:
            return ArtifactProto(
                uuid=artifact_meta.uuid,
                name=artifact_meta.name,
                properties=artifact_meta.properties,
                artifact_type=stringValue(artifact_meta.artifact_type),
                description=stringValue(artifact_meta.description),
                uri=stringValue(artifact_meta.uri),
                create_time=int64Value(artifact_meta.create_time),
                update_time=int64Value(artifact_meta.update_time))

    @staticmethod
    def artifact_meta_list_to_proto(artifacts: List[ArtifactMeta]) -> List[ArtifactProto]:
        artifact_proto_list = []
        for artifact in artifacts:
            artifact_proto_list.append(MetaToProto.artifact_meta_to_proto(artifact))
        return artifact_proto_list

    @staticmethod
    def model_relation_meta_to_proto(model_relation_meta: ModelRelationMeta) -> ModelRelationProto:
        if model_relation_meta is None:
            return None
        else:
            return ModelRelationProto(
                uuid=model_relation_meta.uuid,
                name=model_relation_meta.name,
                project_id=int64Value(model_relation_meta.project_id))

    @staticmethod
    def model_relation_meta_list_to_proto(model_relation_meta_list: List[ModelRelationMeta]) -> List[
        ModelRelationProto]:
        model_proto_list = []
        for model in model_relation_meta_list:
            model_proto_list.append(MetaToProto.model_relation_meta_to_proto(model))
        return model_proto_list

    @staticmethod
    def model_version_relation_meta_to_proto(
            model_version_relation: ModelVersionRelationMeta) -> ModelVersionRelationProto:
        if model_version_relation is None:
            return None
        else:
            return ModelVersionRelationProto(
                version=stringValue(model_version_relation.version),
                model_id=int64Value(model_version_relation.model_id),
                project_snapshot_id=int64Value(model_version_relation.project_snapshot_id))

    @staticmethod
    def model_version_relation_meta_list_to_proto(model_version_relation_list: List[ModelVersionRelationMeta]) -> List[
        ModelVersionRelationProto]:
        model_version_list = []
        for model_version in model_version_relation_list:
            model_version_list.append(MetaToProto.model_version_relation_meta_to_proto(model_version))
        return model_version_list

    @staticmethod
    def model_meta_to_proto(model_relation, model_center_detail) -> ModelProto:
        if model_relation is not None and model_center_detail is not None:
            return ModelProto(uuid=model_relation.uuid, name=model_relation.name,
                              project_id=int64Value(model_relation.project_id),
                              model_desc=stringValue(model_center_detail.model_desc))
        else:
            return None

    @staticmethod
    def model_version_meta_to_proto(model_version_relation, model_center_detail) -> ModelVersionProto:
        if model_version_relation is not None and model_center_detail is not None:
            return ModelVersionProto(
                version=stringValue(model_version_relation.version),
                model_id=int64Value(model_version_relation.model_id),
                project_snapshot_id=int64Value(model_version_relation.project_snapshot_id),
                model_path=stringValue(model_center_detail.model_path),
                model_type=stringValue(model_center_detail.model_type),
                version_desc=stringValue(model_center_detail.version_desc),
                current_stage=model_center_detail.current_stage)
        else:
            return None

    @staticmethod
    def model_version_store_to_proto(model_version_relation, model_center_detail) -> ModelVersionProto:
        if model_version_relation is not None and model_center_detail is not None:
            return ModelVersionProto(
                version=stringValue(model_version_relation.version),
                model_id=int64Value(model_version_relation.model_id),
                project_snapshot_id=int64Value(model_version_relation.project_snapshot_id),
                model_path=stringValue(model_center_detail.model_path),
                model_type=stringValue(model_center_detail.model_type),
                version_desc=stringValue(model_center_detail.version_desc),
                current_stage=ModelVersionStage.Value(model_center_detail.current_stage.upper()))
        else:
            return None
