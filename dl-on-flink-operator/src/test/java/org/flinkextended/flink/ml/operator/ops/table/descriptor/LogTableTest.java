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

package org.flinkextended.flink.ml.operator.ops.table.descriptor;

import org.flinkextended.flink.ml.operator.ops.table.descriptor.LogTable.RichSinkFunctionSerializer;

import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.apache.flink.table.data.RowData;

import org.junit.Before;
import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

/** Unit test for {@link LogTable}. */
public class LogTableTest {
    RichSinkFunction<RowData> function;
    String serializedString;

    @Before
    public void setUp() throws Exception {
        function = new TestRichSinkFunction<>("testpath");
        serializedString = RichSinkFunctionSerializer.serialize(function);
    }

    @Test
    public void testSerializeRichSinkFunction() throws IOException {
        String serialize = RichSinkFunctionSerializer.serialize(function);
        assertNotNull(serialize);
    }

    @Test
    public void testDeserializeRichSinkFunction() throws IOException, ClassNotFoundException {
        RichSinkFunction<RowData> func =
                LogTable.RichSinkFunctionDeserializer.deserialize(serializedString);
        assertNotNull(func);
    }

    @Test
    public void testSerializeAndDeserialize() throws IOException, ClassNotFoundException {
        String base64String = RichSinkFunctionSerializer.serialize(function);
        RichSinkFunction<RowData> deserialize =
                LogTable.RichSinkFunctionDeserializer.deserialize(base64String);
        assertEquals(deserialize, function);
    }

    static class TestRichSinkFunction<T> extends RichSinkFunction<T> {
        private String path;

        TestRichSinkFunction(String path) {
            this.path = path;
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj) {
                return true;
            }

            if (!(obj instanceof TestRichSinkFunction)) {
                return false;
            }

            TestRichSinkFunction<RowData> other = (TestRichSinkFunction<RowData>) obj;
            return path.equals(other.path);
        }
    }
}
