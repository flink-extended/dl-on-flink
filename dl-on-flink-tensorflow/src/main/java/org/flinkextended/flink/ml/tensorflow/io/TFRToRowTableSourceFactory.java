/*
 * Copyright 2022 Deep Learning on Flink Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.flinkextended.flink.ml.tensorflow.io;

import org.flinkextended.flink.ml.operator.util.TypeUtil;
import org.flinkextended.flink.ml.tensorflow.io.descriptor.TFRToRowTableValidator;

import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.configuration.ConfigOption;
import org.apache.flink.table.connector.source.DynamicTableSource;
import org.apache.flink.table.factories.DynamicTableFactory;
import org.apache.flink.table.factories.DynamicTableSourceFactory;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import static org.apache.flink.configuration.ConfigOptions.key;

/** Factory for {@link TFRToRowTableSource}. */
public class TFRToRowTableSourceFactory implements DynamicTableSourceFactory {

    public static final ConfigOption<String> CONNECTOR_CONVERTERS_OPTION =
            key(TFRToRowTableValidator.CONNECTOR_CONVERTERS).stringType().noDefaultValue();

    public static final ConfigOption<String> CONNECTOR_OUT_COL_ALIASES_OPTION =
            key(TFRToRowTableValidator.CONNECTOR_OUT_COL_ALIASES).stringType().noDefaultValue();
    public static final ConfigOption<String> CONNECTOR_EPOCHS_OPTION =
            key(TFRToRowTableValidator.CONNECTOR_EPOCHS).stringType().noDefaultValue();
    public static final ConfigOption<String> CONNECTOR_PATH_OPTION =
            key(TFRToRowTableValidator.CONNECTOR_PATH).stringType().noDefaultValue();

    private TFRExtractRowHelper.ScalarConverter[] getConverters(Map<String, String> properties) {
        return Arrays.stream(properties.get(TFRToRowTableValidator.CONNECTOR_CONVERTERS).split(","))
                .map(TFRExtractRowHelper.ScalarConverter::valueOf)
                .toArray(TFRExtractRowHelper.ScalarConverter[]::new);
    }

    private String[] getOutColAliases(Map<String, String> properties) {
        if (!properties.containsKey(TFRToRowTableValidator.CONNECTOR_OUT_COL_ALIASES)) {
            return null;
        }
        return properties.get(TFRToRowTableValidator.CONNECTOR_OUT_COL_ALIASES).split(",");
    }

    private int getEpochs(Map<String, String> properties) {
        return Integer.parseInt(properties.get(TFRToRowTableValidator.CONNECTOR_EPOCHS));
    }

    private String[] getPaths(Map<String, String> properties) {
        return properties.get(TFRToRowTableValidator.CONNECTOR_PATH).split(",");
    }

    @Override
    public DynamicTableSource createDynamicTableSource(DynamicTableFactory.Context context) {
        final Map<String, String> options = context.getCatalogTable().getOptions();

        String[] paths = getPaths(options);
        int epochs = getEpochs(options);
        String[] outColAliases = getOutColAliases(options);
        TFRExtractRowHelper.ScalarConverter[] converters = getConverters(options);
        RowTypeInfo outRowType =
                TypeUtil.schemaToRowTypeInfo(context.getCatalogTable().getResolvedSchema());
        if (outColAliases != null) {

            return new TFRToRowTableSource(paths, epochs, outRowType, outColAliases, converters);
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
