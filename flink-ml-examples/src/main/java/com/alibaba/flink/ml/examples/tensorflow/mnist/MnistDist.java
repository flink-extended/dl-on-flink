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

import com.alibaba.flink.ml.cluster.ExecutionMode;
import com.alibaba.flink.ml.cluster.node.MLContext;
import com.alibaba.flink.ml.tensorflow.client.TFConfig;
import com.alibaba.flink.ml.tensorflow.client.TFUtils;
import com.alibaba.flink.ml.util.MLConstants;
import com.google.common.base.Preconditions;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;
import org.apache.commons.lang.StringUtils;

import org.apache.flink.api.common.restartstrategy.RestartStrategies;
import org.apache.flink.api.common.time.Time;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.TableEnvironment;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * tensorflow train mnist data example.
 * train mnist data on flink cluster.
 */
public class MnistDist {

	private static final int NUM_PARTITIONS = 2;

	private Path trainPath;
	private Path outputPath;
	private String zkConnStr;
	private FileSystem fs;
	private final String envPath;
	private final String codePath;
	private final boolean withRestart;

	public enum EnvMode {
		StreamEnv,
		StreamTableEnv,
	}

	public MnistDist(String trainPath, String outputPath, String zkConnStr, String envPath, String codePath,
			boolean withRestart) {
		this.trainPath = new Path(trainPath);
		this.outputPath = new Path(outputPath);
		this.zkConnStr = zkConnStr;
		this.envPath = envPath;
		this.codePath = codePath;
		this.withRestart = withRestart;
	}

