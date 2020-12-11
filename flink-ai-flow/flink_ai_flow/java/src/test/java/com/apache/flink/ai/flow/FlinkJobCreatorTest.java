/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package com.apache.flink.ai.flow;

import org.apache.flink.api.java.ExecutionEnvironment;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.EnvironmentSettings;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.api.config.ExecutionConfigOptions;

import com.alibaba.fastjson.JSONObject;
import com.alibaba.flink.ml.lib.tensorflow.util.ShellExec;
import com.apache.flink.ai.flow.common.FileUtils;
import com.apache.flink.ai.flow.common.JsonUtils;
import org.junit.Assert;
import org.junit.Test;

import java.io.File;

import static com.apache.flink.ai.flow.ConstantConfig.DDL_STRING;


public class FlinkJobCreatorTest {


	public void createTransformJob(boolean isStream) throws Exception{
		String currentPath = FlinkJobCreatorTest.class.getClassLoader().getResource("").getPath();
		String inputFile = "file://" + currentPath + "test.csv";
		String outputDir = "file://" + currentPath + "output";
		if(FileUtils.exist(new File(outputDir))) {
			FileUtils.deleteDir(new File(outputDir));
		}
		String json = FileUtils.readResourceFile("transform.json");
		JSONObject jsonObject = JsonUtils.loadJson(json);
		JSONObject nodes = jsonObject.getJSONObject("ai_graph").getJSONObject("nodes");
		String inputDdl = nodes.getJSONObject("Example_0").getJSONObject("execute_properties")
				.getJSONObject("batch_properties").getString(DDL_STRING);
		nodes.getJSONObject("Example_0").getJSONObject("execute_properties")
				.getJSONObject("batch_properties").put(DDL_STRING, inputDdl.replace("INPUT", inputFile));

		nodes.getJSONObject("Example_0").getJSONObject("execute_properties")
				.getJSONObject("stream_properties").put(DDL_STRING, inputDdl.replace("INPUT", inputFile));

		String outputDdl = nodes.getJSONObject("Example_1").getJSONObject("execute_properties")
				.getJSONObject("batch_properties").getString(DDL_STRING);
		nodes.getJSONObject("Example_1").getJSONObject("execute_properties")
				.getJSONObject("batch_properties").put(DDL_STRING, outputDdl.replace("OUTPUT", outputDir));
		nodes.getJSONObject("Example_1").getJSONObject("execute_properties")
				.getJSONObject("stream_properties").put(DDL_STRING, outputDdl.replace("OUTPUT", outputDir));

		FlinkJobSpec flinkJobSpec = FlinkJobParser.parseFlinkJob(jsonObject);
		ComponentContext context;
		TableEnvironment tableEnv;
		StatementSet statementSet;
		RunEnv runEnv = new RunEnv(isStream, flinkJobSpec).invoke();
		context = runEnv.getContext();
		tableEnv = runEnv.getTableEnv();
		statementSet = context.getStatementSet();
		System.out.println(TestTransformer.class.getCanonicalName());
		FlinkJobCreator.createJob(context,flinkJobSpec);
		statementSet.execute().getJobClient().get()
				.getJobExecutionResult(Thread.currentThread().getContextClassLoader()).get();
	}
	@Test
	public void streamTransformJob() throws Exception{
		createTransformJob(true);
	}

	@Test
	public void batchTransformJob() throws Exception{
		createTransformJob(false);
	}

	public void createPredictJob(boolean isStream) throws Exception{

		String pythonScriptPath = this.getClass().getClassLoader().getResource("").getPath();
		String pythonScript = pythonScriptPath + "predict.py";
		String modelDir = this.getClass().getClassLoader().getResource("").getPath()+"/export2";
		File f = new File(modelDir);
		if(!f.exists()) {
			Assert.assertTrue(ShellExec.run("python " + pythonScript));
		}

		String currentPath = FlinkJobCreatorTest.class.getClassLoader().getResource("").getPath();
		String inputFile = currentPath + "test.csv";
		String outputDir = currentPath + "/predict_output";
		if(FileUtils.exist(new File(outputDir))) {
			FileUtils.deleteDir(new File(outputDir));
		}
		String json = FileUtils.readResourceFile("predict.json");
		JSONObject jsonObject = JsonUtils.loadJson(json);
		JSONObject nodes = jsonObject.getJSONObject("ai_graph").getJSONObject("nodes");
		String inputDdl = nodes.getJSONObject("Example_0").getJSONObject("execute_properties")
				.getJSONObject("batch_properties").getString(DDL_STRING);
		nodes.getJSONObject("Example_0").getJSONObject("execute_properties")
				.getJSONObject("batch_properties").put(DDL_STRING, inputDdl.replace("INPUT", inputFile));

		nodes.getJSONObject("Example_0").getJSONObject("execute_properties")
				.getJSONObject("stream_properties").put(DDL_STRING, inputDdl.replace("INPUT", inputFile));

		String outputDdl = nodes.getJSONObject("Example_1").getJSONObject("execute_properties")
				.getJSONObject("batch_properties").getString(DDL_STRING);
		nodes.getJSONObject("Example_1").getJSONObject("execute_properties")
				.getJSONObject("batch_properties").put(DDL_STRING, outputDdl.replace("OUTPUT", outputDir));
		nodes.getJSONObject("Example_1").getJSONObject("execute_properties")
				.getJSONObject("stream_properties").put(DDL_STRING, outputDdl.replace("OUTPUT", outputDir));
		nodes.getJSONObject("Predictor_0").getJSONObject("model_version").put("model_path", modelDir);
		FlinkJobSpec flinkJobSpec = FlinkJobParser.parseFlinkJob(jsonObject);
		ComponentContext context;
		StatementSet statementSet;
		RunEnv runEnv = new RunEnv(isStream, flinkJobSpec).invoke();
		context = runEnv.getContext();
		statementSet = context.getStatementSet();
		System.out.println(TestPredict.class.getCanonicalName());
		FlinkJobCreator.createJob(context,flinkJobSpec);
		statementSet.execute().getJobClient().get()
				.getJobExecutionResult(Thread.currentThread().getContextClassLoader()).get();
	}
	@Test
	public void streamPredictJob() throws Exception{
		createPredictJob(true);
	}

