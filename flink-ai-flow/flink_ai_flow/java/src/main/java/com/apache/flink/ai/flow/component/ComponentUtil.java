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

import org.apache.flink.table.api.Table;

import com.apache.flink.ai.flow.ComponentContext;
import com.apache.flink.ai.flow.node.BaseNode;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * util to
 */
public class ComponentUtil {
	private static Map<String, Component> componentMap = new HashMap<>();

	static {
		registerComponent("Transformer", new TransformerComponent());
		registerComponent("Example", new ExampleComponent());
		registerComponent("Predictor", new PredictorComponent());
		registerComponent("Trainer", new TrainerComponent());

	}
	public static void registerComponent(String key, Component component){
		componentMap.put(key, component);
	}

	public static Component getComponent(String key){
		return componentMap.getOrDefault(key, null);
	}

	public static List<Table> translate(ComponentContext context, BaseNode node, List<Table> inputs) throws Exception{
		Component component = getComponent(node.getType());
		return component.translate(context, node, inputs);
	}

}
