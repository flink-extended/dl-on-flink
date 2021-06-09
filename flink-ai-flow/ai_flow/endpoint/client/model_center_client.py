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
from typing import Optional, List

import grpc

from ai_flow.model_center.entity.model_version import ModelVersion
from ai_flow.model_center.entity.model_version_detail import ModelVersionDetail
from ai_flow.model_center.entity.model_version_stage import ModelVersionStage
from ai_flow.model_center.entity.registered_model import RegisteredModel
from ai_flow.model_center.entity.registered_model_detail import RegisteredModelDetail
from ai_flow.protobuf import model_center_service_pb2_grpc
from ai_flow.protobuf.message_pb2 import ModelMetaParam, RegisteredModelParam, \
    ModelVersionParam, RegisteredModelDetail as ProtoModelDetail, RegisteredModelMeta, RegisteredModelMetas, \
    ModelVersionMeta, ModelType
from ai_flow.protobuf.model_center_service_pb2 import CreateRegisteredModelRequest, \
    UpdateRegisteredModelRequest, DeleteRegisteredModelRequest, ListRegisteredModelsRequest, \
    GetRegisteredModelDetailRequest, CreateModelVersionRequest, UpdateModelVersionRequest, DeleteModelVersionRequest, \
    GetModelVersionDetailRequest
from ai_flow.endpoint.server import stringValue
from ai_flow.endpoint.client.base_client import BaseClient
from ai_flow.endpoint.server.util import _parse_response


