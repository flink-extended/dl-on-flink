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
package org.aiflow.client.entity;

import org.aiflow.client.common.DataType;
import org.aiflow.client.proto.Message.DataTypeProto;
import org.aiflow.client.proto.Message.SchemaProto;

import java.util.ArrayList;
import java.util.List;

public class Schema {

    private List<String> nameList;
    private List<DataType> typeList;

    public Schema() {
    }

    public Schema(List<String> nameList, List<DataType> typeList) {
        this.nameList = nameList;
        this.typeList = typeList;
    }

    public List<String> getNameList() {
        return nameList;
    }

    public void setNameList(List<String> nameList) {
        this.nameList = nameList;
    }

    public List<DataType> getTypeList() {
        return typeList;
    }

    public void setTypeList(List<DataType> typeList) {
        this.typeList = typeList;
    }

    @Override
    public String toString() {
        return "Schema{" +
                "nameList=" + nameList +
                ", typeList=" + typeList +
                '}';
    }

    public static Schema buildSchema(SchemaProto schemaProto) {
        if (schemaProto == null) {
            return null;
        } else {
            List<DataType> typeList = new ArrayList<>();
            for (DataTypeProto dataType : schemaProto.getTypeListList()) {
                typeList.add(DataType.valueOf(dataType.name()));
            }
            return new Schema(schemaProto.getNameListList(), typeList);
        }
    }
}