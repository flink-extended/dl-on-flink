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

package com.alibaba.flink.ml.lib.tensorflow.table;

import com.alibaba.flink.ml.operator.util.TypeUtil;
import org.apache.flink.table.catalog.ResolvedSchema;
import org.apache.flink.table.connector.ChangelogMode;
import org.apache.flink.table.connector.source.DynamicTableSource;
import org.apache.flink.table.connector.source.ScanTableSource;
import org.apache.flink.table.connector.source.SourceFunctionProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.Serializable;


public class TableDebugRowSource implements ScanTableSource, Serializable {

    private static Logger LOG = LoggerFactory.getLogger(TableDebugRowSource.class);
    private DebugRowSource debugRowSource;
    private ResolvedSchema tableSchema;

    public TableDebugRowSource(ResolvedSchema tableSchema) {
        this(0, tableSchema);
    }

    public TableDebugRowSource(int rank, ResolvedSchema tableSchema) {
        this(rank, false, tableSchema);
    }

    public TableDebugRowSource(int rank, boolean hasString, ResolvedSchema tableSchema) {
        this.debugRowSource = new DebugRowSource(rank, hasString, TypeUtil.schemaToRowTypeInfo(tableSchema));
        this.tableSchema = tableSchema;
    }

    TableDebugRowSource(DebugRowSource debugRowSource, ResolvedSchema tableSchema) {
        this.debugRowSource = debugRowSource;
        this.tableSchema = tableSchema;
    }

    @Override
    public ChangelogMode getChangelogMode() {
        return ChangelogMode.insertOnly();
    }

    @Override
    public ScanRuntimeProvider getScanRuntimeProvider(ScanContext runtimeProviderContext) {
        return SourceFunctionProvider.of(this.debugRowSource, true);
    }

    @Override
    public DynamicTableSource copy() {
        return new TableDebugRowSource(this.debugRowSource, this.tableSchema);
    }

    @Override
    public String asSummaryString() {
        return "debug_source";
    }
}
