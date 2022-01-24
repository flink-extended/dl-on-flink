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

package org.flinkextended.flink.ml.examples.tensorflow.ut;


import org.flinkextended.flink.ml.examples.tensorflow.mnist.MnistDataUtil;
import org.flinkextended.flink.ml.examples.tensorflow.mnist.MnistJavaInference;
import org.flinkextended.flink.ml.examples.tensorflow.mnist.ops.MnistTFRExtractRowForJavaFunction;
import org.flinkextended.flink.ml.examples.tensorflow.mnist.ops.MnistTFRPojo;
import org.flinkextended.flink.ml.examples.tensorflow.ops.MnistTFRExtractPojoMapOp;
import org.flinkextended.flink.ml.operator.ops.sink.LogSink;
import org.flinkextended.flink.ml.operator.util.FlinkUtil;
import org.flinkextended.flink.ml.operator.util.TypeUtil;
import org.flinkextended.flink.ml.tensorflow.client.TFConfig;
import org.flinkextended.flink.ml.tensorflow.client.TFUtils;
import org.flinkextended.flink.ml.tensorflow.coding.ExampleCoding;
import org.flinkextended.flink.ml.tensorflow.coding.ExampleCodingConfig;
import org.flinkextended.flink.ml.tensorflow.io.TFRToRowSourceFunc;
import org.flinkextended.flink.ml.tensorflow.io.TFRToRowTableSourceFactory;
import org.flinkextended.flink.ml.tensorflow.io.TFRecordSource;
import org.flinkextended.flink.ml.tensorflow.util.TFConstants;
import org.flinkextended.flink.ml.util.IpHostUtil;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.SysUtil;
import org.flinkextended.flink.ml.util.TestUtil;
import com.google.common.base.Joiner;
import org.apache.curator.test.TestingServer;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableDescriptor;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.TableSchema;
import org.apache.flink.table.api.Types;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.functions.TableFunction;
import org.apache.flink.types.Row;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.StringJoiner;
import java.util.concurrent.ThreadLocalRandom;

public class TFMnistInferenceTest {

    private static TestingServer server;
    private static final String mnist_dist_with_input = "mnist_dist_with_input.py";
    private static final String mnist_inference_with_input = "mnist_table_inference.py";
    private static String version = "0";
    private static String rootPath = TestUtil.getProjectRootPath() + "/flink-ml-examples";
    private static final String checkpointPath = rootPath + "/target/ckpt/" + version;
    public static final String exportPath = rootPath + "/target/export/" + version;
    public static final String testDataPath = rootPath + "/target/data/test";

    @Before
    public void setUp() throws Exception {
        MnistDataUtil.prepareData();
        server = new TestingServer(IpHostUtil.getFreePort(), true);
        generateModelIfNeeded();
    }

    @After
    public void tearDown() throws Exception {
        if (server != null) {
            server.close();
            server = null;
        }
    }

    private static TFConfig buildTFConfig(String pyFile) {
        String script = rootPath + "/src/test/python/" + pyFile;
        System.out.println("Current version:" + version);
        Map<String, String> properties = new HashMap<>();
        properties.put("batch_size", "32");
        properties.put("input", rootPath + "/target/data/train/");
        properties.put("epochs", "1");
        properties.put("checkpoint_dir", checkpointPath);
        properties.put("export_dir", exportPath);
        properties.put(MLConstants.CONFIG_ZOOKEEPER_CONNECT_STR, server.getConnectString());
        return new TFConfig(4, 1, properties, script, "map_fun", null);
    }

    public static void generateModelIfNeeded() throws Exception {
        File tmp = new File(exportPath);
        if (!tmp.exists()) {
            boolean startServer = server == null;
            if (startServer) {
                server = new TestingServer(IpHostUtil.getFreePort(), true);
            }
            dataStreamHaveInput();
            if (startServer) {
                server.close();
                server = null;
            }
        }
    }

    private static void dataStreamHaveInput() throws Exception {
        TFConfig config = buildTFConfig(mnist_dist_with_input);
        TFMnistTest.setExampleCodingType(config);
        StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        String rootPath = new File("").getAbsolutePath();
        String[] paths = new String[2];
        paths[0] = rootPath + "/target/data/train/0.tfrecords";
        paths[1] = rootPath + "/target/data/train/1.tfrecords";
        TFRecordSource source = TFRecordSource.createSource(paths, 1);
        DataStream<byte[]> input = streamEnv.addSource(source).setParallelism(paths.length);
        DataStream<MnistTFRPojo> pojoDataStream = input.flatMap(new MnistTFRExtractPojoMapOp())
                .setParallelism(input.getParallelism());
        TFUtils.train(streamEnv, pojoDataStream, config);
        streamEnv.execute();
    }

