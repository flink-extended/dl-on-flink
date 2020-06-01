package com.alibaba.flink.ml.examples.tensorflow.ops.descriptor;

import com.alibaba.flink.ml.tensorflow.io.descriptor.TFRToRowTable;

import static com.alibaba.flink.ml.examples.tensorflow.mnist.MnistJavaInference.CONVERTERS;
import org.apache.flink.table.descriptors.ConnectorDescriptor;

import java.util.Map;

public class MnistTFRToRowTable extends TFRToRowTable {
    public MnistTFRToRowTable() {
        super();
        converters(CONVERTERS);
    }
}
