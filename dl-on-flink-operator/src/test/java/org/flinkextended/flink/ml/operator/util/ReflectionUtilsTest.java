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

package org.flinkextended.flink.ml.operator.util;

import org.junit.Test;

import java.lang.reflect.Field;
import java.util.Collections;

import static org.junit.Assert.assertEquals;

/** Tests the utility methods related to reflection. */
public class ReflectionUtilsTest {

    @Test
    public void testGetField() {
        Field field = ReflectionUtils.getClassField(Base.class, "field1");
        assertEquals("field1", field.getName());
        assertEquals(Base.class, field.getDeclaringClass());

        Child child = new Child();
        assertEquals("field1", ReflectionUtils.getFieldValue(child, field));
        assertEquals("field1", ReflectionUtils.getFieldValue(child, Base.class, "field1"));
        assertEquals("field2", ReflectionUtils.getFieldValue(child, Child.class, "field2"));
    }

    @Test
    public void testCallMethod() {
        assertEquals(
                5,
                (int)
                        ReflectionUtils.callMethod(
                                null,
                                Child.class,
                                "staticParseInteger",
                                Collections.singletonList(String.class),
                                Collections.singletonList("5")));

        Child child = new Child();
        assertEquals("field1", ReflectionUtils.callMethod(child, Base.class, "getField1"));
        ReflectionUtils.callMethod(
                child,
                Base.class,
                "setField1",
                Collections.singletonList(String.class),
                Collections.singletonList("value"));
        assertEquals("value", ReflectionUtils.callMethod(child, Base.class, "getField1"));
    }

    private static class Base {
        private String field1 = "field1";

        public void setField1(String field1) {
            this.field1 = field1;
        }

        public String getField1() {
            return field1;
        }
    }

    private static class Child extends Base {
        private String field2 = "field2";

        private static int staticParseInteger(String s) {
            return Integer.parseInt(s);
        }
    }
}