    protected static void setExampleCodingTypeWithPojoOut(TFConfig config) {
        String[] names = {"image_raw", "label"};
        org.flinkextended.flink.ml.operator.util.DataTypes[] types = {org.flinkextended.flink.ml.operator.util.DataTypes.STRING,
                org.flinkextended.flink.ml.operator.util.DataTypes.INT_32};
        String str = ExampleCodingConfig.createExampleConfigStr(names, types,
                ExampleCodingConfig.ObjectType.ROW, MnistTFRPojo.class);
        config.getProperties().put(TFConstants.INPUT_TF_EXAMPLE_CONFIG, str);

        String[] namesOutput = {"predict_label", "label_org"};
        org.flinkextended.flink.ml.operator.util.DataTypes[] typesOutput = {org.flinkextended.flink.ml.operator.util.DataTypes.INT_32,
                org.flinkextended.flink.ml.operator.util.DataTypes.INT_32};
        String strOutput = ExampleCodingConfig.createExampleConfigStr(namesOutput, typesOutput,
                ExampleCodingConfig.ObjectType.POJO, InferenceOutPojo.class);
        config.getProperties().put(TFConstants.OUTPUT_TF_EXAMPLE_CONFIG, strOutput);
        config.getProperties().put(MLConstants.ENCODING_CLASS, ExampleCoding.class.getCanonicalName());
        config.getProperties().put(MLConstants.DECODING_CLASS, ExampleCoding.class.getCanonicalName());
    }

    protected static void setExampleCodingTypeWithRowOut(TFConfig config) {
        String[] names = { "image_raw", "label" };
        org.flinkextended.flink.ml.operator.util.DataTypes[] types = { org.flinkextended.flink.ml.operator.util.DataTypes.STRING,
                org.flinkextended.flink.ml.operator.util.DataTypes.INT_32 };
        String str = ExampleCodingConfig.createExampleConfigStr(names, types,
                ExampleCodingConfig.ObjectType.ROW, MnistTFRPojo.class);
        config.getProperties().put(TFConstants.INPUT_TF_EXAMPLE_CONFIG, str);

        String[] namesOutput = { "predict_label", "label_org" };
        org.flinkextended.flink.ml.operator.util.DataTypes[] typesOutput = { org.flinkextended.flink.ml.operator.util.DataTypes.INT_32,
                org.flinkextended.flink.ml.operator.util.DataTypes.INT_32 };
        String strOutput = ExampleCodingConfig.createExampleConfigStr(namesOutput, typesOutput,
                ExampleCodingConfig.ObjectType.ROW, InferenceOutPojo.class);
        config.getProperties().put(TFConstants.OUTPUT_TF_EXAMPLE_CONFIG, strOutput);
        config.getProperties().put(MLConstants.ENCODING_CLASS, ExampleCoding.class.getCanonicalName());
        config.getProperties().put(MLConstants.DECODING_CLASS, ExampleCoding.class.getCanonicalName());
    }


    @Test
    public void inferenceDataStreamWithInput() throws Exception {
        System.out.println("Run Test: " + SysUtil._FUNC_());
        StreamExecutionEnvironment flinkEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        String[] paths = new String[]{testDataPath + "/0.tfrecords", testDataPath + "/1.tfrecords"};
        DataStream<Row> inputDS = flinkEnv.addSource(new TFRToRowSourceFunc(paths, 1, MnistJavaInference.OUT_ROW_TYPE,
                MnistJavaInference.CONVERTERS)).setParallelism(paths.length);
        TFConfig tfConfig = buildTFConfig(mnist_inference_with_input);
        tfConfig.setWorkerNum(paths.length);
        tfConfig.setPsNum(0);
        setExampleCodingTypeWithPojoOut(tfConfig);
        DataStream<InferenceOutPojo> outDS = TFUtils.inference(flinkEnv, inputDS, tfConfig, InferenceOutPojo.class);
        outDS.addSink(new LogSink<>()).setParallelism(tfConfig.getWorkerNum());
        flinkEnv.execute();
    }

    @Test
    public void tableStreamWithInput() throws Exception {
        System.out.println("Run Test: " + SysUtil._FUNC_());
        inferenceWithTable();
    }


