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
import org.junit.Assert;
import org.junit.Test;

public class FlinkJobParserTest {

	@Test
	public void parseFlinkJob() throws Exception{
		String json = FileUtils.readResourceFile("transform.json");
		JSONObject jsonObject = JsonUtils.loadJson(json);
		FlinkJobSpec flinkJobSpec = FlinkJobParser.parseFlinkJob(jsonObject);
		Assert.assertEquals(FlinkJobSpec.ExecutionMode.BATCH, flinkJobSpec.getExecutionMode());
		Assert.assertEquals(3, flinkJobSpec.getNodeMap().size());
		Assert.assertEquals(2, flinkJobSpec.getEdgeMap().size());
	}
}