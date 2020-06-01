package com.alibaba.flink.ml.tensorflow.io;

import org.apache.flink.table.factories.TableSourceFactory;
import org.apache.flink.table.sources.TableSource;
import org.apache.flink.types.Row;

import java.util.Collections;
import java.util.List;
import java.util.Map;

import static org.apache.flink.table.descriptors.ConnectorDescriptorValidator.CONNECTOR_TYPE;

public class TFRToRowTableSourceFactory implements TableSourceFactory<Row> {
    @Override
    public TableSource<Row> createTableSource(Context context) {
        return null;
    }

    @Override
    public Map<String, String> requiredContext() {
        return Collections.singletonMap(CONNECTOR_TYPE, "TFRToRowTable");
    }

    @Override
    public List<String> supportedProperties() {
        return Collections.singletonList("*");
    }
}
