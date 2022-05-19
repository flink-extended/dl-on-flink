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

package org.flinkextended.flink.ml.operator.table;

import org.flinkextended.flink.ml.operator.util.TypeUtil;

import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.configuration.ConfigOption;
import org.apache.flink.table.connector.sink.DynamicTableSink;
import org.apache.flink.table.connector.source.DynamicTableSource;
import org.apache.flink.table.factories.DynamicTableSinkFactory;
import org.apache.flink.table.factories.DynamicTableSourceFactory;

import java.util.Collections;
import java.util.Set;

/** Factory for {@link TableDebugRowSink} and {@link TableDebugRowSource}. */
public class DebugRowFactory implements DynamicTableSinkFactory, DynamicTableSourceFactory {
    @Override
    public DynamicTableSink createDynamicTableSink(Context context) {
        final RowTypeInfo rowTypeInfo =
                TypeUtil.schemaToRowTypeInfo(context.getCatalogTable().getResolvedSchema());
        return new TableDebugRowSink(rowTypeInfo);
    }

    @Override
    public String factoryIdentifier() {
        return "TableDebug";
    }

    @Override
    public Set<ConfigOption<?>> requiredOptions() {
        return Collections.emptySet();
    }

    @Override
    public Set<ConfigOption<?>> optionalOptions() {
        return Collections.emptySet();
    }

    @Override
    public DynamicTableSource createDynamicTableSource(Context context) {
        return new TableDebugRowSource();
    }
}
