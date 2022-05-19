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

package org.flinkextended.flink.ml.examples.tensorflow.ut;

import org.flinkextended.flink.ml.examples.tensorflow.mnist.MnistDataUtil;
import org.flinkextended.flink.ml.examples.tensorflow.mnist.MnistJavaInference;
import org.flinkextended.flink.ml.examples.tensorflow.mnist.ops.MnistTFRPojo;
import org.flinkextended.flink.ml.examples.tensorflow.ops.MnistTFRExtractPojoMapOp;
import org.flinkextended.flink.ml.operator.util.DataTypes;
import org.flinkextended.flink.ml.operator.util.TypeUtil;
import org.flinkextended.flink.ml.tensorflow.client.TFConfig;
import org.flinkextended.flink.ml.tensorflow.client.TFUtilsLegacy;
import org.flinkextended.flink.ml.tensorflow.coding.ExampleCoding;
import org.flinkextended.flink.ml.tensorflow.coding.ExampleCodingConfig;
import org.flinkextended.flink.ml.tensorflow.io.TFRToRowTableSourceFactory;
import org.flinkextended.flink.ml.tensorflow.io.TFRecordSource;
import org.flinkextended.flink.ml.tensorflow.util.TFConstants;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.SysUtil;

import org.apache.flink.api.common.JobExecutionResult;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableDescriptor;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;

import org.apache.curator.test.TestingServer;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

/** TFMnistTest. */
public class TFMnistTest {
    private static TestingServer server;
    private static final String mnist_dist = "mnist_dist.py";
    private static final String mnist_dist_with_input = "mnist_dist_with_input.py";

    public TFMnistTest() {}

    @Before
    public void setUp() throws Exception {
        MnistDataUtil.prepareData();
        server = new TestingServer(2181, true);
    }

    @After
    public void tearDown() throws Exception {
        if (server != null) {
            server.stop();
        }
    }

    public TFConfig buildTFConfig(String pyFile) {
        return buildTFConfig(pyFile, String.valueOf(System.currentTimeMillis()));
    }

    private TFConfig buildTFConfig(String pyFile, String version) {
        System.out.println("Run Test: " + SysUtil._FUNC_());
        String rootPath = new File("").getAbsolutePath();
        String script = rootPath + "/src/test/python/" + pyFile;
        System.out.println("Current version:" + version);
        Map<String, String> properties = new HashMap<>();
        properties.put("batch_size", "32");
        properties.put("input", rootPath + "/target/data/train/");
        properties.put("epochs", "1");
        properties.put("checkpoint_dir", rootPath + "/target/ckpt/" + version);
        properties.put("export_dir", rootPath + "/target/export/" + version);
        return new TFConfig(2, 1, properties, script, "map_fun", null);
    }

    @Test
    public void testDataStreamApi() throws Exception {
        System.out.println("Run Test: " + SysUtil._FUNC_());
        TFConfig config = buildTFConfig(mnist_dist);
        StreamExecutionEnvironment flinkEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        TFUtilsLegacy.train(flinkEnv, config);
        JobExecutionResult result = flinkEnv.execute();
        System.out.println(result.getNetRuntime());
    }

    @Test
    public void testTableStreamApi() throws Exception {
        System.out.println("Run Test: " + SysUtil._FUNC_());
        StreamExecutionEnvironment flinkEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        flinkEnv.setParallelism(2);
        TableEnvironment tableEnv = StreamTableEnvironment.create(flinkEnv);
        StatementSet statementSet = tableEnv.createStatementSet();
        TFConfig config = buildTFConfig(mnist_dist);
        TFUtilsLegacy.train(flinkEnv, tableEnv, statementSet, null, config, null);

        statementSet.execute().getJobClient().get().getJobExecutionResult().get();
    }

