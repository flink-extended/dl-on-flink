/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.flinkextended.flink.ml.operator.ops.table.descriptor;

import org.apache.flink.table.descriptors.ConnectorDescriptorValidator;
import org.apache.flink.table.descriptors.DescriptorProperties;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;

import static org.apache.flink.table.descriptors.DescriptorProperties.noValidation;

public class MLTableValidator extends ConnectorDescriptorValidator {

    public static final String CONNECTOR_ROLE_CLASS = "connector.role.class";
    public static final String CONNECTOR_EXECUTION_MODE = "connector.execution-mode";
    public static final String CONNECTOR_PARALLELISM = "connector.parallelism";
    public static final String CONNECTOR_ML_CONFIG_PROPERTIES = "connector.ml-config.properties";
    public static final String CONNECTOR_ML_CONFIG_ROLE_PARALLELISM_MAP = "connector.ml-config.role-parallelism-map";
    public static final String CONNECTOR_ML_CONFIG_FUNC_NAME = "connector.ml-config.func-name";
    public static final String CONNECTOR_ML_CONFIG_PYTHON_FILES = "connector.ml-config.python-files";
    public static final String CONNECTOR_ML_CONFIG_ENV_PATH = "connector.ml-config.env-path";


    @Override
    public void validate(DescriptorProperties properties) {
        super.validate(properties);

        validateExecutionMode(properties);
    }

    private void validateExecutionMode(DescriptorProperties properties) {
        Map<String, Consumer<String>> executionModeValidation = new HashMap<>();
        executionModeValidation.put("train", noValidation());
        executionModeValidation.put("inference", noValidation());
        executionModeValidation.put("other", noValidation());

        properties.validateEnum(CONNECTOR_EXECUTION_MODE, false, executionModeValidation);
    }
}
