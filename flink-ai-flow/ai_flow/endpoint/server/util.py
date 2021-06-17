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
from functools import wraps

from google.protobuf.json_format import MessageToJson, Parse

from ai_flow.common.status import Status
from ai_flow.meta.artifact_meta import ArtifactMeta
from ai_flow.meta.dataset_meta import DataType, Schema, DatasetMeta
from ai_flow.meta.job_meta import State, JobMeta
from ai_flow.meta.model_meta import ModelMeta, ModelVersionMeta
from ai_flow.meta.model_relation_meta import ModelRelationMeta, ModelVersionRelationMeta
from ai_flow.meta.project_meta import ProjectMeta
from ai_flow.meta.workflow_execution_meta import WorkflowExecutionMeta
from ai_flow.metadata_store.utils.MetaToProto import MetaToProto
from ai_flow.metadata_store.utils.ProtoToMeta import ProtoToMeta
from ai_flow.protobuf.message_pb2 import Response, SUCCESS, ReturnCode, RESOURCE_DOES_NOT_EXIST, \
    DatasetProto, ModelProto, ModelVersionProto, WorkflowExecutionProto, JobProto, ProjectProto, INTERNAL_ERROR, \
    DataTypeProto, StateProto, ArtifactProto
from ai_flow.protobuf.metadata_service_pb2 import DatasetListProto, WorkFlowExecutionListProto, \
    JobListProto, ProjectListProto, ModelVersionRelationListProto, ModelRelationListProto, ModelVersionListProto, \
    ArtifactListProto
from ai_flow.endpoint.server.exception import AIFlowException
from ai_flow.store.sqlalchemy_store import UPDATE_FAIL


def catch_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AIFlowException as e:
            return Response(return_code=str(e.error_code), return_msg=e.error_msg)

    return wrapper


def _wrap_response(response_message):
    if response_message is None:
        return Response(return_code=str(SUCCESS), return_msg=ReturnCode.Name(SUCCESS).lower())
    else:
        return Response(return_code=str(SUCCESS), return_msg=ReturnCode.Name(SUCCESS).lower(),
                        data=MessageToJson(response_message, preserving_proto_field_name=True))


def _parse_response(response, message):
    if response.return_code == str(SUCCESS):
        if response.data == '':
            return None
        else:
            return Parse(response.data, message, ignore_unknown_fields=False)
    else:
        raise AIFlowException(error_code=response.return_code, error_msg=response.return_msg)


def _unwrap_dataset_response(response):
    if response.return_code == str(SUCCESS):
        return ProtoToMeta.proto_to_dataset_meta(Parse(response.data, DatasetProto()))
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_dataset_list_response(response):
    if response.return_code == str(SUCCESS):
        dataset_proto_list = Parse(response.data, DatasetListProto())
        return ProtoToMeta.proto_to_dataset_meta_list(dataset_proto_list.datasets)
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_model_relation_response(response):
    if response.return_code == str(SUCCESS):
        return ProtoToMeta.proto_to_model_relation_meta(Parse(response.data, ModelProto()))
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_model_relation_list_response(response):
    if response.return_code == str(SUCCESS):
        model_proto_list = Parse(response.data, ModelRelationListProto())
        return ProtoToMeta.proto_to_model_relation_meta_list(model_proto_list.model_relations)
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_model_version_relation_response(response):
    if response.return_code == str(SUCCESS):
        return ProtoToMeta.proto_to_model_version_relation_meta(Parse(response.data, ModelVersionProto()))
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_model_version_relation_list_response(response):
    if response.return_code == str(SUCCESS):
        model_version_proto_list = Parse(response.data, ModelVersionRelationListProto())
        return ProtoToMeta.proto_to_model_version_relation_meta_list(model_version_proto_list.model_versions)
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_model_response(response):
    if response.return_code == str(SUCCESS):
        return ProtoToMeta.proto_to_model_meta(Parse(response.data, ModelProto()))
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_model_version_response(response):
    if response.return_code == str(SUCCESS):
        return ProtoToMeta.proto_to_model_version_meta(Parse(response.data, ModelVersionProto()))
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_model_version_list_response(response):
    if response.return_code == str(SUCCESS):
        model_version_proto_list = Parse(response.data, ModelVersionListProto())
        return ProtoToMeta.proto_to_model_version_meta_list(model_version_proto_list.model_versions)
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_workflow_execution_response(response):
    if response.return_code == str(SUCCESS):
        return ProtoToMeta.proto_to_execution_meta(Parse(response.data, WorkflowExecutionProto()))
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_workflow_execution_list_response(response):
    if response.return_code == str(SUCCESS):
        workflow_execution_proto_list = Parse(response.data, WorkFlowExecutionListProto())
        return ProtoToMeta.proto_to_execution_meta_list(workflow_execution_proto_list.workflow_executions)
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_job_response(response):
    if response.return_code == str(SUCCESS):
        return ProtoToMeta.proto_to_job_meta(Parse(response.data, JobProto()))
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_job_list_response(response):
    if response.return_code == str(SUCCESS):
        job_proto_list = Parse(response.data, JobListProto())
        return ProtoToMeta.proto_to_job_meta_list(job_proto_list.jobs)
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_project_response(response):
    if response.return_code == str(SUCCESS):
        return ProtoToMeta.proto_to_project_meta(Parse(response.data, ProjectProto()))
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_project_list_response(response):
    if response.return_code == str(SUCCESS):
        project_proto_list = Parse(response.data, ProjectListProto())
        return ProtoToMeta.proto_to_project_meta_list(project_proto_list.projects)
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_artifact_response(response):
    if response.return_code == str(SUCCESS):
        return ProtoToMeta.proto_to_artifact_meta(Parse(response.data, ArtifactProto()))
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_artifact_list_response(response):
    if response.return_code == str(SUCCESS):
        artifact_proto_list = Parse(response.data, ArtifactListProto())
        return ProtoToMeta.proto_to_artifact_meta_list(artifact_proto_list.artifacts)
    elif response.return_code == str(RESOURCE_DOES_NOT_EXIST):
        return None
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_delete_response(response):
    if response.return_code == str(SUCCESS):
        return Status.OK
    elif response.return_code == str(INTERNAL_ERROR):
        return Status.ERROR
    else:
        raise AIFlowException(response.return_msg)