    @Test
    public void testDataStreamHaveInput() throws Exception {
        System.out.println("Run Test: " + SysUtil._FUNC_());
        String version = String.valueOf(System.currentTimeMillis());
        StreamExecutionEnvironment flinkEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        String rootPath = new File("").getAbsolutePath();
        String[] paths = new String[2];
        paths[0] = rootPath + "/target/data/train/0.tfrecords";
        paths[1] = rootPath + "/target/data/train/1.tfrecords";
        TFConfig config = buildTFConfig(mnist_dist_with_input, version);
        config.setWorkerNum(paths.length);
        TFRecordSource source = TFRecordSource.createSource(paths, 1);
        DataStream<byte[]> input = flinkEnv.addSource(source).setParallelism(paths.length);
        DataStream<MnistTFRPojo> pojoDataStream =
                input.flatMap(new MnistTFRExtractPojoMapOp())
                        .setParallelism(input.getParallelism());
        setExampleCodingType(config);
        TFUtilsLegacy.train(flinkEnv, pojoDataStream, config);
        JobExecutionResult result = flinkEnv.execute();
        System.out.println("Run Finish:" + result.getNetRuntime());
    }

    public static void setExampleCodingType(TFConfig config) {
        String[] names = {"image_raw", "label"};
        DataTypes[] types = {DataTypes.STRING, DataTypes.INT_32};
        String str =
                ExampleCodingConfig.createExampleConfigStr(
                        names, types, ExampleCodingConfig.ObjectType.POJO, MnistTFRPojo.class);
        config.getProperties().put(TFConstants.INPUT_TF_EXAMPLE_CONFIG, str);
        config.getProperties().put(TFConstants.OUTPUT_TF_EXAMPLE_CONFIG, str);
        config.getProperties()
                .put(MLConstants.ENCODING_CLASS, ExampleCoding.class.getCanonicalName());
        config.getProperties()
                .put(MLConstants.DECODING_CLASS, ExampleCoding.class.getCanonicalName());
    }

    public static void setExampleCodingRowType(TFConfig config) {
        String[] names = {"image_raw", "label"};
        DataTypes[] types = {DataTypes.STRING, DataTypes.INT_32};
        String str =
                ExampleCodingConfig.createExampleConfigStr(
                        names, types, ExampleCodingConfig.ObjectType.ROW, MnistTFRPojo.class);
        config.getProperties().put(TFConstants.INPUT_TF_EXAMPLE_CONFIG, str);
        config.getProperties().put(TFConstants.OUTPUT_TF_EXAMPLE_CONFIG, str);
        config.getProperties()
                .put(MLConstants.ENCODING_CLASS, ExampleCoding.class.getCanonicalName());
        config.getProperties()
                .put(MLConstants.DECODING_CLASS, ExampleCoding.class.getCanonicalName());
    }

    @Test
    public void testTableStreamHaveInput() throws Exception {
        System.out.println("Run Test: " + SysUtil._FUNC_());
        String version = String.valueOf(System.currentTimeMillis());
        TFConfig config = buildTFConfig(mnist_dist_with_input, version);
        setExampleCodingRowType(config);
        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        streamEnv.setParallelism(2);
        TableEnvironment tableEnv = StreamTableEnvironment.create(streamEnv);
        StatementSet statementSet = tableEnv.createStatementSet();
        String rootPath = new File("").getAbsolutePath();
        String paths =
                rootPath
                        + "/target/data/train/0.tfrecords"
                        + ","
                        + rootPath
                        + "/target/data/train/1.tfrecords";

        tableEnv.createTemporaryTable(
                "input",
                TableDescriptor.forConnector("TFRToRow")
                        .schema(TypeUtil.rowTypeInfoToSchema(MnistJavaInference.OUT_ROW_TYPE))
                        .option(TFRToRowTableSourceFactory.CONNECTOR_PATH_OPTION, paths)
                        .option(TFRToRowTableSourceFactory.CONNECTOR_EPOCHS_OPTION, "1")
                        .option(
                                TFRToRowTableSourceFactory.CONNECTOR_CONVERTERS_OPTION,
                                MnistJavaInference.CONVERTERS_STRING)
                        .build());
        //		tableEnv.connect(new MnistTFRToRowTable().paths(paths).epochs(1))
        //				.withSchema(new Schema().schema(TypeUtil.rowTypeInfoToSchema(OUT_ROW_TYPE)))
        //				.createTemporaryTable("input");
        Table inputTable = tableEnv.from("input");
        TFUtilsLegacy.train(streamEnv, tableEnv, statementSet, inputTable, config, null);
        statementSet.execute().getJobClient().get().getJobExecutionResult().get();
    }
}
