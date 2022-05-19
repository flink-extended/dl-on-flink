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

import org.flinkextended.flink.ml.operator.ops.table.descriptor.LogTable;
import org.flinkextended.flink.ml.operator.ops.table.descriptor.LogTableValidator;

import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.catalog.Catalog;
import org.apache.flink.table.catalog.CatalogTable;
import org.apache.flink.table.catalog.Column;
import org.apache.flink.table.catalog.GenericInMemoryCatalog;
import org.apache.flink.table.catalog.ObjectIdentifier;
import org.apache.flink.table.catalog.ResolvedCatalogTable;
import org.apache.flink.table.catalog.ResolvedSchema;
import org.apache.flink.table.connector.sink.DynamicTableSink;
import org.apache.flink.table.connector.sink.SinkFunctionProvider;
import org.apache.flink.table.data.RowData;
import org.apache.flink.table.factories.FactoryUtil;

import org.junit.Test;
import org.mockito.Mockito;

import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import static org.hamcrest.CoreMatchers.instanceOf;
import static org.junit.Assert.assertThat;

/** Unit test for {@link LogTableSinkFactory}. */
public class LogTableSinkFactoryTest {
    @Test
    public void testCreateTableSink() {
        final Catalog catalog = new GenericInMemoryCatalog("default");
        ResolvedSchema schema = ResolvedSchema.of(Column.physical("a", DataTypes.STRING()));

        final CatalogTable table = Mockito.mock(CatalogTable.class);
        Mockito.when(table.getOptions())
                .thenReturn(Collections.singletonMap("connector", "LogTable"));

        final DynamicTableSink tableSink =
                FactoryUtil.createTableSink(
                        catalog,
                        ObjectIdentifier.of("default", "test", "test"),
                        new ResolvedCatalogTable(table, schema),
                        new Configuration(),
                        Thread.currentThread().getContextClassLoader(),
                        true);
        assertThat(tableSink, instanceOf(LogTableStreamSink.class));
    }

    @Test
    public void testCreateTableSinkWithRickSinkFunction() throws IOException {
        final DynamicTableSink.Context context = Mockito.mock(DynamicTableSink.Context.class);

        Map<String, String> map = new HashMap<>();
        map.put("connector", "LogTable");
        final RichSinkFunction<RowData> function = new MySinkFunction();
        map.put(
                LogTableValidator.CONNECTOR_RICH_SINK_FUNCTION,
                LogTable.RichSinkFunctionSerializer.serialize(function));

        final Catalog catalog = new GenericInMemoryCatalog("default");
        ResolvedSchema schema = ResolvedSchema.of(Column.physical("a", DataTypes.STRING()));

        final CatalogTable table = Mockito.mock(CatalogTable.class);
        Mockito.when(table.getOptions()).thenReturn(map);

        final DynamicTableSink tableSink =
                FactoryUtil.createTableSink(
                        catalog,
                        ObjectIdentifier.of("default", "test", "test"),
                        new ResolvedCatalogTable(table, schema),
                        new Configuration(),
                        Thread.currentThread().getContextClassLoader(),
                        true);

        assertThat(tableSink, instanceOf(LogTableStreamSink.class));
        assertThat(
                ((SinkFunctionProvider) tableSink.getSinkRuntimeProvider(context))
                        .createSinkFunction(),
                instanceOf(MySinkFunction.class));
    }

    /** Dummy class for unit test. */
    public static class MySinkFunction extends RichSinkFunction<RowData> {}
}