def _unwrap_update_response(response):
    if response.return_code == str(SUCCESS):
        return int(response.data)
    elif response.return_code == str(INTERNAL_ERROR):
        return Status.ERROR
    else:
        raise AIFlowException(response.return_msg)


def transform_dataset_type_list_to_proto(type_list):
    data_type_list = []
    if type_list is not None:
        for data_type in type_list:
            data_type_list.append(DataTypeProto.Value(data_type))
    else:
        data_type_list = None
    return data_type_list


def _wrap_meta_response(data):
    if data is not None:
        return Response(return_code=str(SUCCESS), return_msg=ReturnCode.Name(SUCCESS).lower(),
                        data=MessageToJson(data, preserving_proto_field_name=True))
    else:
        return Response(return_code=str(RESOURCE_DOES_NOT_EXIST),
                        return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                        data=None)


def _wrap_delete_response(status):
    if status == Status.OK:
        return Response(return_code=str(SUCCESS), return_msg=ReturnCode.Name(SUCCESS).lower(), data=None)
    else:
        return Response(return_code=str(INTERNAL_ERROR), return_msg=ReturnCode.Name(INTERNAL_ERROR).lower(),
                        data=None)


def _wrap_update_response(uuid):
    if uuid != UPDATE_FAIL:
        return Response(return_code=str(SUCCESS), return_msg=ReturnCode.Name(SUCCESS).lower(), data=str(uuid))
    else:
        return Response(return_code=str(INTERNAL_ERROR), return_msg=ReturnCode.Name(INTERNAL_ERROR).lower(),
                        data=None)


def _warp_dataset_list_response(dataset_meta_list):
    if dataset_meta_list is not None:
        dataset_proto_list = MetaToProto.dataset_meta_list_to_proto(dataset_meta_list)
        return Response(return_code=str(SUCCESS), return_msg=ReturnCode.Name(SUCCESS).lower(),
                        data=MessageToJson(DatasetListProto(datasets=dataset_proto_list),
                                           preserving_proto_field_name=True))
    else:
        return Response(return_code=str(RESOURCE_DOES_NOT_EXIST),
                        return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                        data=None)


def _warp_model_relation_list_response(model_relation_list):
    if model_relation_list is not None:
        model_proto_list = MetaToProto.model_relation_meta_list_to_proto(model_relation_list)
        return Response(return_code=str(SUCCESS), return_msg=ReturnCode.Name(SUCCESS).lower(),
                        data=MessageToJson(ModelRelationListProto(model_relations=model_proto_list),
                                           preserving_proto_field_name=True))
    else:
        return Response(return_code=str(RESOURCE_DOES_NOT_EXIST),
                        return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                        data=None)


