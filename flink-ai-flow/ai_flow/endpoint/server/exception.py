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
from ai_flow.protobuf.message_pb2 import INTERNAL_ERROR


class AIFlowException(Exception):
    """
    Generic exception thrown to surface failure information about external-facing operations.
    The error message associated with this exception may be exposed to clients in HTTP responses
    for debugging purposes. If the error text is sensitive, raise a generic `Exception` object
    instead.
    """

    def __init__(self, error_msg, error_code=INTERNAL_ERROR, **kwargs):
        """
        :param message: The message describing the error that occured. This will be included in the
                        exception's serialized JSON representation.
        :param error_code: An appropriate error code for the error that occured; it will be included
                           in the exception's serialized JSON representation. This should be one of
                           the codes listed in the `ai_flow.endpoint.proto.message_pb2` proto.
        :param kwargs: Additional key-value pairs to include in the serialized JSON representation
                       of the AIFlowException.
        """
        try:
            self.error_code = error_code
        except (ValueError, TypeError):
            self.error_code = INTERNAL_ERROR
        self.error_msg = error_msg
        self.json_kwargs = kwargs
        super(AIFlowException, self).__init__(error_msg)
