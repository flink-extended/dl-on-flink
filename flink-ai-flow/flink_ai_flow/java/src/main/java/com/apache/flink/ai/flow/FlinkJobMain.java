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

import com.alibaba.fastjson.JSONObject;
import com.apache.flink.ai.flow.common.FileUtils;
import com.apache.flink.ai.flow.common.JsonUtils;
import com.apache.flink.ai.flow.common.ReflectUtil;
import com.apache.flink.ai.flow.environment.DefaultEnvironment;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;
import org.apache.commons.lang3.StringUtils;
import org.apache.flink.api.java.ExecutionEnvironment;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.TableEnvironment;

public class FlinkJobMain {

    public static void main(String[] args) throws Exception {
        ArgumentParser parser = ArgumentParsers.newFor("FlinkJob").build();
        parser.addArgument("--execution-config").metavar("EXECUTION_CONFIG").dest("EXECUTION_CONFIG")
                .help("a execution configuration file define flink job.").required(true);
        Namespace namespace = null;
        try {
            namespace = parser.parseArgs(args);
        } catch (ArgumentParserException e) {
            parser.handleError(e);
            System.exit(1);
        }
        String executionConfig = namespace.getString("EXECUTION_CONFIG");
        String jsonString = FileUtils.readFile(executionConfig);
        JSONObject jsonObject = JsonUtils.loadJson(jsonString);
        runFlinkJob(jsonObject);
    }

    public static void runFlinkJob(JSONObject jsonObject) throws Exception {
        FlinkJobSpec flinkJobSpec = FlinkJobParser.parseFlinkJob(jsonObject);
        FlinkEnvironment flinkEnvironment;
        try {
            if (StringUtils.isEmpty(flinkJobSpec.getFlinkEnvironment())) {
                flinkEnvironment = new DefaultEnvironment();
            } else {
                flinkEnvironment = ReflectUtil.createInstance(flinkJobSpec.getFlinkEnvironment());
            }
        } catch (Exception e) {
            flinkEnvironment = new DefaultEnvironment();
        }
        TableEnvironment tableEnv;
        StatementSet statementSet;
        if (flinkJobSpec.getExecutionMode() == FlinkJobSpec.ExecutionMode.BATCH) {
            ExecutionEnvironment env = flinkEnvironment.getExecutionEnvironment();
            tableEnv = flinkEnvironment.getBatchTableEnvironment();
            statementSet = tableEnv.createStatementSet();
            ComponentContext context = new ComponentContext(env, tableEnv, statementSet,
                    flinkJobSpec.getWorkflowExecutionId());
            FlinkJobCreator.createJob(context, flinkJobSpec);
        } else {
            StreamExecutionEnvironment env = flinkEnvironment.getStreamExecutionEnvironment();
            tableEnv = flinkEnvironment.getStreamTableEnvironment();
            statementSet = tableEnv.createStatementSet();
            ComponentContext context = new ComponentContext(env, tableEnv, statementSet,
                    flinkJobSpec.getWorkflowExecutionId());
            FlinkJobCreator.createJob(context, flinkJobSpec);
        }
        statementSet.execute().getJobClient().get()
                .getJobExecutionResult(Thread.currentThread().getContextClassLoader()).get();
    }
}