def _warp_model_version_relation_list_response(model_version_relation_list):
    if model_version_relation_list is not None:
        model_version_proto_list = MetaToProto.model_version_relation_meta_list_to_proto(model_version_relation_list)
        return Response(return_code=str(SUCCESS), return_msg=ReturnCode.Name(SUCCESS).lower(),
                        data=MessageToJson(ModelVersionRelationListProto(model_versions=model_version_proto_list),
                                           preserving_proto_field_name=True))
    else:
        return Response(return_code=str(RESOURCE_DOES_NOT_EXIST),
                        return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                        data=None)


def _warp_workflow_execution_list_response(workflow_execution_list):
    if workflow_execution_list is not None:
        workflow_execution_proto_list = MetaToProto.workflow_execution_meta_list_to_proto(workflow_execution_list)
        return Response(return_code=str(SUCCESS), return_msg=ReturnCode.Name(SUCCESS).lower(),
                        data=MessageToJson(
                            WorkFlowExecutionListProto(workflow_executions=workflow_execution_proto_list),
                            preserving_proto_field_name=True))
    else:
        return Response(return_code=str(RESOURCE_DOES_NOT_EXIST),
                        return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                        data=None)


def _warp_job_list_response(job_list):
    if job_list is not None:
        job_proto_list = MetaToProto.job_meta_list_to_proto(job_list)
        return Response(return_code=str(SUCCESS), return_msg=ReturnCode.Name(SUCCESS).lower(),
                        data=MessageToJson(JobListProto(jobs=job_proto_list), preserving_proto_field_name=True))
    else:
        return Response(return_code=str(RESOURCE_DOES_NOT_EXIST),
                        return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                        data=None)


def _warp_project_list_response(project_list):
    if project_list is not None:
        project_proto_list = MetaToProto.project_meta_list_to_proto(project_list)
        return Response(return_code=str(SUCCESS), return_msg=ReturnCode.Name(SUCCESS).lower(),
                        data=MessageToJson(ProjectListProto(projects=project_proto_list),
                                           preserving_proto_field_name=True))
    else:
        return Response(return_code=str(RESOURCE_DOES_NOT_EXIST),
                        return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                        data=None)


def _warp_artifact_list_response(artifact_list):
    if artifact_list is not None:
        artifact_proto_list = MetaToProto.artifact_meta_list_to_proto(artifact_list)
        return Response(return_code=str(SUCCESS), return_msg=ReturnCode.Name(SUCCESS).lower(),
                        data=MessageToJson(ArtifactListProto(artifacts=artifact_proto_list),
                                           preserving_proto_field_name=True))
    else:
        return Response(return_code=str(RESOURCE_DOES_NOT_EXIST),
                        return_msg=ReturnCode.Name(RESOURCE_DOES_NOT_EXIST).lower(),
                        data=None)


def transform_dataset_meta(dataset_proto):
    properties = dataset_proto.properties
    if properties == {}:
        properties = None
    name_list = dataset_proto.schema.name_list
    type_list = dataset_proto.schema.type_list
    if not name_list:
        name_list = None
    if not type_list:
        data_type_list = None
    else:
        data_type_list = []
        for c in type_list:
            data_type_list.append(DataType(DataTypeProto.Name(c)))
    schema = Schema(name_list=name_list, type_list=data_type_list)
    return DatasetMeta(name=dataset_proto.name,
                       data_format=dataset_proto.data_format.value if dataset_proto.HasField('data_format') else None,
                       description=dataset_proto.description.value if dataset_proto.HasField('description') else None,
                       uri=dataset_proto.uri.value if dataset_proto.HasField('uri') else None,
                       create_time=dataset_proto.create_time.value if dataset_proto.HasField('create_time') else None,
                       update_time=dataset_proto.update_time.value if dataset_proto.HasField('update_time') else None,
                       properties=properties,
                       schema=schema,
                       catalog_name=dataset_proto.catalog_name.value if dataset_proto.HasField(
                           'catalog_name') else None,
                       catalog_type=dataset_proto.catalog_type.value if dataset_proto.HasField(
                           'catalog_type') else None,
                       catalog_database=dataset_proto.catalog_database.value if dataset_proto.HasField(
                           'catalog_database') else None,
                       catalog_connection_uri=dataset_proto.catalog_connection_uri.value \
                           if dataset_proto.HasField('catalog_connection_uri') else None,
                       catalog_table=dataset_proto.catalog_table.value if dataset_proto.HasField(
                           'catalog_table') else None)


def transform_project_meta(project_proto):
    properties = project_proto.properties
    if properties == {}:
        properties = None
    return ProjectMeta(
        name=project_proto.name,
        properties=properties,
        uri=project_proto.uri.value if project_proto.HasField('uri') else None)


