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
import ast
from ai_flow.meta.artifact_meta import ArtifactMeta
from ai_flow.meta.dataset_meta import DatasetMeta, DataType, Schema
from ai_flow.meta.job_meta import JobMeta, State
from ai_flow.meta.model_relation_meta import ModelRelationMeta, ModelVersionRelationMeta, \
    create_model_version_relation
from ai_flow.meta.project_meta import ProjectMeta
from ai_flow.meta.workflow_execution_meta import WorkflowExecutionMeta


class ResultToMeta:
    @staticmethod
    def result_to_dataset_meta(dataset_result) -> DatasetMeta:
        properties = dataset_result.properties
        if properties is not None:
            properties = ast.literal_eval(properties)
        name_list = dataset_result.name_list
        if name_list is not None:
            name_list = ast.literal_eval(name_list)
        type_list = dataset_result.type_list
        if type_list is not None:
            type_list = ast.literal_eval(type_list)
            data_type_list = []
            for data_type in type_list:
                data_type_list.append(DataType(data_type))
        else:
            data_type_list = None
        schema = Schema(name_list=name_list, type_list=data_type_list)
        return DatasetMeta(uuid=dataset_result.uuid, name=dataset_result.name,
                           data_format=dataset_result.format,
                           description=dataset_result.description,
                           uri=dataset_result.uri,
                           create_time=dataset_result.create_time,
                           update_time=dataset_result.update_time, schema=schema,
                           properties=properties, catalog_name=dataset_result.catalog_name,
                           catalog_type=dataset_result.catalog_type, catalog_database=dataset_result.catalog_database,
                           catalog_connection_uri=dataset_result.catalog_connection_uri,
                           catalog_table=dataset_result.catalog_table)

    @staticmethod
    def result_to_project_meta(project_result) -> ProjectMeta:
        properties = project_result.properties
        if properties is not None:
            properties = ast.literal_eval(properties)
        return ProjectMeta(uuid=project_result.uuid, name=project_result.name, uri=project_result.uri,
                           properties=properties)

    @staticmethod
    def result_to_job_meta(job_result) -> JobMeta:
        properties = job_result.properties
        if properties is not None:
            properties = ast.literal_eval(properties)
        state = State(job_result.job_state)
        return JobMeta(uuid=job_result.uuid, name=job_result.name, job_id=job_result.job_id, properties=properties,
                       start_time=job_result.start_time, end_time=job_result.end_time,
                       job_state=state, log_uri=job_result.log_uri,
                       workflow_execution_id=job_result.workflow_execution_id, signature=job_result.signature)

    @staticmethod
    def result_to_artifact_meta(artifact_result) -> ArtifactMeta:
        properties = artifact_result.properties
        if properties is not None:
            properties = ast.literal_eval(properties)
        return ArtifactMeta(uuid=artifact_result.uuid, name=artifact_result.name,
                            artifact_type=artifact_result.artifact_type,
                            description=artifact_result.description, uri=artifact_result.uri,
                            create_time=artifact_result.create_time,
                            update_time=artifact_result.update_time, properties=properties)

    @staticmethod
    def result_to_workflow_execution_meta(execution_result) -> WorkflowExecutionMeta:
        properties = execution_result.properties
        if properties is not None:
            properties = ast.literal_eval(properties)
        execution_state = State(execution_result.execution_state)
        return WorkflowExecutionMeta(uuid=execution_result.uuid, name=execution_result.name, properties=properties,
                                     start_time=execution_result.start_time, end_time=execution_result.end_time,
                                     execution_state=execution_state,
                                     log_uri=execution_result.log_uri,
                                     project_id=execution_result.project_id,
                                     workflow_json=execution_result.workflow_json, signature=execution_result.signature
                                     )

    @staticmethod
    def result_to_model_relation_meta(model_result) -> ModelRelationMeta:
        return ModelRelationMeta(uuid=model_result.uuid, name=model_result.name, project_id=model_result.project_id)

    @staticmethod
    def result_to_model_version_relation_meta(model_version_result) -> ModelVersionRelationMeta:
        return create_model_version_relation(version=model_version_result.version,
                                             model_id=model_version_result.model_id,
                                             workflow_execution_id=model_version_result.workflow_execution_id)
