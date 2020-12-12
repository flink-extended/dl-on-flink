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
package com.apache.flink.ai.flow.node;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.apache.flink.ai.flow.common.FileUtils;
import com.apache.flink.ai.flow.common.JsonUtils;
import org.junit.Assert;
import org.junit.Test;

public class NodeParserUtilTest {

	@Test
	public void parseNode() throws Exception{
		String json = FileUtils.readResourceFile("transform.json");
		JSONObject jsonObject = JsonUtils.loadJson(json);
		JSONObject nodes = jsonObject.getJSONObject("ai_graph").getJSONObject("nodes");
		JSONObject node0 = nodes.getJSONObject("Example_0");
		BaseNode baseNode = NodeParserUtil.parseNode(node0);
		Assert.assertEquals(ExampleNode.class, baseNode.getClass());
		ExampleNode exampleNode = (ExampleNode) baseNode;
		Assert.assertEquals("Example_0", exampleNode.getId());
	}

	@Test
	public void parsePredictNode() throws Exception{
		String json = FileUtils.readResourceFile("predict.json");
		JSONObject jsonObject = JsonUtils.loadJson(json);
		JSONObject nodes = jsonObject.getJSONObject("ai_graph").getJSONObject("nodes");
		JSONObject node1 = nodes.getJSONObject("Predictor_0");
		BaseNode baseNode = NodeParserUtil.parseNode(node1);
		Assert.assertEquals(PredictorNode.class, baseNode.getClass());
		PredictorNode predictorNode = (PredictorNode) baseNode;
		Assert.assertEquals("Predictor_0", predictorNode.getId());
	}
}