package com.alibaba.flink.ml.lib.tensorflow.table.descriptor;

import org.apache.flink.table.descriptors.ConnectorDescriptor;
import org.apache.flink.table.descriptors.DescriptorProperties;

import java.util.Map;

import static com.alibaba.flink.ml.lib.tensorflow.table.descriptor.TableDebugRowValidator.CONNECTOR_HAS_STRING;
import static com.alibaba.flink.ml.lib.tensorflow.table.descriptor.TableDebugRowValidator.CONNECTOR_RANK;

public class TableDebugRow extends ConnectorDescriptor {
    DescriptorProperties properties = new DescriptorProperties();

    public TableDebugRow() {
        super("TableDebugRow", 1, false);
    }

    public TableDebugRow rank(int rank) {
        properties.putInt(CONNECTOR_RANK, rank);
        return this;
    }

    public TableDebugRow hasString(boolean hasString) {
        properties.putBoolean(CONNECTOR_HAS_STRING, hasString);
        return this;
    }

    @Override
    protected Map<String, String> toConnectorProperties() {
        return properties.asMap();
    }
}
