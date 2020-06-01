package com.alibaba.flink.ml.examples.tensorflow.mnist.ops.descriptor;

import com.alibaba.flink.ml.tensorflow.io.TFRExtractRowHelper;
import org.apache.flink.table.descriptors.ConnectorDescriptor;
import org.apache.flink.table.descriptors.DescriptorProperties;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import static com.alibaba.flink.ml.examples.tensorflow.mnist.ops.descriptor.DelayedTFRTableValidator.*;

public class DelayedTFRTable extends ConnectorDescriptor {
    DescriptorProperties properties = new DescriptorProperties();

    public DelayedTFRTable() {
        super("DelayedTFRTable", 1, false);
    }

    @Override
    protected Map<String, String> toConnectorProperties() {
        return properties.asMap();
    }

    public DelayedTFRTable paths(String[] paths) {
        List<List<String>> res = new ArrayList<>();
        for (String path : paths) {
            res.add(Collections.singletonList(path));
        }
        properties.putIndexedFixedProperties(CONNECTOR_PATH, Collections.singletonList("name"), res);
        return this;
    }

    public DelayedTFRTable epochs(int epochs) {
        properties.putInt(CONNECTOR_EPOCHS, epochs);
        return this;
    }

    public DelayedTFRTable converters(TFRExtractRowHelper.ScalarConverter[] converters) {
        List<List<String>> res = new ArrayList<>();
        for (TFRExtractRowHelper.ScalarConverter converter : converters) {
            res.add(Collections.singletonList(converter.name()));
        }
        properties.putIndexedFixedProperties(CONNECTOR_CONVERTERS, Collections.singletonList("name"), res);
        return this;
    }
}
