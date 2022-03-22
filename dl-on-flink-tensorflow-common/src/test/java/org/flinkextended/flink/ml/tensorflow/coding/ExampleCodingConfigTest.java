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

package org.flinkextended.flink.ml.tensorflow.coding;

import org.flinkextended.flink.ml.coding.CodingException;
import org.flinkextended.flink.ml.operator.util.DataTypes;

import com.alibaba.fastjson.JSON;
import org.junit.Before;
import org.junit.Test;

import java.util.Arrays;

import static org.junit.Assert.*;

public class ExampleCodingConfigTest {

    private ExampleCodingConfig exampleCodingConfig;

    @Before
    public void setUp() throws Exception {
        exampleCodingConfig = new ExampleCodingConfig();
    }

    @Test
    public void testFromJsonObject() throws CodingException {
        final String str =
                ExampleCodingConfig.createExampleConfigStr(
                        new String[] {"f0", "f1"},
                        new DataTypes[] {DataTypes.STRING, DataTypes.INT_64},
                        ExampleCodingConfig.ObjectType.TUPLE,
                        String.class);
        exampleCodingConfig.fromJsonObject(JSON.parseObject(str));
        assertEquals("f0", exampleCodingConfig.getColName(0));
        assertEquals("f1", exampleCodingConfig.getColName(1));
        assertEquals(DataTypes.STRING, exampleCodingConfig.getType(0));
        assertEquals(DataTypes.INT_64, exampleCodingConfig.getType(1));
        assertEquals(2, exampleCodingConfig.count());
    }

    @Test
    public void testArray() throws CodingException {
        final String str =
                ExampleCodingConfig.createExampleConfigStr(
                        new String[] {"f0", "f1"},
                        new DataTypes[] {DataTypes.STRING, DataTypes.INT_64},
                        ExampleCodingConfig.ObjectType.ARRAY,
                        String.class);
        exampleCodingConfig.fromJsonObject(JSON.parseObject(str));
        final Object[] array =
                (Object[]) exampleCodingConfig.createResultObject(Arrays.asList("Hello", 1L));
        assertEquals("Hello", exampleCodingConfig.getField(array, 0));
        assertEquals(1L, exampleCodingConfig.getField(array, 1));
    }

    @Test
    public void testTuple() throws CodingException {
        final String str =
                ExampleCodingConfig.createExampleConfigStr(
                        new String[] {"f0", "f1"},
                        new DataTypes[] {DataTypes.STRING, DataTypes.INT_64},
                        ExampleCodingConfig.ObjectType.TUPLE,
                        String.class);
        exampleCodingConfig.fromJsonObject(JSON.parseObject(str));
        final Object array = exampleCodingConfig.createResultObject(Arrays.asList("Hello", 1L));
        assertEquals("Hello", exampleCodingConfig.getField(array, 0));
        assertEquals(1L, exampleCodingConfig.getField(array, 1));
    }

    @Test
    public void testRow() throws CodingException {
        final String str =
                ExampleCodingConfig.createExampleConfigStr(
                        new String[] {"f0", "f1"},
                        new DataTypes[] {DataTypes.STRING, DataTypes.INT_64},
                        ExampleCodingConfig.ObjectType.ROW,
                        MyPojo.class);
        exampleCodingConfig.fromJsonObject(JSON.parseObject(str));
        final Object array = exampleCodingConfig.createResultObject(Arrays.asList("Hello", 1L));
        assertEquals("Hello", exampleCodingConfig.getField(array, 0));
        assertEquals(1L, exampleCodingConfig.getField(array, 1));
    }

    @Test
    public void testPOJO() throws CodingException {
        final String str =
                ExampleCodingConfig.createExampleConfigStr(
                        new String[] {"f0", "f1"},
                        new DataTypes[] {DataTypes.STRING, DataTypes.INT_64},
                        ExampleCodingConfig.ObjectType.POJO,
                        MyPojo.class);
        exampleCodingConfig.fromJsonObject(JSON.parseObject(str));
        final Object array = exampleCodingConfig.createResultObject(Arrays.asList("Hello", 1L));
        assertEquals("Hello", exampleCodingConfig.getField(array, 0));
        assertEquals(1L, exampleCodingConfig.getField(array, 1));
    }
}
