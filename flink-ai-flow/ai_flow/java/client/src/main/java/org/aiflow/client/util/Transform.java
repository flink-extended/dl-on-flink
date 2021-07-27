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
package org.aiflow.client.util;

import com.google.protobuf.GeneratedMessageV3.Builder;
import com.google.protobuf.Int32Value;
import com.google.protobuf.Int64Value;
import com.google.protobuf.StringValue;
import com.google.protobuf.util.JsonFormat.Parser;
import org.aiflow.client.common.DataType;
import org.aiflow.client.common.Status;
import org.aiflow.client.exception.AIFlowException;
import org.aiflow.proto.Message.DataTypeProto;
import org.aiflow.proto.Message.Response;
import org.aiflow.proto.Message.ReturnCode;
import org.apache.commons.lang3.StringUtils;

import java.util.ArrayList;
import java.util.List;

public class Transform {

    public static StringValue.Builder stringValue(String value) {
        return value == null ? StringValue.newBuilder() : StringValue.newBuilder().setValue(value);
    }

    public static Int32Value.Builder int32Value(Integer value) {
        return value == null ? Int32Value.newBuilder() : Int32Value.newBuilder().setValue(value);
    }

    public static Int64Value.Builder int64Value(Long value) {
        return value == null ? Int64Value.newBuilder() : Int64Value.newBuilder().setValue(value);
    }

    public static List<DataTypeProto> dataTypeList(List<DataType> typeLIst) {
        List<DataTypeProto> dataTypes = new ArrayList<>();
        for (DataType dataType : typeLIst) {
            dataTypes.add(dataType.getDataType());
        }
        return dataTypes;
    }

    public static String metadataDetailResponse(Response response, Parser parser, Builder<?> builder) throws Exception {
        if (ReturnCode.SUCCESS.getNumber() == Integer.parseInt(response.getReturnCode())) {
            parser.merge(response.getData(), builder);
            return response.getData();
        } else if (ReturnCode.RESOURCE_DOES_NOT_EXIST.getNumber() == Integer.parseInt(response.getReturnCode())) {
            return null;
        } else {
            throw new AIFlowException(response.getReturnCode(), response.getReturnMsg());
        }
    }

    public static Status metadataDeleteResponse(Response response) throws Exception {
        if (ReturnCode.SUCCESS.getNumber() == Integer.parseInt(response.getReturnCode())) {
            return Status.OK;
        } else if (ReturnCode.INTERNAL_ERROR.getNumber() == Integer.parseInt(response.getReturnCode())) {
            return Status.ERROR;
        } else {
            throw new AIFlowException(response.getReturnCode(), response.getReturnMsg());
        }
    }

    public static String buildResponse(Response response, Parser parser, Builder<?> builder) throws Exception {
        if (ReturnCode.SUCCESS.getNumber() == Integer.parseInt(response.getReturnCode())) {
            if (!StringUtils.isEmpty(response.getData())) {
                parser.merge(response.getData(), builder);
            }
            return response.getData();
        } else {
            throw new AIFlowException(response.getReturnCode(), response.getReturnMsg());
        }
    }
}