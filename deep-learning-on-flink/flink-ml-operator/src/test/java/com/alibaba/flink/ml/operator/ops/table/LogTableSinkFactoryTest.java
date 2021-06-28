package com.alibaba.flink.ml.operator.ops.table;

import com.alibaba.flink.ml.operator.ops.table.descriptor.LogTable;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.apache.flink.table.api.TableSchema;
import org.apache.flink.table.catalog.CatalogTable;
import org.apache.flink.table.factories.TableFactoryUtil;
import org.apache.flink.table.factories.TableSinkFactory.Context;
import org.apache.flink.table.sinks.TableSink;
import org.apache.flink.types.Row;
import org.junit.Test;
import org.mockito.Mockito;

import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import static com.alibaba.flink.ml.operator.ops.table.descriptor.LogTableValidator.CONNECTOR_RICH_SINK_FUNCTION;
import static org.apache.flink.table.descriptors.ConnectorDescriptorValidator.CONNECTOR_TYPE;
import static org.hamcrest.CoreMatchers.instanceOf;
import static org.junit.Assert.assertThat;

public class LogTableSinkFactoryTest {
	@Test
	public void testCreateTableSink() {
		final Context context = Mockito.mock(Context.class);
		final CatalogTable table = Mockito.mock(CatalogTable.class);
		Mockito.when(context.getTable()).thenReturn(table);
		Mockito.when(table.toProperties()).thenReturn(Collections.singletonMap(CONNECTOR_TYPE, "LogTable"));
		Mockito.when(table.getSchema()).thenReturn(TableSchema.builder().build());
		final TableSink<Object> tableSink = TableFactoryUtil.findAndCreateTableSink(context);
		assertThat(tableSink, instanceOf(LogTableStreamSink.class));
	}

	@Test
	public void testCreateTableSinkWithRickSinkFunction() throws IOException {
		final Context context = Mockito.mock(Context.class);
		final CatalogTable table = Mockito.mock(CatalogTable.class);
		Mockito.when(context.getTable()).thenReturn(table);

		Map<String, String> map = new HashMap<>();
		map.put(CONNECTOR_TYPE, "LogTable");
		final RichSinkFunction<Row> function = new MySinkFunction();
		map.put(CONNECTOR_RICH_SINK_FUNCTION, LogTable.RichSinkFunctionSerializer.serialize(function));
		Mockito.when(table.toProperties()).thenReturn(map);
		Mockito.when(table.getSchema()).thenReturn(TableSchema.builder().build());
		final TableSink<Row> tableSink = TableFactoryUtil.findAndCreateTableSink(context);
		assertThat(tableSink, instanceOf(LogTableStreamSink.class));
		assertThat(((LogTableStreamSink)tableSink).getSinkFunction(), instanceOf(MySinkFunction.class));
	}

	public static class MySinkFunction extends RichSinkFunction<Row> {
	}
}