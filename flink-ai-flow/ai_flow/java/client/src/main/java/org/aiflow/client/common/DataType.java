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

import org.aiflow.client.proto.Message.DataTypeProto;

public enum DataType {
    INT32(DataTypeProto.INT32),
    INT64(DataTypeProto.INT64),
    FLOAT32(DataTypeProto.FLOAT32),
    FLOAT64(DataTypeProto.FLOAT64),
    STRING(DataTypeProto.STRING),
    BYTES(DataTypeProto.BYTES),
    INT32ARRAY(DataTypeProto.INT32ARRAY),
    INT64ARRAY(DataTypeProto.INT64ARRAY),
    FlOAT32ARRAY(DataTypeProto.FlOAT32ARRAY),
    FLOAT64ARRAY(DataTypeProto.FLOAT64ARRAY),
    STRINGARRAY(DataTypeProto.STRINGARRAY),
    BYTESARRAY(DataTypeProto.BYTESARRAY);

    private DataTypeProto dataType;

    DataType(DataTypeProto dataType) {
        this.dataType = dataType;
    }

    public DataTypeProto getDataType() {
        return dataType;
    }
}
