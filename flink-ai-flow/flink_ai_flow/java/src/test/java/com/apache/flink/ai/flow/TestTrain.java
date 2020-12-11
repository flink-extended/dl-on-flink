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

import org.apache.flink.ml.api.core.Estimator;
import org.apache.flink.ml.api.core.Model;
import org.apache.flink.ml.api.misc.param.ParamInfoFactory;
import org.apache.flink.ml.api.misc.param.Params;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;

import com.apache.flink.ai.flow.node.TrainerNode;

public class TestTrain implements Estimator<TestTrain, TestTrain.SimpleModel> {
	private ComponentContext componentContext;
	public TestTrain(ComponentContext componentContext) {
		this.componentContext = componentContext;
	}

	@Override
	public SimpleModel fit(TableEnvironment tEnv, Table input) {
		TrainerNode trainerNode = get(
				ParamInfoFactory.createParamInfo(ConstantConfig.NODE_CONFIG, TrainerNode.class).build());
		StatementSet statementSet = componentContext.getStatementSet();
		tEnv.executeSql("CREATE TABLE output_table (aa STRING, bb STRING, cc STRING) WITH ('connector' = 'print')");
		statementSet.addInsert("output_table", input);
		return new SimpleModel();
	}

	public static class SimpleModel implements Model<SimpleModel>{

		@Override
		public Table transform(TableEnvironment tEnv, Table input) {
			return null;
		}

		@Override
		public Params getParams() {
			return null;
		}
	}

	private Params params = new Params();


	@Override
	public Params getParams() {
		return params;
	}
}