	@Test
	public void batchPredictJob() throws Exception{
		createPredictJob(false);
	}

	public void createTrainJob(boolean isStream) throws Exception{
		String currentPath = FlinkJobCreatorTest.class.getClassLoader().getResource("").getPath();
		String inputFile = currentPath + "test.csv";
		String json = FileUtils.readResourceFile("train.json");
		JSONObject jsonObject = JsonUtils.loadJson(json);
		JSONObject nodes = jsonObject.getJSONObject("ai_graph").getJSONObject("nodes");
		String inputDdl = nodes.getJSONObject("Example_0").getJSONObject("execute_properties")
				.getJSONObject("batch_properties").getString(DDL_STRING);
		nodes.getJSONObject("Example_0").getJSONObject("execute_properties")
				.getJSONObject("batch_properties").put(DDL_STRING, inputDdl.replace("INPUT", inputFile));

		nodes.getJSONObject("Example_0").getJSONObject("execute_properties")
				.getJSONObject("stream_properties").put(DDL_STRING, inputDdl.replace("INPUT", inputFile));
		FlinkJobSpec flinkJobSpec = FlinkJobParser.parseFlinkJob(jsonObject);
		ComponentContext context;
		TableEnvironment tableEnv;
		RunEnv runEnv = new RunEnv(isStream, flinkJobSpec).invoke();
		context = runEnv.getContext();
		StatementSet statementSet = context.getStatementSet();
		FlinkJobCreator.createJob(context,flinkJobSpec);
		statementSet.execute().getJobClient().get()
				.getJobExecutionResult(Thread.currentThread().getContextClassLoader()).get();
	}

	@Test
	public void batchTrainJob() throws Exception{
		createTrainJob(false);
	}

	@Test
	public void streamTrainJob() throws Exception{
		createTrainJob(true);
	}
	private class RunEnv {
		private boolean isStream;
		private ComponentContext context;
		private TableEnvironment tableEnv;
		private FlinkJobSpec flinkJobSpec;

		public RunEnv(boolean isStream, FlinkJobSpec flinkJobSpec) {
			this.isStream = isStream;
			this.flinkJobSpec = flinkJobSpec;
		}

		public ComponentContext getContext() {
			return context;
		}

		public TableEnvironment getTableEnv() {
			return tableEnv;
		}

		public RunEnv invoke() {
			if(isStream){
				EnvironmentSettings fsSettings = EnvironmentSettings.newInstance().useBlinkPlanner()
						.inStreamingMode().build();
				StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
				tableEnv = StreamTableEnvironment.create(env, fsSettings);
				env.setParallelism(1);
				StatementSet statementSet = tableEnv.createStatementSet();
				context = new ComponentContext(env, tableEnv, statementSet, flinkJobSpec.getWorkflowExecutionId());
			}else {
				final ExecutionEnvironment env = null;
				EnvironmentSettings bbSettings = EnvironmentSettings.newInstance().useBlinkPlanner()
						.inBatchMode().build();
				tableEnv = TableEnvironment.create(bbSettings);
				tableEnv.getConfig().getConfiguration()
						.set(ExecutionConfigOptions.TABLE_EXEC_RESOURCE_DEFAULT_PARALLELISM, 1);
				StatementSet statementSet = tableEnv.createStatementSet();
				context = new ComponentContext(env, tableEnv, statementSet, flinkJobSpec.getWorkflowExecutionId());
			}
			return this;
		}
	}
}