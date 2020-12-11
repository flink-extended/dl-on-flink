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
from ai_flow.model_center.entity._model_repo_entity import _ModelRepoEntity


class RegisteredModel(_ModelRepoEntity):
    """
    AIFlow entity for Registered Model.
    A registered model entity is uniquely identified by its name.
    """

    def __init__(self, model_name):
        """
        Construct a :py:class:`ai_flow.model_center.entity.RegisteredModel`

        :param model_name: Unique name for this registered model within Model Registry.
        """
        super(RegisteredModel, self).__init__()
        self._model_name = model_name

    @property
    def model_name(self):
        """String. Unique name for this registered model within Model Registry."""
        return self._model_name

    # proto mappers
    @classmethod
    def from_proto(cls, proto):
        model_meta = proto.model_meta
        return cls(model_meta.model_name.value if model_meta.HasField("model_name") else None)

    @classmethod
    def from_resp_proto(cls, proto):
        return cls(proto.model_name.value if proto.HasField("model_name") else None)
