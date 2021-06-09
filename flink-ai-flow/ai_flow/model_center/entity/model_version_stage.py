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
from ai_flow.protobuf.message_pb2 import INVALID_PARAMETER_VALUE, \
    ModelVersionStage as ProtoModelVersionStage
from ai_flow.endpoint.server.exception import AIFlowException
from enum import Enum

STAGE_GENERATED = "Generated"
STAGE_VALIDATED = "Validated"
STAGE_DEPLOYED = "Deployed"
STAGE_DEPRECATED = "Deprecated"
STAGE_DELETED = "Deleted"

ALL_STAGES = [STAGE_GENERATED, STAGE_VALIDATED, STAGE_DEPLOYED, STAGE_DEPRECATED, STAGE_DELETED]
DEFAULT_STAGES_FOR_GET_LATEST_VERSIONS = [STAGE_GENERATED, STAGE_VALIDATED, STAGE_DEPLOYED]
_CANONICAL_MAPPING = {stage.lower(): stage for stage in ALL_STAGES}


def get_canonical_stage(stage):
    key = stage.lower()
    if key not in _CANONICAL_MAPPING:
        raise AIFlowException("Invalid Model Version stage {}.".format(stage),
                              INVALID_PARAMETER_VALUE)
    return _CANONICAL_MAPPING[key]


class ModelVersionStage(object):
    """Enum for stage of an :py:class:`ai_flow.model_center.model_repo.entity.ModelVersionDetail`."""
    GENERATED = ProtoModelVersionStage.Value('GENERATED')
    VALIDATED = ProtoModelVersionStage.Value('VALIDATED')
    DEPLOYED = ProtoModelVersionStage.Value('DEPLOYED')
    DEPRECATED = ProtoModelVersionStage.Value('DEPRECATED')
    DELETED = ProtoModelVersionStage.Value('DELETED')

    _STRING_TO_STAGE = {k: ProtoModelVersionStage.Value(k)
                        for k in ProtoModelVersionStage.keys()}
    _STAGE_TO_STRING = {value: key for key, value in _STRING_TO_STAGE.items()}

    @staticmethod
    def from_string(stage_str):
        if stage_str not in ModelVersionStage._STRING_TO_STAGE:
            raise Exception(
                "Could not get model version stage corresponding to string %s. Valid status "
                "strings: %s" % (stage_str, list(ModelVersionStage._STRING_TO_STAGE.keys())))
        return ModelVersionStage._STRING_TO_STAGE[stage_str]

    @staticmethod
    def to_string(status):
        if status not in ModelVersionStage._STAGE_TO_STRING:
            raise Exception("Could not get string corresponding to model version stage %s. Valid "
                            "stages: %s" % (status,
                                            list(ModelVersionStage._STAGE_TO_STRING.keys())))
        return ModelVersionStage._STAGE_TO_STRING[status]


class ModelVersionEventType(str, Enum):
    MODEL_GENERATED = 'MODEL_GENERATED'
    MODEL_VALIDATED = 'MODEL_VALIDATED'
    MODEL_DEPLOYED = 'MODEL_DEPLOYED'
    MODEL_DEPRECATED = 'MODEL_DEPRECATED'
    MODEL_DELETED = 'MODEL_DELETED'


MODEL_VERSION_TO_EVENT_TYPE = {
    ModelVersionStage.GENERATED: ModelVersionEventType.MODEL_GENERATED,
    ModelVersionStage.VALIDATED: ModelVersionEventType.MODEL_VALIDATED,
    ModelVersionStage.DEPLOYED: ModelVersionEventType.MODEL_DEPLOYED,
    ModelVersionStage.DEPRECATED: ModelVersionEventType.MODEL_DEPRECATED,
    ModelVersionStage.DELETED: ModelVersionEventType.MODEL_DELETED
}
