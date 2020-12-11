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
package com.apache.flink.ai.flow.component;

import org.apache.flink.ml.api.core.Transformer;
import org.apache.flink.ml.api.misc.param.ParamInfoFactory;
import org.apache.flink.table.api.Table;

import com.apache.flink.ai.flow.ComponentContext;
import com.apache.flink.ai.flow.ConstantConfig;
import com.apache.flink.ai.flow.common.ReflectUtil;
import com.apache.flink.ai.flow.node.BaseNode;
import com.apache.flink.ai.flow.node.TransformerNode;

import java.util.ArrayList;
import java.util.List;

/**
 *  translate transformer node to code
 */
public class TransformerComponent implements Component{
	@Override
	public List<Table> translate(ComponentContext context, BaseNode node, List<Table> inputs) throws Exception {
		TransformerNode transformerNode = (TransformerNode) node;
		Transformer transformer = ReflectUtil.createInstance(transformerNode.getClassName());
		//set prams
		transformer.set(ParamInfoFactory.createParamInfo(ConstantConfig.EXECUTION_MODE_IS_STREAM, Boolean.class).build(),
				context.isStream());

		transformer.set(ParamInfoFactory.createParamInfo(ConstantConfig.NODE_CONFIG, TransformerNode.class).build(),
				transformerNode);
		Table result = transformer.transform(context.getTableEnv(), inputs.get(0));
		List<Table> resultList = new ArrayList<>();
		resultList.add(result);
		return resultList;
	}
}
