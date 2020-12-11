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

import org.apache.flink.ml.api.core.Transformer;
import org.apache.flink.ml.api.misc.param.ParamInfoFactory;
import org.apache.flink.ml.api.misc.param.Params;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.bridge.java.BatchTableEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;

import com.alibaba.flink.ml.lib.tensorflow.TFInferenceUDTF;
import com.apache.flink.ai.flow.node.PredictorNode;

import java.util.Properties;
import static org.apache.flink.table.api.Expressions.$;
import static org.apache.flink.table.api.Expressions.call;

public class TestPredict implements Transformer<TestPredict> {
	private Params params = new Params();

	@Override
	public Table transform(TableEnvironment tEnv, Table input) {
		PredictorNode predictorNode = get(
				ParamInfoFactory.createParamInfo(ConstantConfig.NODE_CONFIG, PredictorNode.class).build());
		String modelDir = "file://" + predictorNode.getModelVersionMeta().getVersionUri();
		String inputNames = "a,b,c";
		String inputTypes = "DT_INT32,DT_INT32,DT_INT32";
		String inputRanks = "0,0,0";
		String outputNames = "aa, cc";
		String outputTypes = "DT_INT32,DT_INT32";
		String outputRanks = "0,0";
		TFInferenceUDTF predictUDTF = new TFInferenceUDTF(modelDir, inputNames, inputTypes, inputRanks,
				outputNames, outputTypes, outputRanks,
				new Properties(), 2);
		boolean isStream = get(
				ParamInfoFactory.createParamInfo(ConstantConfig.EXECUTION_MODE_IS_STREAM, Boolean.class).build());
		if(isStream) {
			StreamTableEnvironment streamTableEnvironment = (StreamTableEnvironment) tEnv;
			streamTableEnvironment.registerFunction("predict", predictUDTF);
		}else {
			BatchTableEnvironment batchTableEnvironment = (BatchTableEnvironment) tEnv;
			batchTableEnvironment.registerFunction("predict", predictUDTF);
		}
		return input.joinLateral("predict(a, b, c) as (aa, cc)").select("aa, cc");
	}

	@Override
	public Params getParams() {
		return params;
	}
}
