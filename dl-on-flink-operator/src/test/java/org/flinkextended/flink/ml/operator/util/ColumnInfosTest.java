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

package org.flinkextended.flink.ml.operator.util;

import org.flinkextended.flink.ml.util.MLException;

import org.apache.flink.api.common.ExecutionConfig;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.tuple.Tuple1;
import org.apache.flink.api.java.typeutils.TupleTypeInfo;
import org.apache.flink.types.Row;
import org.apache.flink.types.RowKind;

import org.junit.Before;
import org.junit.Test;

import java.util.Collections;
import java.util.Map;

import static org.hamcrest.CoreMatchers.instanceOf;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThat;
import static org.junit.Assert.assertTrue;

/** Unit test for {@link ColumnInfos}. */
public class ColumnInfosTest {

    @Before
    public void setUp() throws Exception {}

    @Test
    public void testCreateTypeInformation() {
        final TypeInformation<Row> typeInfo =
                Types.ROW(
                        Types.FLOAT,
                        Types.DOUBLE,
                        Types.LONG,
                        Types.INT,
                        Types.CHAR,
                        Types.SHORT,
                        Types.BYTE,
                        Types.BOOLEAN,
                        Types.STRING,
                        Types.PRIMITIVE_ARRAY(Types.BYTE),
                        Types.PRIMITIVE_ARRAY(Types.FLOAT));
        final ColumnInfos columnInfos = ColumnInfos.fromTypeInformation(typeInfo);
        assertEquals(11, columnInfos.count());
        assertEquals(typeInfo, columnInfos.getOriginalTI());
        assertTrue(columnInfos.isDecomposed());
    }

    @Test(expected = IllegalArgumentException.class)
    public void testCreateUnsupportedTypeInformation() {
        final TypeInformation<Row> typeInfo = Types.ROW(Types.BIG_INT);
        ColumnInfos.fromTypeInformation(typeInfo);
    }

    @Test
    public void testGetColName() {
        final String[] fieldNames = {"int_field", "float_field"};
        final TypeInformation<Row> typeInfo = Types.ROW_NAMED(fieldNames, Types.INT, Types.FLOAT);
        final ColumnInfos columnInfos = ColumnInfos.fromTypeInformation(typeInfo);
        assertEquals("int_field", columnInfos.getColName(0));
        assertEquals("float_field", columnInfos.getColName(1));
        assertEquals(Types.INT, columnInfos.getTiInfo(0));
        assertEquals(Types.FLOAT, columnInfos.getTiInfo(1));
        assertEquals(DataTypes.INT_32, columnInfos.getDataTypes(0));
        assertEquals(DataTypes.FLOAT_32, columnInfos.getDataTypes(1));

        final Map<String, String> nameToTypeMap = columnInfos.getNameToTypeMap();
        assertEquals(DataTypes.INT_32.toString(), nameToTypeMap.get("int_field"));
        assertEquals(DataTypes.FLOAT_32.toString(), nameToTypeMap.get("float_field"));
    }

    @Test
    public void testGetField() {
        TypeInformation<?> typeInfo = Types.ROW(Types.INT);
        ColumnInfos columnInfos = ColumnInfos.fromTypeInformation(typeInfo);
        final Row row = new Row(RowKind.INSERT, 1);
        row.setField(0, 1);
        final Object field = columnInfos.getField(row, 0);
        assertThat(field, instanceOf(Integer.class));

        typeInfo = new TupleTypeInfo<>(Types.INT);
        columnInfos = ColumnInfos.fromTypeInformation(typeInfo);
        final Tuple1<Integer> tuple = new Tuple1<>(99);
        assertEquals(99, columnInfos.getField(tuple, 0));

        typeInfo = Types.POJO(TestPojo.class);
        columnInfos = ColumnInfos.fromTypeInformation(typeInfo);
        final TestPojo testPojo = new TestPojo(99);
        assertEquals(99, columnInfos.getField(testPojo, 0));
    }

    @Test
    public void testCreateResultObject() throws MLException {
        TypeInformation<?> typeInfo = Types.ROW(Types.INT);
        ColumnInfos columnInfos = ColumnInfos.fromTypeInformation(typeInfo);
        Object res =
                columnInfos.createResultObject(
                        Collections.singletonList(99), new ExecutionConfig());
        assertThat(res, instanceOf(Row.class));
        assertEquals(99, ((Row) res).getField(0));

        typeInfo = new TupleTypeInfo<>(Types.INT);
        columnInfos = ColumnInfos.fromTypeInformation(typeInfo);
        res = columnInfos.createResultObject(Collections.singletonList(99), new ExecutionConfig());
        assertThat(res, instanceOf(Tuple1.class));
        assertEquals(new Integer(99), ((Tuple1<?>) res).getField(0));

        typeInfo = Types.POJO(TestPojo.class);
        columnInfos = ColumnInfos.fromTypeInformation(typeInfo);
        res = columnInfos.createResultObject(Collections.singletonList(99), new ExecutionConfig());
        assertThat(res, instanceOf(TestPojo.class));
        assertEquals(99, ((TestPojo) res).num);
    }

    /** Dummy class for unit test. */
    public static class TestPojo {
        public int num;

        public TestPojo() {}

        public TestPojo(int num) {
            this.num = num;
        }
    }
}
