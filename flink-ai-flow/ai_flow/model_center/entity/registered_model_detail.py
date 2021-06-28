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
from ai_flow.model_center.entity.model_version_detail import ModelVersionDetail
from ai_flow.model_center.entity.registered_model import RegisteredModel
from ai_flow.protobuf.message_pb2 import RegisteredModelDetail as ProtoModelDetail, \
    RegisteredModelMeta
from ai_flow.endpoint.server import stringValue


class RegisteredModelDetail(RegisteredModel):
    """
    AIFlow entity for Registered Model Detail.
    Provides additional metadata data for registered model in addition to information in
    :py:class:`ai_flow.model_center.entity.RegisteredModel`.
    """

    def __init__(self, model_name, model_desc=None, latest_model_version=None):
        # Constructor is called only from within the system by various backend stores.
        super(RegisteredModelDetail, self).__init__(model_name)
        self._model_desc = model_desc
        self._latest_model_version = latest_model_version

    @property
    def model_desc(self):
        """String. Model desc for this registered model within Model Registry."""
        return self._model_desc

    @property
    def latest_model_version(self):
        """Specific :py:class:`ai_flow.model_center.entity.ModelVersionDetail` instances"""
        return self._latest_model_version

    @classmethod
    def _properties(cls):
        # aggregate with base class properties since cls.__dict__ does not do it automatically
        return sorted(cls._get_properties_helper() + RegisteredModel._properties())

    # proto mappers
    @classmethod
    def from_proto(cls, proto):
        if proto is None:
            return None
        else:
            return cls(proto.model_name,
                       proto.model_desc.value if proto.HasField("model_desc") else None)

    @classmethod
    def from_detail_proto(cls, proto):
        if proto is None:
            return None
        else:
            registered_model = proto.registered_model
            latest_model_version = proto.latest_model_version
            return cls(registered_model.model_name,
                       registered_model.model_desc.value if registered_model.HasField("model_desc") else None,
                       ModelVersionDetail.from_proto(latest_model_version))

    def to_meta_proto(self):
        return RegisteredModelMeta(model_name=self.model_name,
                                   model_desc=stringValue(self.model_desc))

    def to_detail_proto(self):
        if self.latest_model_version is None:
            return ProtoModelDetail(
                registered_model=RegisteredModelMeta(model_name=self.model_name,
                                                     model_desc=stringValue(self.model_desc)),
                latest_model_version=None)
        else:
            return ProtoModelDetail(
                registered_model=RegisteredModelMeta(model_name=self.model_name,
                                                     model_desc=stringValue(self.model_desc)),
                latest_model_version=self.latest_model_version.to_meta_proto())