    private void inferenceWithTable() throws Exception {
        StreamExecutionEnvironment flinkEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        flinkEnv.setParallelism(2);
        TableEnvironment tableEnv = StreamTableEnvironment.create(flinkEnv);
        StatementSet statementSet = tableEnv.createStatementSet();
        TFConfig config = buildTFConfig(mnist_inference_with_input);
        config.setPsNum(0);
        config.setWorkerNum(3);
        setExampleCodingTypeWithRowOut(config);
        //create input table
        String paths = testDataPath + "/0.tfrecords";
        String tblName = "tfr_input_table";
//		tableEnv.registerTableSource(tblName, new MnistTFRToRowTableSource(paths, 1));

        tableEnv.createTemporaryTable(tblName, TableDescriptor
                .forConnector("TFRToRow")
                .schema(TypeUtil.rowTypeInfoToSchema(MnistJavaInference.OUT_ROW_TYPE))
                .option(TFRToRowTableSourceFactory.CONNECTOR_PATH_OPTION, paths)
                .option(TFRToRowTableSourceFactory.CONNECTOR_CONVERTERS_OPTION, MnistJavaInference.CONVERTERS_STRING)
                .option(TFRToRowTableSourceFactory.CONNECTOR_EPOCHS_OPTION, "1")
                .build());
//		tableEnv.connect(new MnistTFRToRowTable().paths(paths).epochs(1))
//				.withSchema(new Schema().schema(TypeUtil.rowTypeInfoToSchema(OUT_ROW_TYPE)))
//				.createTemporaryTable(tblName);
        Table inputTable = tableEnv.from(tblName);

        //construct out schema
        Schema outSchema = Schema.newBuilder()
                .column("label_org", DataTypes.INT())
                .column("predict_label", DataTypes.INT())
                .build();
//		TableSchema outSchema = TableSchema.builder()
//				.field("label_org", Types.INT())
//				.field("predict_label", Types.INT())
//				.build();
        Table predictTbl = TFUtils.inference(flinkEnv, tableEnv, statementSet, inputTable, config, outSchema);
        tableEnv.createTemporaryView("predict_tbl", predictTbl);

        tableEnv.createTemporaryTable("predict_sink", TableDescriptor
                .forConnector("LogTable")
                .schema(outSchema)
                .build());
//		tableEnv.connect(new LogTable())
//				.withSchema(new Schema().schema(outSchema))
//				.createTemporaryTable("predict_sink");
        statementSet.addInsert("predict_sink", predictTbl);
        statementSet.execute().getJobClient().get()
                .getJobExecutionResult().get();
    }

    @Test
    public void testInferenceJavaFunction() throws Exception {
        System.out.println("Run Test: " + SysUtil._FUNC_());
        inferenceWithJava(1, false);
    }

    @Test
    public void testInferenceJavaFunctionBatching() throws Exception {
        System.out.println("Run Test: " + SysUtil._FUNC_());
        int batchSize = ThreadLocalRandom.current().nextInt(500) + 2;
        System.out.println("Batch size set to " + batchSize);
        inferenceWithJava(batchSize, false);
    }

    @Test
    public void testJavaInferenceTableToStream() throws Exception {
        System.out.println("Run Test: " + SysUtil._FUNC_());
        int batchSize = ThreadLocalRandom.current().nextInt(500) + 2;
        System.out.println("Batch size set to " + batchSize);
        inferenceWithJava(batchSize, true);
    }

    protected static void setExampleCodingTypeRow(TFConfig config) {
        String[] names = {"image_raw", "org_label"};
        org.flinkextended.flink.ml.operator.util.DataTypes[] types = {org.flinkextended.flink.ml.operator.util.DataTypes.FLOAT_32_ARRAY,
                org.flinkextended.flink.ml.operator.util.DataTypes.INT_32};
        String str = ExampleCodingConfig.createExampleConfigStr(names, types,
                ExampleCodingConfig.ObjectType.ROW, MnistTFRPojo.class);
        config.getProperties().put(TFConstants.INPUT_TF_EXAMPLE_CONFIG, str);

        String[] namesOutput = {"real_label", "predicted_label"};
        org.flinkextended.flink.ml.operator.util.DataTypes[] typesOutput = {org.flinkextended.flink.ml.operator.util.DataTypes.INT_32,
                org.flinkextended.flink.ml.operator.util.DataTypes.INT_32};
        String strOutput = ExampleCodingConfig.createExampleConfigStr(namesOutput, typesOutput,
                ExampleCodingConfig.ObjectType.ROW, InferenceOutPojo.class);
        config.getProperties().put(TFConstants.OUTPUT_TF_EXAMPLE_CONFIG, strOutput);
        config.getProperties().put(MLConstants.ENCODING_CLASS, ExampleCoding.class.getCanonicalName());
        config.getProperties().put(MLConstants.DECODING_CLASS, ExampleCoding.class.getCanonicalName());
    }

