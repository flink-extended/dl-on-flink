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

package org.flinkextended.flink.ml.examples.tensorflow.mnist.ops.descriptor;

import org.apache.flink.table.descriptors.ConnectorDescriptorValidator;
import org.apache.flink.table.descriptors.DescriptorProperties;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;

import static org.apache.flink.table.descriptors.DescriptorProperties.noValidation;

/** DelayedTFRTableValidator. */
public class DelayedTFRTableValidator extends ConnectorDescriptorValidator {
    public static final String CONNECTOR_PATH = "connector.path";
    public static final String CONNECTOR_EPOCHS = "connector.epochs";
    public static final String CONNECTOR_CONVERTERS = "connector.converters";

    @Override
    public void validate(DescriptorProperties properties) {
        super.validate(properties);

        validateConverters(properties);
    }

    private void validateConverters(DescriptorProperties properties) {
        Map<String, Consumer<String>> convertersValidation = new HashMap<>();
        convertersValidation.put("first", noValidation());
        convertersValidation.put("last", noValidation());
        convertersValidation.put("max", noValidation());
        convertersValidation.put("min", noValidation());
        convertersValidation.put("one_hot", noValidation());

        properties.validateEnum(CONNECTOR_CONVERTERS, false, convertersValidation);
    }
}
