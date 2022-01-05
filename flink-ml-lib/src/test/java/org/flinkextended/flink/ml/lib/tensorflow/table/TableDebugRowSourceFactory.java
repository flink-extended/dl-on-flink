package org.flinkextended.flink.ml.lib.tensorflow.table;

import org.apache.flink.configuration.ConfigOption;
import org.apache.flink.configuration.ReadableConfig;
import org.apache.flink.table.catalog.ResolvedSchema;
import org.apache.flink.table.connector.source.DynamicTableSource;
import org.apache.flink.table.factories.DynamicTableSourceFactory;
import org.apache.flink.table.factories.FactoryUtil;
import org.flinkextended.flink.ml.lib.tensorflow.table.descriptor.TableDebugRowOptions;

import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

public class TableDebugRowSourceFactory implements DynamicTableSourceFactory {

    @Override
    public DynamicTableSource createDynamicTableSource(Context context) {
        final FactoryUtil.TableFactoryHelper helper = FactoryUtil.createTableFactoryHelper(this, context);
        final ReadableConfig options = helper.getOptions();
        ;
        boolean containsRank = options.getOptional(TableDebugRowOptions.CONNECTOR_RANK_OPTION).isPresent();
        boolean containsHasString = options.getOptional(TableDebugRowOptions.CONNECTOR_HAS_STRING_OPTION).isPresent();
        ResolvedSchema tableSchema = context.getCatalogTable().getResolvedSchema();
        if (containsHasString && containsRank) {
            return new TableDebugRowSource(options.get(TableDebugRowOptions.CONNECTOR_RANK_OPTION), options.get(TableDebugRowOptions.CONNECTOR_HAS_STRING_OPTION),
                    tableSchema);
        } else if (containsRank) {
            return new TableDebugRowSource(options.get(TableDebugRowOptions.CONNECTOR_RANK_OPTION), tableSchema);
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
        options.add(TableDebugRowOptions.CONNECTOR_RANK_OPTION);
        options.add(TableDebugRowOptions.CONNECTOR_HAS_STRING_OPTION);
        return options;
    }
}
