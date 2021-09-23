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
from ai_flow.api.context_extractor import ContextExtractor, BroadcastAllContextExtractor

from ai_flow.context.project_context import current_project_config
from ai_flow.meta.workflow_meta import WorkflowMeta
from typing import Optional, Text, List, Tuple, Union

from ai_flow.client.ai_flow_client import get_ai_flow_client
from ai_flow.common.properties import Properties
from ai_flow.common.status import Status
from ai_flow.meta.artifact_meta import ArtifactMeta
from ai_flow.meta.dataset_meta import DatasetMeta, DataType
from ai_flow.meta.metric_meta import MetricType, MetricMeta, MetricSummary
from ai_flow.meta.model_meta import ModelMeta, ModelVersionMeta
from ai_flow.meta.model_relation_meta import ModelRelationMeta, ModelVersionRelationMeta
from ai_flow.meta.project_meta import ProjectMeta
from ai_flow.model_center.entity.model_version_detail import ModelVersionDetail
from ai_flow.model_center.entity.model_version_stage import ModelVersionStage
from ai_flow.model_center.entity.registered_model_detail import RegisteredModelDetail


def get_dataset_by_id(dataset_id) -> Optional[DatasetMeta]:
    return get_ai_flow_client().get_dataset_by_id(dataset_id)


def get_dataset_by_name(dataset_name) -> Optional[DatasetMeta]:
    return get_ai_flow_client().get_dataset_by_name(dataset_name)


def register_dataset(name: Text, data_format: Text = None, description: Text = None,
                     uri: Text = None, properties: Properties = None, name_list: List[Text] = None,
                     type_list: List[DataType] = None) -> DatasetMeta:
    return get_ai_flow_client().register_dataset(name=name, data_format=data_format, description=description,
                                                 uri=uri, properties=properties, name_list=name_list, type_list=type_list)


def register_dataset_with_catalog(name: Text,
                                  catalog_name: Text, catalog_type: Text,
                                  catalog_connection_uri: Text,
                                  catalog_table: Text, catalog_database: Text = None) -> DatasetMeta:
    return get_ai_flow_client().register_dataset_with_catalog(name=name,
                                                              catalog_name=catalog_name, catalog_type=catalog_type,
                                                              catalog_connection_uri=catalog_connection_uri,
                                                              catalog_table=catalog_table,
                                                              catalog_database=catalog_database)


def register_datasets(datasets: List[DatasetMeta]) -> List[DatasetMeta]:
    return get_ai_flow_client().register_datasets(datasets)


def update_dataset(dataset_name: Text,
                   data_format: Text = None, description: Text = None,
                   uri: Text = None,
                   properties: Properties = None, name_list: List[Text] = None,
                   type_list: List[DataType] = None, catalog_name: Text = None,
                   catalog_type: Text = None, catalog_database: Text = None,
                   catalog_connection_uri: Text = None,
                   catalog_table: Text = None) -> Optional[DatasetMeta]:
    return get_ai_flow_client().update_dataset(dataset_name, data_format, description,
                                               uri, properties, name_list, type_list, catalog_name,
                                               catalog_type, catalog_database, catalog_connection_uri,
                                               catalog_table)


def list_datasets(page_size, offset) -> Optional[List[DatasetMeta]]:
    return get_ai_flow_client().list_datasets(page_size, offset)


def delete_dataset_by_name(dataset_name) -> Status:
    return get_ai_flow_client().delete_dataset_by_name(dataset_name)


def delete_dataset_by_id(dataset_id) -> Status:
    return get_ai_flow_client().delete_dataset_by_id(dataset_id)


def get_model_relation_by_id(model_id) -> Optional[ModelRelationMeta]:
    return get_ai_flow_client().get_model_by_id(model_id)


def get_model_relation_by_name(model_name) -> Optional[ModelRelationMeta]:
    return get_ai_flow_client().get_model_relation_by_name(model_name)


def register_model_relation(name, project_id) -> ModelRelationMeta:
    return get_ai_flow_client().register_model_relation(name, project_id)


def list_model_relation(page_size, offset) -> List[ModelRelationMeta]:
    return get_ai_flow_client().list_model_relation(page_size, offset)


