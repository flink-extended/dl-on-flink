package org.flinkextended.flink.ml.operator.ops.table;

import org.flinkextended.flink.ml.operator.ops.table.descriptor.LogTable;
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
import org.flinkextended.flink.ml.operator.ops.table.descriptor.LogTableValidator;
import org.junit.Test;
import org.mockito.Mockito;

import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import static org.hamcrest.CoreMatchers.instanceOf;
import static org.junit.Assert.assertThat;

public class LogTableSinkFactoryTest {
    @Test
    public void testCreateTableSink() {
        final Catalog catalog = new GenericInMemoryCatalog("default");
        ResolvedSchema schema =
                ResolvedSchema.of(
                        Column.physical("a", DataTypes.STRING()));

        final CatalogTable table = Mockito.mock(CatalogTable.class);
        Mockito.when(table.getOptions()).thenReturn(Collections.singletonMap("connector", "LogTable"));

        final DynamicTableSink tableSink = FactoryUtil.createTableSink(catalog,
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
        map.put(LogTableValidator.CONNECTOR_RICH_SINK_FUNCTION, LogTable.RichSinkFunctionSerializer.serialize(function));

        final Catalog catalog = new GenericInMemoryCatalog("default");
        ResolvedSchema schema =
                ResolvedSchema.of(
                        Column.physical("a", DataTypes.STRING()));

        final CatalogTable table = Mockito.mock(CatalogTable.class);
        Mockito.when(table.getOptions()).thenReturn(map);

        final DynamicTableSink tableSink = FactoryUtil.createTableSink(catalog,
                ObjectIdentifier.of("default", "test", "test"),
                new ResolvedCatalogTable(table, schema),
                new Configuration(),
                Thread.currentThread().getContextClassLoader(),
                true);


        assertThat(tableSink, instanceOf(LogTableStreamSink.class));
        assertThat(((SinkFunctionProvider) tableSink.getSinkRuntimeProvider(context)).createSinkFunction(),
                instanceOf(MySinkFunction.class));
    }

    public static class MySinkFunction extends RichSinkFunction<RowData> {
    }
}