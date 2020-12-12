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

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.EnvironmentSettings;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;

import java.util.concurrent.ExecutionException;

import static org.apache.flink.table.api.Expressions.$;

public class TestCsv {
	public static void main(String[] args) throws ExecutionException, InterruptedException {
		EnvironmentSettings fsSettings = EnvironmentSettings.newInstance().useBlinkPlanner()
				.inStreamingMode().build();
		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		TableEnvironment tableEnv = StreamTableEnvironment.create(env, fsSettings);
		env.setParallelism(1);
		StatementSet statementSet = tableEnv.createStatementSet();
		tableEnv.executeSql("CREATE TABLE input_table (a STRING, b STRING, c STRING) WITH ('connector' = 'filesystem',\n" +
				"                'path' = 'file:///Users/chenwuchao/code/ali/ai_flow/flink_ai_flow/java/src/test/resources/test.csv',\n" +
				"                'format' = 'csv'                  \n" +
				"                )");
		tableEnv.executeSql("CREATE TABLE output_table (aa STRING, bb STRING) WITH ('connector' = 'filesystem',\n" +
				"                'path' = 'file:///Users/chenwuchao/code/ali/ai_flow/flink_ai_flow/java/src/test/resources/output.csv',\n" +
				"                'format' = 'csv'                \n" +
				"                )");
		Table output = tableEnv.from("input_table").select($("a"), $("b"));
		statementSet.addInsert("output_table", output);
		statementSet.execute().getJobClient().get()
				.getJobExecutionResult(Thread.currentThread().getContextClassLoader()).get();
	}
}