def delete_model_relation_by_id(model_id) -> Status:
    return get_ai_flow_client().delete_model_relation_by_id(model_id)


def delete_model_relation_by_name(model_name) -> Status:
    return get_ai_flow_client().delete_model_relation_by_name(model_name)


def get_model_by_id(model_id) -> Optional[ModelMeta]:
    return get_ai_flow_client().get_model_by_id(model_id)


def get_model_by_name(model_name) -> Optional[ModelMeta]:
    return get_ai_flow_client().get_model_by_name(model_name)


def register_model(model_name: Text, model_desc: Text = None) -> ModelMeta:
    project_config = current_project_config()
    project_id = int(project_config.get_project_uuid())
    return get_ai_flow_client().register_model(model_name, project_id, model_desc)


def delete_model_by_id(model_id) -> Status:
    return get_ai_flow_client().delete_model_by_id(model_id)


def delete_model_by_name(model_name) -> Status:
    return get_ai_flow_client().delete_model_by_name(model_name)


def get_model_version_relation_by_version(version, model_id) -> Optional[ModelVersionRelationMeta]:
    return get_ai_flow_client().get_model_version_relation_by_version(version, model_id)


def register_model_version_relation(version: Text, model_id: int,
                                    project_snapshot_id: int = None) -> ModelVersionRelationMeta:
    return get_ai_flow_client().register_model_version_relation(version, model_id, project_snapshot_id)


def list_model_version_relation(model_id, page_size, offset) -> List[ModelVersionRelationMeta]:
    return get_ai_flow_client().list_model_version_relation(model_id, page_size, offset)


def delete_model_version_relation_by_version(version, model_id) -> Status:
    return get_ai_flow_client().delete_model_version_relation_by_version(version, model_id)


def get_model_version_by_version(version, model_id) -> Optional[ModelVersionMeta]:
    return get_ai_flow_client().get_model_version_by_version(version, model_id)


def register_model_version(model, model_path, model_type=None, version_desc=None,
                           current_stage=ModelVersionStage.GENERATED) -> ModelVersionMeta:
    workflow_execution_id = None
    if isinstance(model, str):
        model_meta_info = get_ai_flow_client().get_model_by_name(model)
    else:
        model_meta_info = model
    return get_ai_flow_client().register_model_version(model_meta_info, model_path, workflow_execution_id,
                                                       model_type, version_desc, current_stage)


def delete_model_version_by_version(version, model_id) -> Status:
    return get_ai_flow_client().delete_model_version_by_version(version, model_id)


def get_deployed_model_version(model_name) -> ModelVersionMeta:
    return get_ai_flow_client().get_deployed_model_version(model_name)


def get_latest_validated_model_version(model_name) -> ModelVersionMeta:
    return get_ai_flow_client().get_latest_validated_model_version(model_name)


def get_latest_generated_model_version(model_name) -> ModelVersionMeta:
    return get_ai_flow_client().get_latest_generated_model_version(model_name)


def get_project_by_id(project_id) -> Optional[ProjectMeta]:
    return get_ai_flow_client().get_project_by_id(project_id)


def get_project_by_name(project_name) -> Optional[ProjectMeta]:
    return get_ai_flow_client().get_project_by_name(project_name)


def register_project(name, uri: Text = None, properties: Properties = None) -> ProjectMeta:
    return get_ai_flow_client().register_project(name, uri, properties)


def update_project(project_name: Text, uri: Text = None, properties: Properties = None) -> Optional[ProjectMeta]:
    return get_ai_flow_client().update_project(project_name, uri, properties)


def list_projects(page_size, offset) -> Optional[List[ProjectMeta]]:
    return get_ai_flow_client().list_projects(page_size, offset)


def delete_project_by_id(project_id) -> Status:
    return get_ai_flow_client().delete_project_by_id(project_id)


def delete_project_by_name(project_name) -> Status:
    return get_ai_flow_client().delete_project_by_name(project_name)


def register_workflow(name: Text, project_id: int, properties: Properties = None,
                      context_extractor: ContextExtractor = BroadcastAllContextExtractor, graph: Text = None) -> WorkflowMeta:
    return get_ai_flow_client().register_workflow(name=name, project_id=project_id, properties=properties,
                                                  context_extractor=context_extractor, graph=graph)


