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

package com.alibaba.flink.ml.examples.tensorflow.mnist;


import com.alibaba.flink.ml.examples.tensorflow.mnist.ops.DelayedTFRTableSourceStream;
import com.alibaba.flink.ml.examples.tensorflow.mnist.ops.LogInferAccSink;
import com.alibaba.flink.ml.examples.tensorflow.mnist.ops.MnistTFRExtractRowForJavaFunction;
import com.alibaba.flink.ml.examples.tensorflow.mnist.ops.MnistTFRPojo;
import com.alibaba.flink.ml.operator.ops.sink.LogTableStreamSink;
import com.alibaba.flink.ml.operator.util.FlinkUtil;
import com.alibaba.flink.ml.tensorflow.client.TFConfig;
import com.alibaba.flink.ml.tensorflow.client.TFUtils;
import com.alibaba.flink.ml.tensorflow.coding.ExampleCoding;
import com.alibaba.flink.ml.tensorflow.coding.ExampleCodingConfig;
import com.alibaba.flink.ml.tensorflow.io.TFRExtractRowHelper;
import com.alibaba.flink.ml.tensorflow.util.TFConstants;
import com.alibaba.flink.ml.util.MLConstants;
import com.google.common.base.Joiner;
import com.google.common.base.Preconditions;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;
import org.apache.commons.lang.StringUtils;

import org.apache.flink.api.common.restartstrategy.RestartStrategies;
import org.apache.flink.api.common.time.Time;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.runtime.state.memory.MemoryStateBackend;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.TableSchema;
import org.apache.flink.table.api.Types;
import org.apache.flink.table.api.java.StreamTableEnvironment;
import org.apache.flink.table.functions.TableFunction;
import org.apache.flink.table.sources.StreamTableSource;
import org.apache.flink.types.Row;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;

import java.io.IOException;
import java.net.URI;

/**
 * do tensorflow inference on mnist data.
 */
public class MnistJavaInference {

	public static final RowTypeInfo OUT_ROW_TYPE = new RowTypeInfo(
			new TypeInformation[] { Types.STRING(), Types.INT() },
			new String[] { "image_raw", "label" });
	public static final TFRExtractRowHelper.ScalarConverter[] CONVERTERS = new TFRExtractRowHelper.ScalarConverter[] {
			TFRExtractRowHelper.ScalarConverter.FIRST, TFRExtractRowHelper.ScalarConverter.ONE_HOT
	};

	private static final int NUM_WORKER = 2;
	private static final String CHECKPOINT_PATH = "/flink/checkpoints";
	private static final String SINK_OUTPUT_PATH = "/tmp/sink_output";
	private static final RestartStrategies.RestartStrategyConfiguration RESTART_STRATEGY =
			RestartStrategies.fixedDelayRestart(2, Time.seconds(5));

	protected static void setExampleCodingTypeRow(TFConfig config) {
		String[] names = { "image_raw", "org_label" };
		com.alibaba.flink.ml.operator.util.DataTypes[] types = { com.alibaba.flink.ml.operator.util.DataTypes.FLOAT_32_ARRAY,
				com.alibaba.flink.ml.operator.util.DataTypes.INT_64 };
		String str = ExampleCodingConfig.createExampleConfigStr(names, types,
				ExampleCodingConfig.ObjectType.ROW, MnistTFRPojo.class);
		config.getProperties().put(TFConstants.INPUT_TF_EXAMPLE_CONFIG, str);

		String[] namesOutput = { "real_label", "predicted_label" };
		com.alibaba.flink.ml.operator.util.DataTypes[] typesOutput = { com.alibaba.flink.ml.operator.util.DataTypes.INT_64,
				com.alibaba.flink.ml.operator.util.DataTypes.INT_64 };
		String strOutput = ExampleCodingConfig.createExampleConfigStr(namesOutput, typesOutput,
				ExampleCodingConfig.ObjectType.ROW, String.class);
		config.getProperties().put(TFConstants.OUTPUT_TF_EXAMPLE_CONFIG, strOutput);
		config.getProperties().put(MLConstants.ENCODING_CLASS, ExampleCoding.class.getCanonicalName());
		config.getProperties().put(MLConstants.DECODING_CLASS, ExampleCoding.class.getCanonicalName());
	}

