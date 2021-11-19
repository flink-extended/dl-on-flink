package com.alibaba.flink.ml.lib.tensorflow.table.descriptor;

import org.apache.flink.configuration.ConfigOption;

import static org.apache.flink.configuration.ConfigOptions.key;

public class TableDebugRowOptions {
    public static final String CONNECTOR_RANK = "connector.rank";
    public static final ConfigOption<Integer> CONNECTOR_RANK_OPTION =
            key(CONNECTOR_RANK)
                    .intType()
                    .noDefaultValue();
    public static final String CONNECTOR_HAS_STRING = "connector.has-string";

    public static final ConfigOption<Boolean> CONNECTOR_HAS_STRING_OPTION =
            key(CONNECTOR_HAS_STRING)
                    .booleanType()
                    .noDefaultValue();
}
