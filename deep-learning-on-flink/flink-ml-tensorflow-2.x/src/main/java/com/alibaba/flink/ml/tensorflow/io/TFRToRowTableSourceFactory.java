package com.alibaba.flink.ml.tensorflow.io;

import com.alibaba.flink.ml.operator.util.TypeUtil;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.configuration.ConfigOption;
import org.apache.flink.table.connector.source.DynamicTableSource;
import org.apache.flink.table.factories.DynamicTableFactory;
import org.apache.flink.table.factories.DynamicTableSourceFactory;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import static com.alibaba.flink.ml.tensorflow.io.descriptor.TFRToRowTableValidator.CONNECTOR_CONVERTERS;
import static com.alibaba.flink.ml.tensorflow.io.descriptor.TFRToRowTableValidator.CONNECTOR_EPOCHS;
import static com.alibaba.flink.ml.tensorflow.io.descriptor.TFRToRowTableValidator.CONNECTOR_OUT_COL_ALIASES;
import static com.alibaba.flink.ml.tensorflow.io.descriptor.TFRToRowTableValidator.CONNECTOR_PATH;
import static org.apache.flink.configuration.ConfigOptions.key;

public class TFRToRowTableSourceFactory implements DynamicTableSourceFactory {

    public static final ConfigOption<String> CONNECTOR_CONVERTERS_OPTION =
            key(CONNECTOR_CONVERTERS)
                    .stringType()
                    .noDefaultValue();

    public static final ConfigOption<String> CONNECTOR_OUT_COL_ALIASES_OPTION =
            key(CONNECTOR_OUT_COL_ALIASES)
                    .stringType()
                    .noDefaultValue();
    public static final ConfigOption<String> CONNECTOR_EPOCHS_OPTION =
            key(CONNECTOR_EPOCHS)
                    .stringType()
                    .noDefaultValue();
    public static final ConfigOption<String> CONNECTOR_PATH_OPTION =
            key(CONNECTOR_PATH)
                    .stringType()
                    .noDefaultValue();


    private TFRExtractRowHelper.ScalarConverter[] getConverters(Map<String, String> properties) {
        return Arrays.stream(properties.get(CONNECTOR_CONVERTERS).split(","))
                .map(TFRExtractRowHelper.ScalarConverter::valueOf)
                .toArray(TFRExtractRowHelper.ScalarConverter[]::new);
    }

    private String[] getOutColAliases(Map<String, String> properties) {
        if (!properties.containsKey(CONNECTOR_OUT_COL_ALIASES)) {
            return null;
        }
        return properties.get(CONNECTOR_OUT_COL_ALIASES).split(",");
    }

    private int getEpochs(Map<String, String> properties) {
        return Integer.parseInt(properties.get(CONNECTOR_EPOCHS));
    }

    private String[] getPaths(Map<String, String> properties) {
        return properties.get(CONNECTOR_PATH).split(",");
    }

    @Override
    public DynamicTableSource createDynamicTableSource(DynamicTableFactory.Context context) {
        final Map<String, String> options = context.getCatalogTable().getOptions();

        String[] paths = getPaths(options);
        int epochs = getEpochs(options);
        String[] outColAliases = getOutColAliases(options);
        TFRExtractRowHelper.ScalarConverter[] converters = getConverters(options);
        RowTypeInfo outRowType = TypeUtil.schemaToRowTypeInfo(context.getCatalogTable().getResolvedSchema());
        if (outColAliases != null) {

            return new TFRToRowTableSource(paths, epochs, outRowType,
                    outColAliases, converters);
        } else {
            return new TFRToRowTableSource(paths, epochs, outRowType, converters);
        }
    }

    @Override
    public String factoryIdentifier() {
        return "TFRToRow";
    }

    @Override
    public Set<ConfigOption<?>> requiredOptions() {
        Set<ConfigOption<?>> options = new HashSet<>();
        options.add(CONNECTOR_CONVERTERS_OPTION);
        options.add(CONNECTOR_EPOCHS_OPTION);
        options.add(CONNECTOR_PATH_OPTION);
        return options;
    }

    @Override
    public Set<ConfigOption<?>> optionalOptions() {
        Set<ConfigOption<?>> options = new HashSet<>();
        options.add(CONNECTOR_OUT_COL_ALIASES_OPTION);
        return options;
    }
}
