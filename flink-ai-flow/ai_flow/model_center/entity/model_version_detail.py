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
from ai_flow.model_center.entity.model_version import ModelVersion
from ai_flow.model_center.entity.model_version_stage import ModelVersionStage
from ai_flow.model_center.entity.model_version_status import ModelVersionStatus
from ai_flow.protobuf.message_pb2 import ModelVersionMeta
from ai_flow.endpoint.server import stringValue


class ModelVersionDetail(ModelVersion):
    """
    AIFlow entity for Model Version Detailed.
    Provides additional metadata data for model version in addition to information in
    :py:class:`ai_flow.model_center.entity.ModelVersion`.
    """

    def __init__(self, model_name, model_version, model_path=None,
                 model_type=None, version_desc=None,
                 version_status=None, current_stage=None):
        # Constructor is called only from within the system by various backend stores.
        super(ModelVersionDetail, self).__init__(model_name=model_name,
                                                 model_version=model_version)
        self._model_path = model_path
        self._model_type = model_type
        self._version_desc = version_desc
        self._version_status = version_status
        self._current_stage = current_stage

    @property
    def model_path(self):
        """String. Model source path for the model."""
        return self._model_path

    @property
    def model_type(self):
        """String. Model type of the model."""
        return self._model_type

    @property
    def version_desc(self):
        """String. Description of the model version."""
        return self._version_desc

    @property
    def version_status(self):
        """String. Current Model Registry status for this model."""
        return self._version_status

    @property
    def current_stage(self):
        """String. Current stage of this model version."""
        return self._current_stage

    @classmethod
    def _properties(cls):
        # aggregate with base class properties since cls.__dict__ does not do it automatically
        return sorted(cls._get_properties_helper() + ModelVersion._properties())

    # proto mappers
    @classmethod
    def from_proto(cls, proto):
        if proto is None:
            return None
        else:
            return cls(proto.model_name, proto.model_version,
                       proto.model_path.value if proto.HasField("model_path") else None,
                       proto.model_type.value if proto.HasField("model_type") else None,
                       proto.version_desc.value if proto.HasField("version_desc") else None,
                       proto.version_status, proto.current_stage)

    def to_meta_proto(self):
        return ModelVersionMeta(model_name=self.model_name, model_version=self.model_version,
                                model_path=stringValue(self.model_path),
                                model_type=stringValue(self.model_type),
                                version_desc=stringValue(self.version_desc),
                                version_status=ModelVersionStatus.from_string(self.version_status),
                                current_stage=ModelVersionStage.from_string(self.current_stage.upper()))
