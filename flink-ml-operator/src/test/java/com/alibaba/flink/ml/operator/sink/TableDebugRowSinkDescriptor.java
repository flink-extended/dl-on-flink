package com.alibaba.flink.ml.operator.sink;

import org.apache.flink.table.descriptors.ConnectorDescriptor;

import java.util.Collections;
import java.util.Map;

public class TableDebugRowSinkDescriptor extends ConnectorDescriptor {
    public TableDebugRowSinkDescriptor() {
        super("TableDebugSink", 1, false);
    }

    @Override
    protected Map<String, String> toConnectorProperties() {
        return Collections.emptyMap();
    }
}