def transform_artifact_meta(artifact_proto) -> ArtifactMeta:
    properties = artifact_proto.properties
    if properties == {}:
        properties = None
    return ArtifactMeta(
        name=artifact_proto.name,
        properties=properties,
        artifact_type=artifact_proto.artifact_type.value if artifact_proto.HasField('artifact_type') else None,
        description=artifact_proto.description.value if artifact_proto.HasField('description') else None,
        uri=artifact_proto.uri.value if artifact_proto.HasField('uri') else None,
        create_time=artifact_proto.create_time.value if artifact_proto.HasField('create_time') else None,
        update_time=artifact_proto.update_time.value if artifact_proto.HasField('update_time') else None)


def transform_workflow_execution_meta(workflow_execution_proto):
    execution_state = State(StateProto.Name(workflow_execution_proto.execution_state))
    properties = workflow_execution_proto.properties
    if properties == {}:
        properties = None
    return WorkflowExecutionMeta(name=workflow_execution_proto.name,
                                 execution_state=execution_state,
                                 properties=properties,
                                 project_id=workflow_execution_proto.project_id.value if workflow_execution_proto.HasField(
                                     'project_id') else None,
                                 start_time=workflow_execution_proto.start_time.value if workflow_execution_proto.HasField(
                                     'start_time') else None,
                                 end_time=workflow_execution_proto.end_time.value if workflow_execution_proto.HasField(
                                     'end_time') else None,
                                 log_uri=workflow_execution_proto.log_uri.value if workflow_execution_proto.HasField(
                                     'log_uri') else None,
                                 workflow_json=workflow_execution_proto.workflow_json.value if workflow_execution_proto.HasField(
                                     'workflow_json') else None,
                                 signature=workflow_execution_proto.signature.value if workflow_execution_proto.HasField(
                                     'signature') else None)


def transform_job_meta(job_proto):
    job_state = State(StateProto.Name(job_proto.job_state))
    properties = job_proto.properties
    if properties == {}:
        properties = None
    return JobMeta(name=job_proto.name,
                   job_state=job_state,
                   properties=properties,
                   workflow_execution_id=job_proto.workflow_execution_id.value if job_proto.HasField(
                       'workflow_execution_id') else None,
                   job_id=job_proto.job_id.value if job_proto.HasField('job_id') else None,
                   start_time=job_proto.start_time.value if job_proto.HasField(
                       'start_time') else None,
                   end_time=job_proto.end_time.value if job_proto.HasField(
                       'end_time') else None,
                   log_uri=job_proto.log_uri.value if job_proto.HasField(
                       'log_uri') else None,
                   signature=job_proto.signature.value if job_proto.HasField(
                       'signature') else None)


def transform_model_relation_meta(model_relation_proto):
    return ModelRelationMeta(name=model_relation_proto.name,
                             project_id=model_relation_proto.project_id.value if model_relation_proto.HasField(
                                 'project_id') else None)


def transform_model_version_relation_meta(model_version_relation_proto):
    return ModelVersionRelationMeta(
        version=model_version_relation_proto.version.value
        if model_version_relation_proto.HasField('version') else None,
        model_id=model_version_relation_proto.model_id.value
        if model_version_relation_proto.HasField('model_id') else None,
        workflow_execution_id=model_version_relation_proto.workflow_execution_id.value
        if model_version_relation_proto.HasField('workflow_execution_id') else None)


def transform_model_meta(model_proto):
    return ModelMeta(name=model_proto.name, model_type=model_proto.model_type,
                     model_desc=model_proto.model_desc.value if model_proto.HasField('model_desc') else None,
                     project_id=model_proto.project_id.value if model_proto.HasField('project_id') else None)


def transform_model_version_meta(model_version_proto):
    return ModelVersionMeta(version=model_version_proto.version.value if model_version_proto.HasField(
        'version') else None,
                            model_id=model_version_proto.model_id.value if model_version_proto.HasField(
                                'model_id') else None,
                            workflow_execution_id=model_version_proto.workflow_execution_id.value
                            if model_version_proto.HasField('workflow_execution_id') else None,
                            model_path=model_version_proto.model_path.value if model_version_proto.HasField(
                                "model_path") else None,
                            model_metric=model_version_proto.model_metric.value if model_version_proto.HasField(
                                "model_metric") else None,
                            model_flavor=model_version_proto.model_flavor.value if model_version_proto.HasField(
                                "model_flavor") else None,
                            version_desc=model_version_proto.version_desc.value if model_version_proto.HasField(
                                "version_desc") else None)
