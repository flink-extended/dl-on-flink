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

package org.flinkextended.flink.ml.operator.ops.table;

import org.flinkextended.flink.ml.operator.ops.sink.LogSink;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.apache.flink.table.catalog.ResolvedSchema;
import org.apache.flink.table.connector.ChangelogMode;
import org.apache.flink.table.connector.sink.DynamicTableSink;
import org.apache.flink.table.connector.sink.SinkFunctionProvider;
import org.apache.flink.table.data.RowData;

/**
 * LogSink class flink table sink wrapped function.
 */
public class LogTableStreamSink extends TableDummySinkBase {

    private final RichSinkFunction<RowData> sinkFunction;


    public LogTableStreamSink() {
        sinkFunction = new LogSink<>();
    }

    public LogTableStreamSink(ResolvedSchema schema) {
        this(schema, new LogSink<>());
    }

    public LogTableStreamSink(RichSinkFunction<RowData> sinkFunction) {
        this.sinkFunction = sinkFunction;
    }

    public LogTableStreamSink(ResolvedSchema schema, RichSinkFunction<RowData> sinkFunction) {
        super(schema);
        this.sinkFunction = sinkFunction;
    }

    @Override
    public ChangelogMode getChangelogMode(ChangelogMode requestedMode) {
        return ChangelogMode.all();
    }

    @Override
    public SinkRuntimeProvider getSinkRuntimeProvider(Context context) {
        return SinkFunctionProvider.of(sinkFunction);
    }

    @Override
    public DynamicTableSink copy() {
        return new LogTableStreamSink(this.sinkFunction);
    }

    @Override
    public String asSummaryString() {
        return "LogTableStreamSink";
    }
}
