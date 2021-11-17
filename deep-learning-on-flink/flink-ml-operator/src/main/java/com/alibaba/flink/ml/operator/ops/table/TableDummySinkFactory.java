package com.alibaba.flink.ml.operator.ops.table;

import org.apache.flink.configuration.ConfigOption;
import org.apache.flink.table.catalog.ResolvedSchema;
import org.apache.flink.table.connector.sink.DynamicTableSink;
import org.apache.flink.table.factories.DynamicTableSinkFactory;

import java.util.Collections;
import java.util.Set;

public class TableDummySinkFactory implements DynamicTableSinkFactory {

    @Override
    public DynamicTableSink createDynamicTableSink(Context context) {
        final ResolvedSchema resolvedSchema = context.getCatalogTable().getResolvedSchema();
        return new TableStreamDummySink(resolvedSchema);
    }

    @Override
    public String factoryIdentifier() {
        return "DummyTable";
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