	private void close() {
		if (fs != null) {
			try {
				fs.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}

	public static void main(String[] args) throws Exception {
		//parse arguments
		ArgumentParser parser = ArgumentParsers.newFor("mnist").build();
		parser.addArgument("--mnist-files").metavar("MNIST_FILES").dest("MNIST_FILES")
				.help("A local path containing the downloaded mnist files.").required(true);
		parser.addArgument("--train-dir").metavar("TRAIN_DIR").dest("TRAIN_DIR")
				.help("The directory on Hadoop filesystem to store the MNIST train data.").setDefault("/mnist_data");
		parser.addArgument("--output-dir").metavar("OUTPUT_DIR").dest("OUTPUT_DIR")
				.help("The directory on Hadoop filesystem to store the train output data.").setDefault("/mnist_output");
		parser.addArgument("--mode").dest("MODE").type(EnvMode.class)
				.help("Use which execution environment to run (default: StreamEnv)").setDefault(EnvMode.StreamEnv);
		parser.addArgument("--zk-conn-str").metavar("ZK_CONN_STR").dest("ZK_CONN_STR");
		parser.addArgument("--setup").metavar("MNIST_SETUP_PYTHON").dest("SETUP_PY")
				.help("The python script to setup Mnist data set on HDFS ready for training.");
		parser.addArgument("--train").metavar("MNIST_TRAIN_PYTHON").dest("TRAIN_PY")
				.help("The python script to run TF train.");
		parser.addArgument("--envpath").metavar("ENVPATH").dest("ENVPATH")
				.help("The HDFS path to the virtual env zip file.");
		parser.addArgument("--code-path").metavar("codePath").dest("codePath")
				.help("Python scriptRunner implementation class name");
		parser.addArgument("--with-restart").metavar("WITH_RESTART").dest("WITH_RESTART")
				.help("Whether try to restart the job in case of failures");

		Namespace res = null;
		try {
			res = parser.parseArgs(args);
			System.out.println(res);
		} catch (ArgumentParserException e) {
			parser.handleError(e);
			System.exit(1);
		}

		String input = res.getString("MNIST_FILES");
		String trainDir = res.getString("TRAIN_DIR");
		String outputDir = res.getString("OUTPUT_DIR");
		String zkConnStr = res.getString("ZK_CONN_STR");
		String setupPy = res.getString("SETUP_PY");
		String trainPy = res.getString("TRAIN_PY");
		String envPath = res.getString("ENVPATH");
		String codePath = res.getString("codePath");
		boolean withRestart = "true".equalsIgnoreCase(res.getString("WITH_RESTART"));

		MnistDist mnist = new MnistDist(trainDir, outputDir, zkConnStr, envPath, codePath, withRestart);

		mnist.prepData(input, setupPy);

		EnvMode mode = res.get("MODE");
		switch (mode) {
			case StreamEnv:
				mnist.trainMnistDistStreamEnv(trainPy);
				break;
			case StreamTableEnv:
				mnist.trainMnistDistTableStreamEnv(trainPy);
				break;
		}
		mnist.close();
	}

	private void prepData(String input, String setupPy) throws Exception {
		//create Hadoop filesystem client
		fs = FileSystem.get(new Configuration());

		TFConfig config = new TFConfig(0, 0, null, (String) null, null, null);
		MLContext mlContext = new MLContext(ExecutionMode.TRAIN, config.getMlConfig(), "worker",
				0, null, null);
		mlContext.setEnvPath(envPath);
		MnistDataUtil.runMnistSetup(mlContext, setupPy, input, getRemotePath(trainPath), NUM_PARTITIONS);
	}

	private String getRemotePath(Path p) {
		return fs.getUri() + p.toString();
	}

	private TFConfig prepareTrain(String trainPy) throws Exception {
		Preconditions.checkState(!fs.exists(outputPath) || fs.delete(outputPath, true), "Cannot delete " + outputPath);

		Map<String, String> prop = new HashMap<>();
		prop.put("batch_size", "100");
		prop.put("epochs", "3");
		String mode = "train";
		prop.put("mode", mode);
		prop.put("input", getRemotePath(trainPath) + "/" + mode);
		prop.put("checkpoint_dir", getRemotePath(outputPath) + "/checkpoint");
		prop.put("export_dir", getRemotePath(outputPath) + "/model");

		if (zkConnStr != null && !zkConnStr.isEmpty()) {
			prop.put(MLConstants.CONFIG_STORAGE_TYPE, MLConstants.STORAGE_ZOOKEEPER);
			prop.put(MLConstants.CONFIG_ZOOKEEPER_CONNECT_STR, zkConnStr);
		}

		if (!StringUtils.isEmpty(codePath)) {
			prop.put(MLConstants.USE_DISTRIBUTE_CACHE, "false");
			prop.put(MLConstants.REMOTE_CODE_ZIP_FILE, codePath);
		}

		return new TFConfig(NUM_PARTITIONS, 1, prop, new String[] { trainPy }, "map_fun", envPath);
	}


	private void trainMnistDistStreamEnv(String trainPy) throws Exception {
		StreamExecutionEnvironment flinkEnv = StreamExecutionEnvironment.getExecutionEnvironment();
		if (withRestart) {
			flinkEnv.setRestartStrategy(restartStrategy());
		}
		TFConfig tfConfig = prepareTrain(trainPy);
		TFUtils.train(flinkEnv, null, tfConfig);
		flinkEnv.execute();
	}

	private void trainMnistDistTableStreamEnv(String trainPy) throws Exception {
		trainMnistTable(trainPy);
	}


	private void trainMnistTable(String trainPy) throws Exception {
		StreamExecutionEnvironment flinkEnv = StreamExecutionEnvironment.getExecutionEnvironment();
		TableEnvironment tableEnv = TableEnvironment.getTableEnvironment(flinkEnv);
		if (withRestart) {
			flinkEnv.setRestartStrategy(restartStrategy());
		}
		TFConfig tfConfig = prepareTrain(trainPy);
		TFUtils.train(flinkEnv, tableEnv, null, tfConfig, null);
		flinkEnv.execute();
	}

	private RestartStrategies.RestartStrategyConfiguration restartStrategy() {
		return RestartStrategies.fixedDelayRestart(2, Time.seconds(5));
	}

}
