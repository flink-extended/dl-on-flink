/*
 * Copyright 2022 Deep Learning on Flink Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.flinkextended.flink.ml.operator.ops.table;

import org.flinkextended.flink.ml.operator.util.TypeUtil;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.catalog.Column;
import org.apache.flink.table.catalog.ResolvedSchema;
import org.apache.flink.table.connector.sink.DynamicTableSink;
import org.apache.flink.table.runtime.typeutils.InternalTypeInfo;
import org.apache.flink.types.Row;

/** a common flink table sink function. */
public abstract class TableDummySinkBase implements DynamicTableSink {
    private final TypeInformation<Row> outType;
    private String[] columnNames;
    private final TypeInformation[] colTypes;

    protected TableDummySinkBase() {
        this(ResolvedSchema.of(Column.physical("dummy", DataTypes.STRING())));
        //		this(TableSchema.builder().field("dummy", Types.STRING()).build());
    }

    public TableDummySinkBase(ResolvedSchema schema) {
        outType = TypeUtil.schemaToRowTypeInfo(schema);
        columnNames = schema.getColumnNames().toArray(new String[0]);
        colTypes =
                schema.getColumnDataTypes().stream()
                        .map(dataType -> InternalTypeInfo.of(dataType.getLogicalType()))
                        .toArray(TypeInformation[]::new);
    }
}
