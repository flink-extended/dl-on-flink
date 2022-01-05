package org.flinkextended.flink.ml.operator.ops.table.descriptor;


import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.apache.flink.table.data.RowData;
import org.apache.flink.util.SerializedValue;

import java.io.IOException;
import java.util.Base64;

public class LogTable {

    public static class RichSinkFunctionSerializer {
        public static String serialize(RichSinkFunction<RowData> function) throws IOException {
            SerializedValue<RichSinkFunction<RowData>> serializedValue = new SerializedValue<>(function);
            return Base64.getEncoder().encodeToString(serializedValue.getByteArray());
        }

    }

    public static class RichSinkFunctionDeserializer {
        public static RichSinkFunction<RowData> deserialize(String base64String) throws IOException, ClassNotFoundException {
            byte[] decode = Base64.getDecoder().decode(base64String);
            SerializedValue<RichSinkFunction<RowData>> serializedValue = SerializedValue.fromBytes(decode);
            return serializedValue.deserializeValue(Thread.currentThread().getContextClassLoader());
        }
    }
}
