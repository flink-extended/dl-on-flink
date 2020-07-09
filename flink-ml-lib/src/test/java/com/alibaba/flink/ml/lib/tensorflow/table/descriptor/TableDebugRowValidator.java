package com.alibaba.flink.ml.lib.tensorflow.table.descriptor;

import org.apache.flink.table.descriptors.ConnectorDescriptorValidator;

public class TableDebugRowValidator extends ConnectorDescriptorValidator {
    public static final String CONNECTOR_RANK = "connector.rank";
    public static final String CONNECTOR_HAS_STRING = "connector.has-string";
}
