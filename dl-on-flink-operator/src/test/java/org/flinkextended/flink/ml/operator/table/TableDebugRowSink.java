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

import org.flinkextended.flink.ml.operator.sink.DebugRowSink;

import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.table.connector.ChangelogMode;
import org.apache.flink.table.connector.sink.DynamicTableSink;
import org.apache.flink.table.connector.sink.SinkFunctionProvider;

/** Table sink for unit test. */
public class TableDebugRowSink implements DynamicTableSink {
    private RowTypeInfo typeInfo;

    public TableDebugRowSink(RowTypeInfo typeInfo) {
        this.typeInfo = typeInfo;
    }

    @Override
    public ChangelogMode getChangelogMode(ChangelogMode requestedMode) {
        return ChangelogMode.all();
    }

    @Override
    public SinkRuntimeProvider getSinkRuntimeProvider(Context context) {
        return SinkFunctionProvider.of(new DebugRowSink());
    }

    @Override
    public DynamicTableSink copy() {
        return new TableDebugRowSink(this.typeInfo);
    }

    @Override
    public String asSummaryString() {
        return "DebugRowSink";
    }
}
