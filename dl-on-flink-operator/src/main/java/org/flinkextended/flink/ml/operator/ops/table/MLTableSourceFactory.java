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

package org.flinkextended.flink.ml.operator.ops.table;

import org.flinkextended.flink.ml.cluster.ExecutionMode;
import org.flinkextended.flink.ml.cluster.MLConfig;
import org.flinkextended.flink.ml.cluster.role.BaseRole;

import org.apache.flink.table.api.TableSchema;
import org.apache.flink.table.descriptors.DescriptorProperties;
import org.apache.flink.table.factories.TableSourceFactory;
import org.apache.flink.table.sources.TableSource;
import org.apache.flink.types.Row;

import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.apache.flink.table.descriptors.ConnectorDescriptorValidator.CONNECTOR_TYPE;
import static org.flinkextended.flink.ml.operator.ops.table.descriptor.MLTableValidator.CONNECTOR_EXECUTION_MODE;
import static org.flinkextended.flink.ml.operator.ops.table.descriptor.MLTableValidator.CONNECTOR_ML_CONFIG_ENV_PATH;
import static org.flinkextended.flink.ml.operator.ops.table.descriptor.MLTableValidator.CONNECTOR_ML_CONFIG_FUNC_NAME;
import static org.flinkextended.flink.ml.operator.ops.table.descriptor.MLTableValidator.CONNECTOR_ML_CONFIG_PROPERTIES;
import static org.flinkextended.flink.ml.operator.ops.table.descriptor.MLTableValidator.CONNECTOR_ML_CONFIG_PYTHON_FILES;
import static org.flinkextended.flink.ml.operator.ops.table.descriptor.MLTableValidator.CONNECTOR_ML_CONFIG_ROLE_PARALLELISM_MAP;
import static org.flinkextended.flink.ml.operator.ops.table.descriptor.MLTableValidator.CONNECTOR_PARALLELISM;
import static org.flinkextended.flink.ml.operator.ops.table.descriptor.MLTableValidator.CONNECTOR_ROLE_CLASS;

/** Factory for {@link MLTableSource}. */
public class MLTableSourceFactory implements TableSourceFactory<Row> {
    @Override
    public TableSource<Row> createTableSource(Context context) {
        DescriptorProperties properties = new DescriptorProperties();
        properties.putProperties(context.getTable().toProperties());

        TableSchema tableSchema = context.getTable().getSchema();
        ExecutionMode mode = getExecutionMode(properties);
        BaseRole role = getRole(properties);
        MLConfig mlConfig = getMLConfig(properties);
        int parallelism = getParallelism(properties);
        return new MLTableSource(mode, role, mlConfig, tableSchema, parallelism);
    }

    private int getParallelism(DescriptorProperties properties) {
        return properties.getInt(CONNECTOR_PARALLELISM);
    }

    private MLConfig getMLConfig(DescriptorProperties properties) {
        Map<String, String> mlConfigProperties =
                properties.getPropertiesWithPrefix(CONNECTOR_ML_CONFIG_PROPERTIES);
        Map<String, String> mlRoleParallelismProperties =
                properties.getPropertiesWithPrefix(CONNECTOR_ML_CONFIG_ROLE_PARALLELISM_MAP);
        Map<String, Integer> mlRoleParallelismMap =
                toMlRoleParallelismMap(mlRoleParallelismProperties);
        String funcName = properties.getString(CONNECTOR_ML_CONFIG_FUNC_NAME);
        String envPath = null;
        if (properties.containsKey(CONNECTOR_ML_CONFIG_ENV_PATH)) {
            envPath = properties.getString(CONNECTOR_ML_CONFIG_ENV_PATH);
        }

        String[] pythonFiles =
                properties
                        .getFixedIndexedProperties(
                                CONNECTOR_ML_CONFIG_PYTHON_FILES, Collections.singletonList("name"))
                        .stream()
                        .map(m -> m.get("name"))
                        .map(properties::getString)
                        .toArray(String[]::new);
        return new MLConfig(
                mlRoleParallelismMap, mlConfigProperties, pythonFiles, funcName, envPath);
    }

    private Map<String, Integer> toMlRoleParallelismMap(
            Map<String, String> mlRoleParallelismProperties) {
        Map<String, Integer> res = new HashMap<>();
        mlRoleParallelismProperties.forEach((k, v) -> res.put(k, Integer.valueOf(v)));
        return res;
    }

    private BaseRole getRole(DescriptorProperties properties) {
        String roleClass = properties.getString(CONNECTOR_ROLE_CLASS);
        try {
            return (BaseRole) Class.forName(roleClass).newInstance();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private ExecutionMode getExecutionMode(DescriptorProperties properties) {
        return ExecutionMode.valueOf(properties.getString(CONNECTOR_EXECUTION_MODE));
    }

    @Override
    public Map<String, String> requiredContext() {
        return Collections.singletonMap(CONNECTOR_TYPE, "MLTable");
    }

    @Override
    public List<String> supportedProperties() {
        return Collections.singletonList("*");
    }
}
