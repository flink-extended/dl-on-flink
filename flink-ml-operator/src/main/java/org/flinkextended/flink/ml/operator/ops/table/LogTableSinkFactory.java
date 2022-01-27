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

import org.flinkextended.flink.ml.operator.ops.table.descriptor.LogTable;
import org.apache.flink.configuration.ConfigOption;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.apache.flink.table.connector.sink.DynamicTableSink;
import org.apache.flink.table.data.RowData;
import org.apache.flink.table.factories.DynamicTableSinkFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Collections;
import java.util.Map;
import java.util.Set;

import static org.flinkextended.flink.ml.operator.ops.table.descriptor.LogTableValidator.CONNECTOR_RICH_SINK_FUNCTION;

public class LogTableSinkFactory implements DynamicTableSinkFactory {

    private static final Logger LOG = LoggerFactory.getLogger(LogTableSinkFactory.class);

    @Override
    public DynamicTableSink createDynamicTableSink(Context context) {
        final Map<String, String> options = context.getCatalogTable().getOptions();
        String serializedRichFunction = null;
        if (options.containsKey(CONNECTOR_RICH_SINK_FUNCTION)) {
            serializedRichFunction = options.get(CONNECTOR_RICH_SINK_FUNCTION);
        }
        if (serializedRichFunction == null) {
            return new LogTableStreamSink(context.getCatalogTable().getResolvedSchema());
        }

        try {
            RichSinkFunction<RowData> richSinkFunction = LogTable.RichSinkFunctionDeserializer.deserialize(serializedRichFunction);
            return new LogTableStreamSink(context.getCatalogTable().getResolvedSchema(), richSinkFunction);
        } catch (Exception e) {
            LOG.error("Fail to create LogTableStreamSink", e);
        }
        return new LogTableStreamSink();
    }

    @Override
    public String factoryIdentifier() {
        return "LogTable";
    }

    @Override
    public Set<ConfigOption<?>> requiredOptions() {
        return Collections.emptySet();
    }

    @Override
    public Set<ConfigOption<?>> optionalOptions() {
        return Collections.emptySet();
    }
}
