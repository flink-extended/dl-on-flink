package com.alibaba.flink.ml.operator.ops.table;

import com.alibaba.flink.ml.operator.ops.table.descriptor.LogTable;
import org.apache.flink.configuration.ConfigOption;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.apache.flink.table.connector.sink.DynamicTableSink;
import org.apache.flink.table.data.RowData;
import org.apache.flink.table.factories.DynamicTableSinkFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Collections;
import java.util.Map;
import java.util.Set;

import static com.alibaba.flink.ml.operator.ops.table.descriptor.LogTableValidator.CONNECTOR_RICH_SINK_FUNCTION;

public class LogTableSinkFactory implements DynamicTableSinkFactory {

    private static final Logger LOG = LoggerFactory.getLogger(LogTableSinkFactory.class);

    @Override
    public DynamicTableSink createDynamicTableSink(Context context) {
        final Map<String, String> options = context.getCatalogTable().getOptions();
        String serializedRichFunction = null;
        if (options.containsKey(CONNECTOR_RICH_SINK_FUNCTION)) {
            serializedRichFunction = options.get(CONNECTOR_RICH_SINK_FUNCTION);
        }
        if (serializedRichFunction == null) {
            return new LogTableStreamSink(context.getCatalogTable().getResolvedSchema());
        }

        try {
            RichSinkFunction<RowData> richSinkFunction = LogTable.RichSinkFunctionDeserializer.deserialize(serializedRichFunction);
            return new LogTableStreamSink(context.getCatalogTable().getResolvedSchema(), richSinkFunction);
        } catch (Exception e) {
            LOG.error("Fail to create LogTableStreamSink", e);
        }
        return new LogTableStreamSink();
    }

    @Override
    public String factoryIdentifier() {
        return "LogTable";
    }

    @Override
    public Set<ConfigOption<?>> requiredOptions() {
        return Collections.emptySet();
    }

    @Override
    public Set<ConfigOption<?>> optionalOptions() {
        return Collections.emptySet();
    }
}
