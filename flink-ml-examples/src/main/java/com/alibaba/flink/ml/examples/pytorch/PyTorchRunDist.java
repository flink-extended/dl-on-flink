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

package com.alibaba.flink.ml.examples.pytorch;

import com.alibaba.flink.ml.pytorch.PyTorchConfig;
import com.alibaba.flink.ml.pytorch.PyTorchUtil;
import com.alibaba.flink.ml.util.MLConstants;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;
import org.apache.commons.lang.StringUtils;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.TableConfig;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.java.StreamTableEnvironment;

import java.util.HashMap;
import java.util.Map;

/**
 * run PyTorch all reduce test main class.
 * test machine learning framework PyTorch on flink stream and table api.
 */
public class PyTorchRunDist {

	private String zkConnStr;
	private final String envPath;
	private final String codePath;


	public PyTorchRunDist(String zkConnStr, String envPath, String codePath) {
		this.zkConnStr = zkConnStr;
		this.envPath = envPath;
		this.codePath = codePath;
	}

	public enum EnvMode {
		Stream,
		Table
	}

	public static void main(String[] args) throws Exception {
		//parse arguments
		ArgumentParser parser = ArgumentParsers.newFor("pytorch").build();
		parser.addArgument("--mode").dest("MODE").type(EnvMode.class)
				.help("Use which execution environment to run (default: StreamEnv)").setDefault(EnvMode.Stream);
		parser.addArgument("--zk-conn-str").metavar("ZK_CONN_STR").dest("ZK_CONN_STR");
		parser.addArgument("--script").metavar("SCRIPT").dest("SCRIPT")
				.help("The python script to run TF train.");
		parser.addArgument("--envpath").metavar("ENVPATH").dest("ENVPATH")
				.help("The HDFS path to the virtual env zip file.");
		parser.addArgument("--code-path").metavar("CODE_PATH").dest("CODE_PATH")
				.help("Python scriptRunner implementation class name");

		Namespace res = null;
		try {
			res = parser.parseArgs(args);
			System.out.println(res);
		} catch (ArgumentParserException e) {
			parser.handleError(e);
			System.exit(1);
		}

		String zkConnStr = res.getString("ZK_CONN_STR");
		String script = res.getString("SCRIPT");
		String envPath = res.getString("ENVPATH");
		String codePath = res.getString("CODE_PATH");

		PyTorchRunDist pytorchRunDist = new PyTorchRunDist(zkConnStr, envPath, codePath);

		EnvMode mode = res.get("MODE");
		switch (mode) {
			case Stream:
				pytorchRunDist.runStream(script);
				break;
			case Table:
				pytorchRunDist.runTable(script);
				break;
		}
	}

	private Map<String, String> createConfigProps() {
		Map<String, String> prop = new HashMap<>();
		if (zkConnStr != null && !zkConnStr.isEmpty()) {
			prop.put(MLConstants.CONFIG_STORAGE_TYPE, MLConstants.STORAGE_ZOOKEEPER);
			prop.put(MLConstants.CONFIG_ZOOKEEPER_CONNECT_STR, zkConnStr);
		}

		if (!StringUtils.isEmpty(codePath)) {
			prop.put(MLConstants.USE_DISTRIBUTE_CACHE, "false");
			prop.put(MLConstants.REMOTE_CODE_ZIP_FILE, codePath);
		}
		return prop;
	}

	private void runStream(String script) throws Exception {
		Map<String, String> prop = createConfigProps();
		PyTorchConfig pytorchConfig = new PyTorchConfig(2, prop,
				script, "map_func", envPath);
		StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
		PyTorchUtil.train(streamEnv, null, pytorchConfig, null);
		System.out.println("before submit job");
		streamEnv.execute("pytorch stream");
	}

	private void runTable(String script) throws Exception {
		Map<String, String> prop = createConfigProps();
		PyTorchConfig pytorchConfig = new PyTorchConfig(3, prop,
				script, "map_func", envPath);
		StreamExecutionEnvironment streamEnv = StreamExecutionEnvironment.getExecutionEnvironment();
		TableEnvironment tableEnv = StreamTableEnvironment.getTableEnvironment(streamEnv, TableConfig.DEFAULT());
		PyTorchUtil.train(streamEnv, tableEnv, null, pytorchConfig, null);
		streamEnv.execute("pytorch table");
	}

}
