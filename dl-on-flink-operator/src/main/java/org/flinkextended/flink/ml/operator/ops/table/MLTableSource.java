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

import org.flinkextended.flink.ml.cluster.ExecutionMode;
import org.flinkextended.flink.ml.cluster.MLConfig;
import org.flinkextended.flink.ml.cluster.role.BaseRole;
import org.flinkextended.flink.ml.operator.ops.source.NodeSource;
import org.flinkextended.flink.ml.operator.util.TypeUtil;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.TableSchema;
import org.apache.flink.table.sources.StreamTableSource;
import org.apache.flink.types.Row;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.Serializable;

/** flink table source function wrap NodeSource class. */
public class MLTableSource implements StreamTableSource<Row>, Serializable {
    private final MLConfig config;
    private final ExecutionMode mode;
    private final BaseRole role;
    private final RowTypeInfo rowType;
    private final int parallelism;

    private static final Logger LOG = LoggerFactory.getLogger(MLTableSource.class);

    public MLTableSource(
            ExecutionMode mode,
            BaseRole role,
            MLConfig config,
            TableSchema outSchema,
            int parallelism) {
        this.mode = mode;
        this.config = config;
        this.role = role;
        this.rowType = TypeUtil.schemaToRowTypeInfo(outSchema);
        this.parallelism = parallelism;
    }

    public MLTableSource(
            ExecutionMode mode, BaseRole role, MLConfig config, TableSchema outSchema) {
        this(mode, role, config, outSchema, -1);
    }

    private MLTableSource(
            ExecutionMode mode,
            BaseRole role,
            MLConfig config,
            RowTypeInfo rowType,
            int parallelism) {
        this.mode = mode;
        this.config = config;
        this.role = role;
        this.rowType = rowType;
        this.parallelism = parallelism;
    }

    @Override
    public TypeInformation<Row> getReturnType() {
        return rowType;
    }

    @Override
    public TableSchema getTableSchema() {
        return TypeUtil.rowTypeInfoToTableSchema(rowType);
    }

    @Override
    public String explainSource() {
        return this.config.getProperties().getOrDefault(MLConstants.FLINK_VERTEX_NAME, role.name());
    }

    @Override
    public DataStream<Row> getDataStream(StreamExecutionEnvironment execEnv) {
        DataStreamSource source =
                execEnv.addSource(NodeSource.createSource(mode, role, config, rowType));
        if (parallelism > 0) {
            source = source.setParallelism(parallelism);
        }
        return (DataStream<Row>) source.name(explainSource());
    }
}