class ModelCenterClient(BaseClient):
    def __init__(self, server_uri):
        super(ModelCenterClient, self).__init__(server_uri)
        channel = grpc.insecure_channel(server_uri)
        self.model_center_stub = model_center_service_pb2_grpc.ModelCenterServiceStub(channel)

    def create_registered_model(self, model_name, model_type, model_desc=None) -> Optional[RegisteredModelDetail]:
        """
        Create a new registered model from given type in Model Center.

        :param model_name: Name of registered model. This is expected to be unique in the backend store.
        :param model_type: Type of registered model.
        :param model_desc: (Optional) Description of registered model.

        :return: A single object of :py:class:`ai_flow.model_center.entity.RegisteredModelDetail` created in
        Model Center.
        """
        request = CreateRegisteredModelRequest(
            registered_model=RegisteredModelParam(model_name=stringValue(model_name),
                                                  model_type=ModelType.Value(model_type),
                                                  model_desc=stringValue(model_desc)))
        response = self.model_center_stub.createRegisteredModel(request)
        return RegisteredModelDetail.from_proto(_parse_response(response, RegisteredModelMeta()))

    def update_registered_model(self, model_name, new_name=None, model_type=None,
                                model_desc=None) -> Optional[RegisteredModelDetail]:
        """
        Update metadata for RegisteredModel entity backend. Either ``model_name`` or ``model_type`` or ``model_desc``
        should be non-None. Backend raises exception if a registered model with given name does not exist.

        :param model_name: Name of registered model. This is expected to be unique in the backend store.
        :param new_name: (Optional) New proposed name for the registered model.
        :param model_type: (Optional) Type of registered model.
        :param model_desc: (Optional) Description of registered model.

        :return: A single updated :py:class:`ai_flow.model_center.entity.RegisteredModelDetail` object.
        """
        request = UpdateRegisteredModelRequest(model_meta=ModelMetaParam(model_name=stringValue(model_name)),
                                               registered_model=RegisteredModelParam(model_name=stringValue(new_name),
                                                                                     model_type=ModelType.Value(
                                                                                         model_type),
                                                                                     model_desc=stringValue(
                                                                                         model_desc)))
        response = self.model_center_stub.updateRegisteredModel(request)
        return RegisteredModelDetail.from_proto(_parse_response(response, RegisteredModelMeta()))

    def delete_registered_model(self, model_name) -> RegisteredModelDetail:
        """
        Delete registered model by model name in Model Center backend.

        :param model_name: Name of registered model. This is expected to be unique in the backend store.

        :return: A single :py:class:`ai_flow.entities.model_registry.RegisteredModel` object.
        """
        request = DeleteRegisteredModelRequest(model_meta=ModelMetaParam(model_name=stringValue(model_name)))
        response = self.model_center_stub.deleteRegisteredModel(request)
        return RegisteredModel.from_resp_proto(_parse_response(response, ModelMetaParam()))

    def list_registered_models(self) -> List[RegisteredModelDetail]:
        """
        List of all registered models in Model Center backend.

        :return: List of :py:class:`ai_flow.model_center.entity.RegisteredModel` objects.
        """
        request = ListRegisteredModelsRequest()
        response = self.model_center_stub.listRegisteredModels(request)
        registered_model_details = []
        for registered_model_detail in _parse_response(response, RegisteredModelMetas()).registered_models:
            registered_model_details.append(RegisteredModelDetail.from_proto(registered_model_detail))
        return registered_model_details

    def get_registered_model_detail(self, model_name) -> Optional[RegisteredModelDetail]:
        """
        Get registered model detail filter by model name for Model Center.

        :param model_name: Name of registered model. This is expected to be unique in the backend store.

        :return: A single :py:class:`ai_flow.entities.model_registry.RegisteredModelDetail` object.
        """
        request = GetRegisteredModelDetailRequest(model_meta=ModelMetaParam(model_name=stringValue(model_name)))
        response = self.model_center_stub.getRegisteredModelDetail(request)
        return RegisteredModelDetail.from_detail_proto(_parse_response(response, ProtoModelDetail()))

    def create_model_version(self, model_name, model_path, model_metric, model_flavor=None, version_desc=None,
                             current_stage=ModelVersionStage.GENERATED) -> Optional[ModelVersionDetail]:
        """
        Create a new model version from given source and metric in Model Center.

        :param model_name: Name of registered model. This is expected to be unique in the backend store.
        :param model_path: Source path where the AIFlow model is stored.
        :param model_metric: Metric address from AIFlow metric server of registered model.
        :param model_flavor: (Optional) Flavor feature of AIFlow registered model option.
        :param version_desc: (Optional) Description of registered model version.
        :param current_stage: (Optional) Stage of registered model version.

        :return: A single object of :py:class:`ai_flow.model_center.entity.ModelVersionDetail` created in
        model repository.
        """
        request = CreateModelVersionRequest(model_meta=ModelMetaParam(model_name=stringValue(model_name)),
                                            model_version=ModelVersionParam(model_path=stringValue(model_path),
                                                                            model_metric=stringValue(model_metric),
                                                                            model_flavor=stringValue(model_flavor),
                                                                            version_desc=stringValue(version_desc),
                                                                            current_stage=current_stage))
        response = self.model_center_stub.createModelVersion(request)
        return ModelVersionDetail.from_proto(_parse_response(response, ModelVersionMeta()))

    def update_model_version(self, model_name, model_version, model_path=None, model_metric=None, model_flavor=None,
                             version_desc=None, current_stage=None) -> Optional[ModelVersionDetail]:
        """
        Update metadata for ModelVersion entity and metadata associated with a model version in backend.
        Either ``model_path`` or ``model_metric`` or ``model_flavor`` or ``version_desc`` should be non-None.
        Backend raises exception if a registered model with given name does not exist.

        :param model_name: Name of registered model. This is expected to be unique in the backend store.
        :param model_version: User-defined version of registered model.
        :param model_path: (Optional) Source path where the AIFlow model is stored.
        :param model_metric: (Optional) Metric address from AIFlow metric server of registered model.
        :param model_flavor: (Optional) Flavor feature of AIFlow registered model option.
        :param version_desc: (Optional) Description of registered model version.
        :param current_stage: (Optional) Current stage of registered model version.

        :return: A single updated :py:class:`ai_flow.model_center.entity.ModelVersionDetail` object.
        """
        request = UpdateModelVersionRequest(
            model_meta=ModelMetaParam(model_name=stringValue(model_name), model_version=stringValue(model_version)),
            model_version=ModelVersionParam(model_path=stringValue(model_path),
                                            model_metric=stringValue(model_metric),
                                            model_flavor=stringValue(model_flavor),
                                            version_desc=stringValue(version_desc),
                                            current_stage=current_stage))
        response = self.model_center_stub.updateModelVersion(request)
        return ModelVersionDetail.from_proto(_parse_response(response, ModelVersionMeta()))

    def delete_model_version(self, model_name, model_version) -> ModelVersion:
        """
        Delete model version by model name and version in Model Center backend.

        :param model_name: Name of registered model. This is expected to be unique in the backend store.
        :param model_version: User-defined version of registered model.

        :return: A single :py:class:`ai_flow.entities.model_registry.ModelVersion` object.
        """
        request = DeleteModelVersionRequest(model_meta=ModelMetaParam(model_name=stringValue(model_name),
                                                                      model_version=stringValue(model_version)))
        response = self.model_center_stub.deleteModelVersion(request)
        return ModelVersion.from_resp_proto(_parse_response(response, ModelMetaParam()))

    def get_model_version_detail(self, model_name, model_version) -> Optional[ModelVersionDetail]:
        """
        Get model version detail filter by model name and model version for Model Center.

        :param model_name: Name of registered model. This is expected to be unique in the backend store.
        :param model_version: User-defined version of registered model.

        :return: A single :py:class:`ai_flow.entities.model_registry.ModelVersionDetail` object.
        """
        request = GetModelVersionDetailRequest(model_meta=ModelMetaParam(model_name=stringValue(model_name),
                                                                         model_version=stringValue(model_version)))
        response = self.model_center_stub.getModelVersionDetail(request)
        return ModelVersionDetail.from_proto(_parse_response(response, ModelVersionMeta()))
