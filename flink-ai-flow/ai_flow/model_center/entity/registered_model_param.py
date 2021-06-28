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


class RegisteredModelParam(_ModelRepoEntity):
    """
    AIFlow entity for Registered Model Parameter.
    """

    def __init__(self, model_name, model_desc):
        self._model_name = model_name
        self._model_desc = model_desc

    @property
    def model_name(self):
        """String. Unique name for this registered model within Model Registry."""
        return self._model_name

    @property
    def model_desc(self):
        """String. Model desc for this registered model within Model Registry."""
        return self._model_desc

    # proto mappers
    @classmethod
    def from_proto(cls, proto):
        registered_model = proto.registered_model
        return cls(registered_model.model_name.value if registered_model.HasField("model_name") else None,
                   registered_model.model_desc.value if registered_model.HasField("model_desc") else None)
