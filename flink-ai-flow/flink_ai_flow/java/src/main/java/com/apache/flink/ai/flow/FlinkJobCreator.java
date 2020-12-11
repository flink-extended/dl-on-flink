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

import org.apache.flink.table.api.Table;

import com.apache.flink.ai.flow.component.ComponentUtil;
import com.apache.flink.ai.flow.edge.DataEdge;
import com.apache.flink.ai.flow.node.BaseNode;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * create flink job by FlinkJobSpec object
 */
public class FlinkJobCreator {

	private static boolean canCompile(BaseNode node, Map<String, List<Table>>returnMap,
			Map<String, List<DataEdge>> edges){
		if (edges.containsKey(node.getId())) {
			List<DataEdge> edgeList = edges.get(node.getId());
			for(DataEdge dataEdge: edgeList){
				if(!returnMap.containsKey(dataEdge.getTarget_id())){
					return false;
				}
			}
			return true;
		}else {
			return true;
		}
	}
	public static void createJob(ComponentContext context, FlinkJobSpec jobSpec)throws Exception{
		Map<String, List<Table>> returnMap = new HashMap<>();
		List<BaseNode> allNodes = new ArrayList<>(jobSpec.getNodeMap().values());
		Map<String, List<DataEdge>> edges = jobSpec.getEdgeMap();
		int size = allNodes.size();
		while (size > 0) {
			List<Integer> processedNodes = new ArrayList<>();
			for (int i = 0; i < size; i++) {
				BaseNode node = allNodes.get(i);
				if(canCompile(node, returnMap, edges)){
					//build component inputs
					List<Table> inputList = new ArrayList<>();
					if(edges.containsKey(node.getId())){
						for(DataEdge dataEdge: edges.get(node.getId())){
							Table tmp = returnMap.get(dataEdge.getTarget_id()).get(dataEdge.getPort());
							inputList.add(tmp);
						}
					}
					List<Table> result = ComponentUtil.translate(context, node, inputList);
					if(null != result) {
						returnMap.put(node.getId(), result);
					}
					processedNodes.add(i);
				}
			}
			// some node can not process so throw exception
			if(processedNodes.size() <= 0){
				StringBuilder sb = new StringBuilder();
				for (BaseNode node: allNodes){
					sb.append(node.getId()).append(",");
				}
				sb.deleteCharAt(sb.lastIndexOf(","));
				throw new Exception("can not compile nodes " + sb.toString());
			}
			// remove processed node
			for(int i = processedNodes.size() -1; i >=0; i--){
				allNodes.remove(processedNodes.get(i).intValue());
			}
			size = allNodes.size();
		}

	}
}