def get_workflow_by_name(project_name: Text, workflow_name: Text) -> Optional[WorkflowMeta]:
    return get_ai_flow_client().get_workflow_by_name(project_name=project_name, workflow_name=workflow_name)


def get_workflow_by_id(workflow_id: int) -> Optional[WorkflowMeta]:
    return get_ai_flow_client().get_workflow_by_id(workflow_id)


def list_workflows(project_name: Text, page_size: int, offset: int) -> Optional[List[WorkflowMeta]]:
    return get_ai_flow_client().list_workflows(project_name=project_name,
                                               page_size=page_size,
                                               offset=offset)


def delete_workflow_by_name(project_name: Text, workflow_name: Text) -> Status:
    return get_ai_flow_client().delete_workflow_by_name(project_name=project_name,
                                                        workflow_name=workflow_name)


def delete_workflow_by_id(workflow_id: int) -> Status:
    return get_ai_flow_client().delete_workflow_by_id(workflow_id)


def update_workflow(workflow_name: Text, project_name: Text, context_extractor: ContextExtractor,
                    properties: Properties = None, graph: Text = None) -> Optional[WorkflowMeta]:
    return get_ai_flow_client().update_workflow(workflow_name=workflow_name,
                                                project_name=project_name,
                                                context_extractor=context_extractor,
                                                properties=properties,
                                                graph=graph)


def get_artifact_by_id(artifact_id) -> Optional[ArtifactMeta]:
    return get_ai_flow_client().get_artifact_by_id(artifact_id)


def get_artifact_by_name(artifact_name) -> Optional[ArtifactMeta]:
    return get_ai_flow_client().get_artifact_by_name(artifact_name)


def register_artifact(name: Text, artifact_type: Text = None, description: Text = None,
                      uri: Text = None,
                      properties: Properties = None) -> ArtifactMeta:
    return get_ai_flow_client().register_artifact(name, artifact_type, description, uri, properties)


def update_artifact(artifact_name: Text, artifact_type: Text = None,
                    description: Text = None, uri: Text = None,
                    properties: Properties = None) -> Optional[ArtifactMeta]:
    return get_ai_flow_client().update_artifact(artifact_name, artifact_type, description, uri, properties)


def list_artifacts(page_size, offset) -> Optional[List[ArtifactMeta]]:
    return get_ai_flow_client().list_artifacts(page_size, offset)


def delete_artifact_by_id(artifact_id) -> Status:
    return get_ai_flow_client().delete_artifact_by_id(artifact_id)


def delete_artifact_by_name(artifact_name) -> Status:
    return get_ai_flow_client().delete_artifact_by_name(artifact_name)


def create_registered_model(model_name: Text, model_desc: Text = None) -> Optional[RegisteredModelDetail]:
    return get_ai_flow_client().create_registered_model(model_name, model_desc)


def update_registered_model(model_name: Text, new_name: Text = None,
                            model_desc: Text = None) -> Optional[RegisteredModelDetail]:
    return get_ai_flow_client().update_registered_model(model_name, new_name, model_desc)


def delete_registered_model(model_name) -> RegisteredModelDetail:
    return get_ai_flow_client().delete_registered_model(model_name)


def list_registered_models() -> List[RegisteredModelDetail]:
    return get_ai_flow_client().list_registered_models()


def get_registered_model_detail(model_name) -> Optional[RegisteredModelDetail]:
    return get_ai_flow_client().get_registered_model_detail(model_name)


def create_model_version(model_name, model_path, model_type=None,
                         version_desc=None, current_stage=ModelVersionStage.GENERATED) -> Optional[ModelVersionDetail]:
    return get_ai_flow_client().create_model_version(model_name, model_path, model_type, version_desc,
                                                     current_stage)


def update_model_version(model_name, model_version, model_path=None, model_type=None,
                         version_desc=None, current_stage=None) -> Optional[ModelVersionDetail]:
    return get_ai_flow_client().update_model_version(model_name, model_version, model_path,
                                                     model_type, version_desc, current_stage)


