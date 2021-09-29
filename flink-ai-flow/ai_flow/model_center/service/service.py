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
import json

from ai_flow.endpoint.server.util import catch_exception, _wrap_response
from ai_flow.model_center.entity.model_version import ModelVersion
from ai_flow.model_center.entity.model_version_param import ModelVersionParam
from ai_flow.model_center.entity.model_version_stage import MODEL_VERSION_TO_EVENT_TYPE, ModelVersionEventType, \
    ModelVersionStage
from ai_flow.model_center.entity.registered_model import RegisteredModel
from ai_flow.model_center.entity.registered_model_param import RegisteredModelParam
from ai_flow.protobuf import model_center_service_pb2_grpc
from ai_flow.protobuf.message_pb2 import RegisteredModelMetas
from ai_flow.store.db.db_util import create_db_store
from notification_service.base_notification import BaseEvent, DEFAULT_NAMESPACE
from notification_service.client import NotificationClient


class ModelCenterService(model_center_service_pb2_grpc.ModelCenterServiceServicer):

    def __init__(self, store_uri, notification_uri=None):
        self.model_repo_store = create_db_store(store_uri)
        self._notification_uri = notification_uri
        self._notification_client = None

    @property
    def notification_client(self) -> NotificationClient:
        if self._notification_uri is None:
            return None
        elif self._notification_client is None:
            self._notification_client = NotificationClient(self._notification_uri, default_namespace=DEFAULT_NAMESPACE)
        return self._notification_client

    @catch_exception
    def createRegisteredModel(self, request, context):
        registered_model_param = RegisteredModelParam.from_proto(request)
        registered_model_meta = self.model_repo_store.create_registered_model(registered_model_param.model_name,
                                                                              registered_model_param.model_desc)
        return _wrap_response(registered_model_meta.to_meta_proto())

    @catch_exception
    def updateRegisteredModel(self, request, context):
        model_meta_param = RegisteredModel.from_proto(request)
        registered_model_param = RegisteredModelParam.from_proto(request)
        registered_model_meta = self.model_repo_store.update_registered_model(
            RegisteredModel(model_meta_param.model_name),
            registered_model_param.model_name,
            registered_model_param.model_desc)
        return _wrap_response(None if registered_model_meta is None else registered_model_meta.to_meta_proto())

    @catch_exception
    def deleteRegisteredModel(self, request, context):
        model_meta_param = RegisteredModel.from_proto(request)
        self.model_repo_store.delete_registered_model(RegisteredModel(model_name=model_meta_param.model_name))
        return _wrap_response(request.model_meta)

    @catch_exception
    def listRegisteredModels(self, request, context):
        registered_models = self.model_repo_store.list_registered_models()
        return _wrap_response(RegisteredModelMetas(registered_models=[registered_model.to_meta_proto()
                                                                      for registered_model in registered_models]))

    @catch_exception
    def getRegisteredModelDetail(self, request, context):
        model_meta_param = ModelVersion.from_proto(request)
        registered_model_detail = self.model_repo_store.get_registered_model_detail(
            RegisteredModel(model_name=model_meta_param.model_name))
        return _wrap_response(None if registered_model_detail is None else registered_model_detail.to_detail_proto())

    @catch_exception
    def createModelVersion(self, request, context):
        model_meta_param = ModelVersion.from_proto(request)
        model_version_param = ModelVersionParam.from_proto(request)
        model_version_meta = self.model_repo_store.create_model_version(model_meta_param.model_name,
                                                                        model_version_param.model_path,
                                                                        model_version_param.model_type,
                                                                        model_version_param.version_desc,
                                                                        model_version_param.current_stage)
        event_type = MODEL_VERSION_TO_EVENT_TYPE.get(ModelVersionStage.from_string(model_version_param.current_stage))
        if self.notification_client is not None:
            self.notification_client.send_event(BaseEvent(model_version_meta.model_name,
                                                          json.dumps(model_version_meta.__dict__),
                                                          event_type))
        return _wrap_response(model_version_meta.to_meta_proto())

    @catch_exception
    def updateModelVersion(self, request, context):
        model_meta_param = ModelVersion.from_proto(request)
        model_version_param = ModelVersionParam.from_proto(request)
        model_version_meta = self.model_repo_store.update_model_version(model_meta_param,
                                                                        model_version_param.model_path,
                                                                        model_version_param.model_type,
                                                                        model_version_param.version_desc,
                                                                        model_version_param.current_stage)
        if model_version_param.current_stage is not None:
            event_type = MODEL_VERSION_TO_EVENT_TYPE.get(
                ModelVersionStage.from_string(model_version_param.current_stage))
            if self.notification_client is not None:
                self.notification_client.send_event(BaseEvent(model_version_meta.model_name,
                                                              json.dumps(model_version_meta.__dict__),
                                                              event_type))
        return _wrap_response(None if model_version_meta is None else model_version_meta.to_meta_proto())

    @catch_exception
    def deleteModelVersion(self, request, context):
        model_meta_param = ModelVersion.from_proto(request)
        self.model_repo_store.delete_model_version(model_meta_param)
        if self.notification_client is not None:
            self.notification_client.send_event(BaseEvent(model_meta_param.model_name,
                                                          json.dumps(model_meta_param.__dict__),
                                                          ModelVersionEventType.MODEL_DELETED))
        return _wrap_response(request.model_meta)

    @catch_exception
    def getModelVersionDetail(self, request, context):
        model_meta_param = ModelVersion.from_proto(request)
        model_version_meta = self.model_repo_store.get_model_version_detail(model_meta_param)
        return _wrap_response(None if model_version_meta is None else model_version_meta.to_meta_proto())
