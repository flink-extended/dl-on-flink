/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package org.aiflow.client.common;

import org.aiflow.proto.Message;

public enum ReturnCode {

    SUCCESS(Message.ReturnCode.SUCCESS),
    INTERNAL_ERROR(Message.ReturnCode.INTERNAL_ERROR),
    TEMPORARILY_UNAVAILABLE(Message.ReturnCode.TEMPORARILY_UNAVAILABLE),
    IO_ERROR(Message.ReturnCode.IO_ERROR),
    BAD_REQUEST(Message.ReturnCode.BAD_REQUEST),
    INVALID_PARAMETER_VALUE(Message.ReturnCode.INVALID_PARAMETER_VALUE),
    ENDPOINT_NOT_FOUND(Message.ReturnCode.ENDPOINT_NOT_FOUND),
    MALFORMED_REQUEST(Message.ReturnCode.MALFORMED_REQUEST),
    INVALID_STATE(Message.ReturnCode.INVALID_STATE),
    PERMISSION_DENIED(Message.ReturnCode.PERMISSION_DENIED),
    FEATURE_DISABLED(Message.ReturnCode.FEATURE_DISABLED),
    CUSTOMER_UNAUTHORIZED(Message.ReturnCode.CUSTOMER_UNAUTHORIZED),
    REQUEST_LIMIT_EXCEEDED(Message.ReturnCode.REQUEST_LIMIT_EXCEEDED),
    RESOURCE_ALREADY_EXISTS(Message.ReturnCode.RESOURCE_ALREADY_EXISTS),
    RESOURCE_DOES_NOT_EXIST(Message.ReturnCode.RESOURCE_DOES_NOT_EXIST),
    QUOTA_EXCEEDED(Message.ReturnCode.QUOTA_EXCEEDED),
    MAX_BLOCK_SIZE_EXCEEDED(Message.ReturnCode.MAX_BLOCK_SIZE_EXCEEDED),
    MAX_READ_SIZE_EXCEEDED(Message.ReturnCode.MAX_READ_SIZE_EXCEEDED),
    UNRECOGNIZED(Message.ReturnCode.UNRECOGNIZED);

    private Message.ReturnCode returnCode;

    ReturnCode(Message.ReturnCode returnCode) {
        this.returnCode = returnCode;
    }

    public Message.ReturnCode getReturnCode() {
        return returnCode;
    }
}