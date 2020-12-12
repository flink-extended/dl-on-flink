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

import com.apache.flink.ai.flow.edge.DataEdge;
import com.apache.flink.ai.flow.node.BaseNode;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class FlinkJobSpec {

    private String name;
    private ExecutionMode executionMode;
    private Long workflowExecutionId;
    private String flinkEnvironment;
    private Map<String, BaseNode> nodeMap = new HashMap<>();
    private Map<String, List<DataEdge>> edgeMap = new HashMap<>();

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public ExecutionMode getExecutionMode() {
        return executionMode;
    }

    public void setExecutionMode(ExecutionMode executionMode) {
        this.executionMode = executionMode;
    }

    public Long getWorkflowExecutionId() {
        return workflowExecutionId;
    }

    public void setWorkflowExecutionId(Long workflowExecutionId) {
        this.workflowExecutionId = workflowExecutionId;
    }

    public String getFlinkEnvironment() {
        return flinkEnvironment;
    }

    public void setFlinkEnvironment(String flinkEnvironment) {
        this.flinkEnvironment = flinkEnvironment;
    }

    public void addNode(BaseNode node) {
        this.nodeMap.put(node.getId(), node);
    }

    public void addEdges(String nodeId, List<DataEdge> edges) {
        this.edgeMap.put(nodeId, edges);
    }

    public Map<String, BaseNode> getNodeMap() {
        return nodeMap;
    }

    public Map<String, List<DataEdge>> getEdgeMap() {
        return edgeMap;
    }

    public enum ExecutionMode {
        BATCH,
        STREAM
    }
}