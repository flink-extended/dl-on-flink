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

package org.flinkextended.flink.ml.tensorflow.util;

import org.flinkextended.flink.ml.operator.util.DataTypes;
import org.flinkextended.flink.ml.tensorflow.client.TFConfig;
import org.flinkextended.flink.ml.tensorflow.coding.ExampleCoding;
import org.flinkextended.flink.ml.tensorflow.coding.ExampleCodingConfig;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.api.common.typeinfo.BasicArrayTypeInfo;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.table.api.TableSchema;

import org.junit.Test;

import java.util.HashMap;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/** Unit test for {@link ExampleCodingConfigUtil}. */
public class ExampleCodingConfigUtilTest {

    @Test
    public void testConfigureEncodeExampleCoding() {
        TFConfig tfConfig = new TFConfig(1, 1, new HashMap<>(), "/tmp/file.py", "func", "/tmp");
        ExampleCodingConfigUtil.configureEncodeExampleCoding(
                tfConfig,
                new String[] {"f0"},
                new DataTypes[] {DataTypes.STRING},
                ExampleCodingConfig.ObjectType.TUPLE,
                Object.class);
        assertNotNull(tfConfig.getProperties().get(TFConstants.INPUT_TF_EXAMPLE_CONFIG));
        assertEquals(
                ExampleCoding.class.getCanonicalName(),
                tfConfig.getProperties().get(MLConstants.ENCODING_CLASS));

        tfConfig = new TFConfig(1, 1, new HashMap<>(), "/tmp/file.py", "func", "/tmp");
        ExampleCodingConfigUtil.configureEncodeExampleCoding(
                tfConfig,
                new String[] {"f0"},
                new TypeInformation[] {Types.STRING},
                ExampleCodingConfig.ObjectType.TUPLE,
                Object.class);
        assertNotNull(tfConfig.getProperties().get(TFConstants.INPUT_TF_EXAMPLE_CONFIG));
        assertEquals(
                ExampleCoding.class.getCanonicalName(),
                tfConfig.getProperties().get(MLConstants.ENCODING_CLASS));
    }

    @Test
    public void testConfigureDecodeExampleCoding() {
        TFConfig tfConfig = new TFConfig(1, 1, new HashMap<>(), "/tmp/file.py", "func", "/tmp");
        ExampleCodingConfigUtil.configureDecodeExampleCoding(
                tfConfig,
                new String[] {"f0"},
                new DataTypes[] {DataTypes.STRING},
                ExampleCodingConfig.ObjectType.TUPLE,
                Object.class);
        assertNotNull(tfConfig.getProperties().get(TFConstants.OUTPUT_TF_EXAMPLE_CONFIG));
        assertEquals(
                ExampleCoding.class.getCanonicalName(),
                tfConfig.getProperties().get(MLConstants.DECODING_CLASS));

        tfConfig = new TFConfig(1, 1, new HashMap<>(), "/tmp/file.py", "func", "/tmp");
        ExampleCodingConfigUtil.configureDecodeExampleCoding(
                tfConfig,
                new String[] {"f0"},
                new TypeInformation[] {Types.STRING},
                ExampleCodingConfig.ObjectType.TUPLE,
                Object.class);
        assertNotNull(tfConfig.getProperties().get(TFConstants.OUTPUT_TF_EXAMPLE_CONFIG));
        assertEquals(
                ExampleCoding.class.getCanonicalName(),
                tfConfig.getProperties().get(MLConstants.DECODING_CLASS));
    }

    @Test
    public void testConfigureExampleCoding() {
        TFConfig tfConfig = new TFConfig(1, 1, new HashMap<>(), "/tmp/file.py", "func", "/tmp");
        final TableSchema schema =
                TableSchema.builder()
                        .field("f0", org.apache.flink.table.api.DataTypes.STRING())
                        .build();
        ExampleCodingConfigUtil.configureExampleCoding(tfConfig, schema, schema);
        assertNotNull(tfConfig.getProperties().get(TFConstants.OUTPUT_TF_EXAMPLE_CONFIG));
        assertEquals(
                ExampleCoding.class.getCanonicalName(),
                tfConfig.getProperties().get(MLConstants.DECODING_CLASS));
        assertNotNull(tfConfig.getProperties().get(TFConstants.INPUT_TF_EXAMPLE_CONFIG));
        assertEquals(
                ExampleCoding.class.getCanonicalName(),
                tfConfig.getProperties().get(MLConstants.ENCODING_CLASS));
    }