    private void inferenceWithJava(int batchSize, boolean toStream) throws Exception {
        StreamExecutionEnvironment flinkEnv = StreamExecutionEnvironment.getExecutionEnvironment();
        flinkEnv.setParallelism(2);
        TableEnvironment tableEnv = StreamTableEnvironment.create(flinkEnv);
        StatementSet statementSet = tableEnv.createStatementSet();
        TFConfig tfConfig = new TFConfig(2, 0, null, (String) null, null, null);
        tfConfig.setPsNum(0);
        tfConfig.setWorkerNum(2);
        tfConfig.addProperty(TFConstants.TF_INFERENCE_BATCH_SIZE, String.valueOf(batchSize));
        File testDataDir = new File(testDataPath);
        File[] files = testDataDir.listFiles();
        StringJoiner pathJoiner = new StringJoiner(",");
        for (int i = 0; i < files.length; ++i) {
            pathJoiner.add(files[i].getAbsolutePath());
        }
        String paths = pathJoiner.toString();
        String tfrTblName = "tfr_input_table";

        tableEnv.createTemporaryTable(tfrTblName, TableDescriptor
                .forConnector("TFRToRow")
                .schema(TypeUtil.rowTypeInfoToSchema(MnistJavaInference.OUT_ROW_TYPE))
                .option(TFRToRowTableSourceFactory.CONNECTOR_PATH_OPTION, paths)
                .option(TFRToRowTableSourceFactory.CONNECTOR_EPOCHS_OPTION, "1")
                .option(TFRToRowTableSourceFactory.CONNECTOR_CONVERTERS_OPTION, MnistJavaInference.CONVERTERS_STRING)
                .build());
//		tableEnv.connect(new MnistTFRToRowTable().paths(paths).epochs(1))
//				.withSchema(new Schema().schema(TypeUtil.rowTypeInfoToSchema(OUT_ROW_TYPE)))
//				.createTemporaryTable(tfrTblName);
        Table tableSource = tableEnv.from(tfrTblName);
        TableFunction extractFunc = new MnistTFRExtractRowForJavaFunction();
        String extFuncName = "tfr_extract";
        FlinkUtil.registerTableFunction(tableEnv, extFuncName, extractFunc);

        TableSchema extractTableSchema = TableSchema.builder()
                .field("image", Types.PRIMITIVE_ARRAY(Types.FLOAT()))
                .field("org_label", Types.LONG()).build();
        String outCols = Joiner.on(",").join(extractTableSchema.getFieldNames());
        String inCols = Joiner.on(",").join(tableSource.getSchema().getFieldNames());
        Table extracted = tableEnv.sqlQuery(String.format("select %s from %s, LATERAL TABLE(%s(%s)) as T(%s)",
                outCols, tfrTblName, extFuncName, inCols, outCols));

        Schema outSchema = Schema.newBuilder()
                .column("label_org", DataTypes.INT())
                .column("predict_label", DataTypes.INT())
                .build();

//		TableSchema outSchema = TableSchema.builder().field("real_label", Types.LONG()).
//				field("predicted_label", Types.LONG()).build();

        // set required configs
        tfConfig.addProperty(TFConstants.TF_INFERENCE_EXPORT_PATH, rootPath + "/target/export/0");
        tfConfig.addProperty(TFConstants.TF_INFERENCE_INPUT_TENSOR_NAMES, "image");
        tfConfig.addProperty(TFConstants.TF_INFERENCE_OUTPUT_TENSOR_NAMES, "prediction");
        tfConfig.addProperty(TFConstants.TF_INFERENCE_OUTPUT_ROW_FIELDS,
                Joiner.on(",").join(new String[]{"org_label", "prediction"}));
        setExampleCodingTypeRow(tfConfig);

        Table predicted = TFUtils.inference(flinkEnv, tableEnv, statementSet, extracted, tfConfig, outSchema);

        tableEnv.createTemporaryTable("inference_sink", TableDescriptor
                .forConnector("LogTable")
                .schema(outSchema)
                .build());
//		tableEnv.connect(new LogTable().richSinkFunction(new LogInferAccSink()))
//				.withSchema(new Schema().schema(outSchema))
//				.createTemporaryTable("inference_sink");
        statementSet.addInsert("inference_sink", predicted);
        statementSet.execute().getJobClient().get()
                .getJobExecutionResult().get();
    }
}
