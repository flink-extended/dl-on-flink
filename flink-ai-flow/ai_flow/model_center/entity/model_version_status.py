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
from ai_flow.protobuf.message_pb2 import \
    ModelVersionStatus as ProtoModelVersionStatus


class ModelVersionStatus(object):
    """Enum for status of an :py:class:`ai_flow.model_center.model_repo.entity.ModelVersionDetail`."""
    PENDING_REGISTRATION = ProtoModelVersionStatus.Value('PENDING_REGISTRATION')
    FAILED_REGISTRATION = ProtoModelVersionStatus.Value('FAILED_REGISTRATION')
    READY = ProtoModelVersionStatus.Value('READY')
    PENDING_DELETION = ProtoModelVersionStatus.Value('PENDING_DELETION')
    FAILED_DELETION = ProtoModelVersionStatus.Value('FAILED_DELETION')

    _STRING_TO_STATUS = {k: ProtoModelVersionStatus.Value(k)
                         for k in ProtoModelVersionStatus.keys()}
    _STATUS_TO_STRING = {value: key for key, value in _STRING_TO_STATUS.items()}

    @staticmethod
    def from_string(status_str):
        if status_str not in ModelVersionStatus._STRING_TO_STATUS:
            raise Exception(
                "Could not get model version status corresponding to string %s. Valid status "
                "strings: %s" % (status_str, list(ModelVersionStatus._STRING_TO_STATUS.keys())))
        return ModelVersionStatus._STRING_TO_STATUS[status_str]

    @staticmethod
    def to_string(status):
        if status not in ModelVersionStatus._STATUS_TO_STRING:
            raise Exception("Could not get string corresponding to model version status %s. Valid "
                            "statuses: %s" % (status,
                                              list(ModelVersionStatus._STATUS_TO_STRING.keys())))
        return ModelVersionStatus._STATUS_TO_STRING[status]

    @staticmethod
    def all_status():
        return list(ModelVersionStatus._STATUS_TO_STRING.keys())