    @Test
    public void testDataTypesToTypeInformation() {
        assertEquals(
                Types.STRING, ExampleCodingConfigUtil.dataTypesToTypeInformation(DataTypes.STRING));
        assertEquals(
                Types.BOOLEAN, ExampleCodingConfigUtil.dataTypesToTypeInformation(DataTypes.BOOL));
        assertEquals(
                Types.BYTE, ExampleCodingConfigUtil.dataTypesToTypeInformation(DataTypes.INT_8));
        assertEquals(
                Types.SHORT, ExampleCodingConfigUtil.dataTypesToTypeInformation(DataTypes.INT_16));
        assertEquals(
                Types.INT, ExampleCodingConfigUtil.dataTypesToTypeInformation(DataTypes.INT_32));
        assertEquals(
                Types.LONG, ExampleCodingConfigUtil.dataTypesToTypeInformation(DataTypes.INT_64));
        assertEquals(
                Types.FLOAT,
                ExampleCodingConfigUtil.dataTypesToTypeInformation(DataTypes.FLOAT_32));
        assertEquals(
                Types.DOUBLE,
                ExampleCodingConfigUtil.dataTypesToTypeInformation(DataTypes.FLOAT_64));
        assertEquals(
                Types.CHAR, ExampleCodingConfigUtil.dataTypesToTypeInformation(DataTypes.UINT_16));
        assertEquals(
                BasicArrayTypeInfo.FLOAT_ARRAY_TYPE_INFO,
                ExampleCodingConfigUtil.dataTypesToTypeInformation(DataTypes.FLOAT_32_ARRAY));
        boolean exception = false;
        try {
            ExampleCodingConfigUtil.dataTypesToTypeInformation(DataTypes.COMPLEX_64);
        } catch (RuntimeException e) {
            // expected
            exception = true;
        }
        assertTrue(exception);
    }

    @Test
    public void testTypeInformationToDataTypes() {
        assertEquals(
                DataTypes.STRING, ExampleCodingConfigUtil.typeInformationToDataTypes(Types.STRING));
        assertEquals(
                DataTypes.BOOL, ExampleCodingConfigUtil.typeInformationToDataTypes(Types.BOOLEAN));
        assertEquals(
                DataTypes.INT_8, ExampleCodingConfigUtil.typeInformationToDataTypes(Types.BYTE));
        assertEquals(
                DataTypes.INT_16, ExampleCodingConfigUtil.typeInformationToDataTypes(Types.SHORT));
        assertEquals(
                DataTypes.INT_32, ExampleCodingConfigUtil.typeInformationToDataTypes(Types.INT));
        assertEquals(
                DataTypes.INT_64, ExampleCodingConfigUtil.typeInformationToDataTypes(Types.LONG));
        assertEquals(
                DataTypes.FLOAT_32,
                ExampleCodingConfigUtil.typeInformationToDataTypes(Types.FLOAT));
        assertEquals(
                DataTypes.FLOAT_64,
                ExampleCodingConfigUtil.typeInformationToDataTypes(Types.DOUBLE));
        assertEquals(
                DataTypes.UINT_16, ExampleCodingConfigUtil.typeInformationToDataTypes(Types.CHAR));
        assertEquals(
                DataTypes.FLOAT_32_ARRAY,
                ExampleCodingConfigUtil.typeInformationToDataTypes(
                        BasicArrayTypeInfo.FLOAT_ARRAY_TYPE_INFO));
        boolean exception = false;
        try {
            ExampleCodingConfigUtil.typeInformationToDataTypes(Types.VOID);
        } catch (RuntimeException e) {
            // expected
            exception = true;
        }
        assertTrue(exception);
    }
}
