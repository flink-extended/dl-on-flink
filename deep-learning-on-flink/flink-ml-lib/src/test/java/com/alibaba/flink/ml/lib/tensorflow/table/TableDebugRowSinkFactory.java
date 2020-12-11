package com.alibaba.flink.ml.lib.tensorflow.table;

import com.alibaba.flink.ml.operator.util.TypeUtil;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.table.factories.TableSinkFactory;
import org.apache.flink.table.sinks.TableSink;
import org.apache.flink.types.Row;

import java.util.Collections;
import java.util.List;
import java.util.Map;

import static org.apache.flink.table.descriptors.ConnectorDescriptorValidator.CONNECTOR_TYPE;

public class TableDebugRowSinkFactory implements TableSinkFactory<Row> {
    @Override
    public TableSink<Row> createTableSink(Context context) {
        RowTypeInfo rowTypeInfo = TypeUtil.schemaToRowTypeInfo(context.getTable().getSchema());
        return new TableDebugRowSink(rowTypeInfo);
    }

    @Override
    public Map<String, String> requiredContext() {
        return Collections.singletonMap(CONNECTOR_TYPE, "TableDebugRow");
    }

    @Override
    public List<String> supportedProperties() {
        return Collections.singletonList("*");
    }
}
