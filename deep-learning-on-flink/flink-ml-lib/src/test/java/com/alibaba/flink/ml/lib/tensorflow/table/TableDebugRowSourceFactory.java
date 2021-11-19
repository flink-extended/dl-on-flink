package com.alibaba.flink.ml.lib.tensorflow.table;

import org.apache.flink.configuration.ConfigOption;
import org.apache.flink.configuration.ReadableConfig;
import org.apache.flink.table.catalog.ResolvedSchema;
import org.apache.flink.table.connector.source.DynamicTableSource;
import org.apache.flink.table.factories.DynamicTableSourceFactory;
import org.apache.flink.table.factories.FactoryUtil;

import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

import static com.alibaba.flink.ml.lib.tensorflow.table.descriptor.TableDebugRowOptions.CONNECTOR_HAS_STRING_OPTION;
import static com.alibaba.flink.ml.lib.tensorflow.table.descriptor.TableDebugRowOptions.CONNECTOR_RANK_OPTION;

public class TableDebugRowSourceFactory implements DynamicTableSourceFactory {

    @Override
    public DynamicTableSource createDynamicTableSource(Context context) {
        final FactoryUtil.TableFactoryHelper helper = FactoryUtil.createTableFactoryHelper(this, context);
        final ReadableConfig options = helper.getOptions();
        ;
        boolean containsRank = options.getOptional(CONNECTOR_RANK_OPTION).isPresent();
        boolean containsHasString = options.getOptional(CONNECTOR_HAS_STRING_OPTION).isPresent();
        ResolvedSchema tableSchema = context.getCatalogTable().getResolvedSchema();
        if (containsHasString && containsRank) {
            return new TableDebugRowSource(options.get(CONNECTOR_RANK_OPTION), options.get(CONNECTOR_HAS_STRING_OPTION),
                    tableSchema);
        } else if (containsRank) {
            return new TableDebugRowSource(options.get(CONNECTOR_RANK_OPTION), tableSchema);
        } else {
            return new TableDebugRowSource(tableSchema);
        }
    }

    @Override
    public String factoryIdentifier() {
        return "TableDebugRow";
    }

    @Override
    public Set<ConfigOption<?>> requiredOptions() {
        return Collections.emptySet();
    }

    @Override
    public Set<ConfigOption<?>> optionalOptions() {
        Set<ConfigOption<?>> options = new HashSet<>();
        options.add(CONNECTOR_RANK_OPTION);
        options.add(CONNECTOR_HAS_STRING_OPTION);
        return options;
    }
}