def delete_model_version(model_name, model_version) -> Status:
    return get_ai_flow_client().delete_model_version_by_version(model_name, model_version)


def get_model_version_detail(model_name, model_version) -> Optional[ModelVersionDetail]:
    return get_ai_flow_client().get_model_version_detail(model_name, model_version)


def register_metric_meta(metric_name: Text,
                         metric_type: MetricType,
                         project_name: Text,
                         metric_desc: Optional[Text] = None,
                         dataset_name: Optional[Text] = None,
                         model_name: Optional[Text] = None,
                         job_name: Optional[Text] = None,
                         start_time: int = None,
                         end_time: int = None,
                         uri: Optional[Text] = None,
                         tags: Optional[Text] = None,
                         properties: Properties = None
                         ) -> Tuple[int, Text, Optional[MetricMeta]]:
    return get_ai_flow_client().register_metric_meta(metric_name, metric_type, project_name, metric_desc, dataset_name,
                                                     model_name, job_name, start_time, end_time, uri, tags, properties)


def update_metric_meta(metric_name: Text,
                       project_name: Optional[Text] = None,
                       metric_desc: Optional[Text] = None,
                       dataset_name: Optional[Text] = None,
                       model_name: Optional[Text] = None,
                       job_name: Optional[Text] = None,
                       start_time: int = None,
                       end_time: int = None,
                       uri: Optional[Text] = None,
                       tags: Optional[Text] = None,
                       properties: Properties = None
                       ) -> Tuple[int, Text, Optional[MetricMeta]]:
    return get_ai_flow_client().update_metric_meta(metric_name, project_name, metric_desc, dataset_name,
                                                   model_name, job_name, start_time, end_time, uri, tags, properties)


def delete_metric_meta(metric_name: Text) -> bool:
    return get_ai_flow_client().delete_metric_meta(metric_name)


def get_metric_meta(metric_name: Text) -> Tuple[int, Text, Union[None, MetricMeta]]:
    return get_ai_flow_client().get_metric_meta(metric_name)


def list_dataset_metric_metas(dataset_name: Text, project_name: Optional[Text] = None) -> Tuple[
     int, Text, Union[None, MetricMeta, List[MetricMeta]]]:
    return get_ai_flow_client().list_dataset_metric_metas(dataset_name, project_name)


def list_model_metric_metas(model_name: Text, project_name: Optional[Text] = None) -> Tuple[
        int, Text, Union[None, MetricMeta, List[MetricMeta]]]:
    return get_ai_flow_client().list_model_metric_metas(model_name, project_name)


def register_metric_summary(metric_name: Text,
                            metric_key: Text,
                            metric_value: Text,
                            metric_timestamp: int,
                            model_version: Optional[Text] = None,
                            job_execution_id: Optional[Text] = None
                            ) -> Tuple[int, Text, Optional[MetricSummary]]:
    return get_ai_flow_client().register_metric_summary(metric_name, metric_key, metric_value, metric_timestamp,
                                                        model_version, job_execution_id)


def update_metric_summary(uuid: int,
                          metric_name: Optional[Text] = None,
                          metric_key: Optional[Text] = None,
                          metric_value: Optional[Text] = None,
                          metric_timestamp: int = None,
                          model_version: Optional[Text] = None,
                          job_execution_id: Optional[Text] = None
                          ) -> Tuple[int, Text, Optional[MetricSummary]]:
    return get_ai_flow_client().update_metric_summary(uuid, metric_name, metric_key, metric_value, metric_timestamp,
                                                      model_version, job_execution_id)


def delete_metric_summary(uuid: int) -> bool:
    return get_ai_flow_client().delete_metric_summary(uuid)


def get_metric_summary(uuid: int) -> Tuple[int, Text, Union[None, MetricSummary]]:
    return get_ai_flow_client().get_metric_summary(uuid)


def list_metric_summaries(metric_name: Optional[Text] = None, metric_key: Optional[Text] = None,
                          model_version: Optional[Text] = None, start_time: int = None, end_time=None) -> Tuple[
        int, Text, Union[None, MetricSummary, List[MetricSummary]]]:
    return get_ai_flow_client().list_metric_summaries(metric_name, metric_key, model_version, start_time, end_time)
