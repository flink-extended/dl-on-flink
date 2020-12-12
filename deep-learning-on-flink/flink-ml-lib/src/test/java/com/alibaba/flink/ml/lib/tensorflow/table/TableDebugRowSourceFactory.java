package com.alibaba.flink.ml.lib.tensorflow.table;

import org.apache.flink.table.api.TableSchema;
import org.apache.flink.table.descriptors.DescriptorProperties;
import org.apache.flink.table.factories.TableSourceFactory;
import org.apache.flink.table.sources.TableSource;
import org.apache.flink.types.Row;

import java.util.Collections;
import java.util.List;
import java.util.Map;

import static com.alibaba.flink.ml.lib.tensorflow.table.descriptor.TableDebugRowValidator.CONNECTOR_HAS_STRING;
import static com.alibaba.flink.ml.lib.tensorflow.table.descriptor.TableDebugRowValidator.CONNECTOR_RANK;
import static org.apache.flink.table.descriptors.ConnectorDescriptorValidator.CONNECTOR_TYPE;

public class TableDebugRowSourceFactory implements TableSourceFactory<Row> {
    @Override
    public TableSource<Row> createTableSource(Context context) {
        DescriptorProperties properties = new DescriptorProperties();
        properties.putProperties(context.getTable().toProperties());
        boolean containsRank = properties.containsKey(CONNECTOR_RANK);
        boolean containsHasString = properties.containsKey(CONNECTOR_HAS_STRING);
        TableSchema tableSchema = context.getTable().getSchema();
        if (containsHasString && containsRank) {
            return new TableDebugRowSource(properties.getInt(CONNECTOR_RANK), properties.getBoolean(CONNECTOR_HAS_STRING),
                    tableSchema);
        } else if (containsRank) {
            return new TableDebugRowSource(properties.getInt(CONNECTOR_RANK), tableSchema);
        } else {
            return new TableDebugRowSource(tableSchema);
        }
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
