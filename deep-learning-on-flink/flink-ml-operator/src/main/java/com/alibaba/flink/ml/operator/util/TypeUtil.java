/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.alibaba.flink.ml.operator.util;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.TableSchema;
import org.apache.flink.table.catalog.Column;
import org.apache.flink.table.catalog.ResolvedSchema;
import org.apache.flink.table.runtime.typeutils.InternalTypeInfo;
import org.apache.flink.table.types.AbstractDataType;
import org.apache.flink.table.types.DataType;

import java.util.ArrayList;
import java.util.List;

/**
 * a util function to transformation between RowTypeInfo and TableSchema.
 */
public class TypeUtil {

    private TypeUtil() {
    }

    /**
     * convert RowTypeInfo to TableSchema.
     *
     * @param rowTypeInfo given RowTypeInfo.
     * @return TableSchema.
     */
    public static TableSchema rowTypeInfoToTableSchema(RowTypeInfo rowTypeInfo) {
        return new TableSchema(rowTypeInfo.getFieldNames(), rowTypeInfo.getFieldTypes());
    }

    /**
     * convert TableSchema to RowTypeInfo.
     *
     * @param tableSchema given TableSchema.
     * @return RowTypeInfo.
     */
    public static RowTypeInfo schemaToRowTypeInfo(TableSchema tableSchema) {
        return new RowTypeInfo(tableSchema.getFieldTypes(), tableSchema.getFieldNames());
    }

    /**
     * convert Schema to RowTypeInfo.
     *
     * @param schema The schema to convert.
     * @return RowTypeInfo.
     */
    public static RowTypeInfo schemaToRowTypeInfo(ResolvedSchema schema) {

        List<TypeInformation<?>> types = new ArrayList<>();
        List<String> fieldNames = new ArrayList<>();
        for (Column column : schema.getColumns()) {
            DataType dataType = column.getDataType();
            types.add(InternalTypeInfo.of(dataType.getLogicalType()));
            fieldNames.add(column.getName());
        }

        return new RowTypeInfo(types.toArray(new TypeInformation[0]), fieldNames.toArray(new String[0]));
    }

    public static Schema rowTypeInfoToSchema(RowTypeInfo rowTypeInfo) {
        final TypeInformation<?>[] fieldTypes = rowTypeInfo.getFieldTypes();
        final AbstractDataType<?>[] fieldDataTypes = new AbstractDataType[fieldTypes.length];
        for (int i = 0; i < fieldTypes.length; i++) {
            fieldDataTypes[i] = DataTypes.of(fieldTypes[i]);
        }
        return Schema.newBuilder()
                .fromFields(rowTypeInfo.getFieldNames(), fieldDataTypes)
                .build();
    }
}
