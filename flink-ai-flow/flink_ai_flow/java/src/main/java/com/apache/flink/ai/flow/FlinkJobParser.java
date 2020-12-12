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

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.apache.flink.ai.flow.edge.DataEdge;
import com.apache.flink.ai.flow.node.BaseNode;
import com.apache.flink.ai.flow.node.NodeParserUtil;
import org.apache.commons.lang3.StringUtils;

import java.util.ArrayList;
import java.util.List;

/**
 * parse FlinkJob from josn to java class FlinkJobSpec
 */
public class FlinkJobParser {

    public static FlinkJobSpec parseFlinkJob(JSONObject jsonObject) throws Exception {
        FlinkJobSpec flinkJobSpec = new FlinkJobSpec();
        JSONObject nodes = jsonObject.getJSONObject("ai_graph").getJSONObject("nodes");
        // add node to job spec
        for (String key : nodes.keySet()) {
            JSONObject nodeJson = nodes.getJSONObject(key);
            BaseNode node = NodeParserUtil.parseNode(nodeJson);
            flinkJobSpec.addNode(node);
        }

        // add edge to job spec
        JSONObject edges = jsonObject.getJSONObject("ai_graph").getJSONObject("edges");
        for (String nid : edges.keySet()) {
            JSONArray edgeArray = edges.getJSONArray(nid);
            List<DataEdge> edgeList = new ArrayList<>();
            for (int i = 0; i < edgeArray.size(); i++) {
                JSONObject edgeJson = edgeArray.getJSONObject(i);
                DataEdge edge = new DataEdge(edgeJson.getString("source_node_id"),
                        edgeJson.getString("target_node_id"), edgeJson.getInteger("port"));
                edgeList.add(edge);
            }
            flinkJobSpec.addEdges(nid, edgeList);
        }
        String execMode = jsonObject.getJSONObject("job_config").getString("exec_mode");
        if (StringUtils.isEmpty(execMode)) {
            flinkJobSpec.setExecutionMode(FlinkJobSpec.ExecutionMode.valueOf(
                    jsonObject.getJSONObject("job_context").getString("execution_mode")));
        } else {
            flinkJobSpec.setExecutionMode(FlinkJobSpec.ExecutionMode.valueOf(execMode));
        }
        flinkJobSpec.setWorkflowExecutionId(jsonObject.getJSONObject("job_context").getLong("workflow_execution_id"));
        flinkJobSpec.setName(jsonObject.getString("name"));
        flinkJobSpec.setFlinkEnvironment(jsonObject.getJSONObject("job_config").getJSONObject("properties").getString("flink_environment"));
        return flinkJobSpec;
    }
}