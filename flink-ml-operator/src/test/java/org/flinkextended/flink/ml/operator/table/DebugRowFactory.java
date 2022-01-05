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


public class DebugRowFactory implements DynamicTableSinkFactory, DynamicTableSourceFactory {
    @Override
    public DynamicTableSink createDynamicTableSink(Context context) {
        final RowTypeInfo rowTypeInfo = TypeUtil.schemaToRowTypeInfo(context.getCatalogTable().getResolvedSchema());
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
