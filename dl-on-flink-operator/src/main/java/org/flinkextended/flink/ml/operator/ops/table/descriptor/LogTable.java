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

import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.apache.flink.table.data.RowData;
import org.apache.flink.util.SerializedValue;

import java.io.IOException;
import java.util.Base64;

public class LogTable {

    public static class RichSinkFunctionSerializer {
        public static String serialize(RichSinkFunction<RowData> function) throws IOException {
            SerializedValue<RichSinkFunction<RowData>> serializedValue =
                    new SerializedValue<>(function);
            return Base64.getEncoder().encodeToString(serializedValue.getByteArray());
        }
    }

    public static class RichSinkFunctionDeserializer {
        public static RichSinkFunction<RowData> deserialize(String base64String)
                throws IOException, ClassNotFoundException {
            byte[] decode = Base64.getDecoder().decode(base64String);
            SerializedValue<RichSinkFunction<RowData>> serializedValue =
                    SerializedValue.fromBytes(decode);
            return serializedValue.deserializeValue(Thread.currentThread().getContextClassLoader());
        }
    }
}