	public static void main(String[] args) throws Exception {
		// parse arguments
		ArgumentParser parser = ArgumentParsers.newFor("mnist").build();
		parser.addArgument("--model-path").metavar("MODEL_PATH").dest("MODEL_PATH")
				.help("The path of saved model").required(true);
		parser.addArgument("--test-data").metavar("TEST_DATA").dest("TEST_DATA")
				.help("The path of mnist test data in TFR format").required(true);
		parser.addArgument("--hadoop-fs").metavar("HADOOP_FS").dest("HADOOP_FS")
				.help("The fs used as state backend").required(true);
		parser.addArgument("--num-records").metavar("NUM_RECORDS").dest("NUM_RECORDS")
				.help("The expected number of records to be processed").required(true);
		parser.addArgument("--batch-size").metavar("BATCH_SIZE").dest("BATCH_SIZE")
				.help("The batch size for inference").required(false);

		Namespace res = null;
		try {
			res = parser.parseArgs(args);
			System.out.println(res);
		} catch (ArgumentParserException e) {
			parser.handleError(e);
			System.exit(1);
		}

		String modelPath = res.getString("MODEL_PATH");
		String testData = res.getString("TEST_DATA");
		String batchSize = res.getString("BATCH_SIZE");
		if (StringUtils.isEmpty(batchSize)) {
			batchSize = "1";
		}
		String hadoopFS = res.getString("HADOOP_FS");
		long numRecords = Long.valueOf(res.getString("NUM_RECORDS"));

		// set required configs
		TFConfig tfConfig = new TFConfig(NUM_WORKER, 0, null, (String) null, "", "");
		tfConfig.addProperty(TFConstants.TF_INFERENCE_EXPORT_PATH, modelPath);
		tfConfig.addProperty(TFConstants.TF_INFERENCE_BATCH_SIZE, batchSize);
		tfConfig.addProperty(TFConstants.TF_INFERENCE_INPUT_TENSOR_NAMES, "image");
		tfConfig.addProperty(TFConstants.TF_INFERENCE_OUTPUT_TENSOR_NAMES, "prediction");
		tfConfig.addProperty(TFConstants.TF_INFERENCE_OUTPUT_ROW_FIELDS,
				Joiner.on(",").join(new String[] { "org_label", "prediction" }));

		Configuration hadoopConf = new Configuration();
		Path testDataPath = new Path(testData);
		FileSystem fs = testDataPath.getFileSystem(hadoopConf);
		FileStatus[] files = fs.listStatus(testDataPath);
		String[] paths = new String[files.length];
		for (int i = 0; i < paths.length; i++) {
			paths[i] = files[i].getPath().toString();
		}

		StreamExecutionEnvironment flinkEnv = StreamExecutionEnvironment.getExecutionEnvironment();
		StreamTableEnvironment tableEnv = TableEnvironment.getTableEnvironment(flinkEnv);
		String tfrTblName = "tfr_input_table";
		StreamTableSource<Row> tableSource = new DelayedTFRTableSourceStream(paths, 1, OUT_ROW_TYPE, CONVERTERS);
		tableEnv.registerTableSource(tfrTblName, tableSource);
		TableFunction extractFunc = new MnistTFRExtractRowForJavaFunction();
		String extFuncName = "tfr_extract";
		FlinkUtil.registerTableFunction(tableEnv, extFuncName, extractFunc);

		TableSchema extractTableSchema = TableSchema.builder()
				.field("image", Types.PRIMITIVE_ARRAY(Types.FLOAT()))
				.field("org_label", Types.LONG()).build();
		String outCols = Joiner.on(",").join(extractTableSchema.getFieldNames());
		String inCols = Joiner.on(",").join(tableSource.getTableSchema().getFieldNames());
		Table extracted = tableEnv.sqlQuery(String.format("select %s from %s, LATERAL TABLE(%s(%s)) as T(%s)",
				outCols, tfrTblName, extFuncName, inCols, outCols));
		TableSchema outSchema = TableSchema.builder().field("real_label", Types.LONG()).
				field("predicted_label", Types.LONG()).build();

		String checkPointURI = hadoopFS + CHECKPOINT_PATH;
		flinkEnv.setStateBackend(new MemoryStateBackend());

		// enable restart
		flinkEnv.setRestartStrategy(RESTART_STRATEGY);
		setExampleCodingTypeRow(tfConfig);

		Table predicted = TFUtils.inference(flinkEnv, tableEnv, extracted, tfConfig, outSchema);
		fs = new Path(checkPointURI).getFileSystem(hadoopConf);
		URI fsURI = fs.getUri();
		Path outDir = new Path(fsURI.getScheme(), fsURI.getAuthority(), SINK_OUTPUT_PATH);
		predicted.writeToSink(new LogTableStreamSink(new LogInferAccSink(outDir.toString())));
		// work around table env issue
		flinkEnv.execute();
		verifyNumRecords(fs, outDir, numRecords);
	}

	private static void verifyNumRecords(FileSystem fs, Path dir, long expected) throws IOException {
		FileStatus[] files = fs.listStatus(dir);
		long count = 0;
		for (FileStatus file : files) {
			try (FSDataInputStream input = fs.open(file.getPath())) {
				count += Long.valueOf(input.readUTF());
			}
		}
		Preconditions.checkState(expected == count, String.format(
				"Num records mismatch! Expected %d, Real %d", expected, count));
	}
}
