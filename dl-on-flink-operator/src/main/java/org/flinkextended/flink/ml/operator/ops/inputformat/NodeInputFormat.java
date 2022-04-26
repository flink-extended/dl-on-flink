/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.flinkextended.flink.ml.operator.ops.inputformat;

import org.flinkextended.flink.ml.cluster.ClusterConfig;
import org.flinkextended.flink.ml.cluster.ExecutionMode;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.rpc.NodeServer;
import org.flinkextended.flink.ml.operator.ops.PythonEnvironmentManager;
import org.flinkextended.flink.ml.operator.ops.ResourcesUtils;
import org.flinkextended.flink.ml.operator.util.ColumnInfos;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.MLException;

import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.operators.StreamingRuntimeContext;
import org.apache.flink.util.Preconditions;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/** The InputFormat that runs node with node types except Application Master. */
public class NodeInputFormat<OUT> extends AbstractNodeInputFormat<OUT> {

    private final String nodeType;
    private final Configuration flinkConfig;

    public NodeInputFormat(String nodeType, ClusterConfig clusterConfig) {
        this(nodeType, clusterConfig, new Configuration());
    }

    public NodeInputFormat(
            String nodeType, ClusterConfig clusterConfig, Configuration flinkConfig) {
        super(clusterConfig);
        this.nodeType = nodeType;
        this.flinkConfig = flinkConfig;
    }

    @Override
    public void configure(Configuration configuration) {}

    @Override
    public NodeInputSplit[] createInputSplits(int minNumSplits) throws IOException {
        final Integer nodeCnt = clusterConfig.getNodeTypeCntMap().get(nodeType);
        Preconditions.checkState(
                nodeCnt >= minNumSplits,
                "The required minimum number of splits: %s "
                        + "is greater than the number of node: %s with type %s",
                minNumSplits,
                nodeCnt,
                nodeType);
        NodeInputSplit[] inputSplits = new NodeInputSplit[nodeCnt];
        for (int i = 0; i < nodeCnt; i++) {
            inputSplits[i] = new NodeInputSplit(nodeCnt, i);
        }
        return inputSplits;
    }

    @Override
    protected MLContext prepareMLContext(Integer nodeIndex) throws MLException {
        final PythonEnvironmentManager pythonEnvironmentManager =
                new PythonEnvironmentManager(clusterConfig, flinkConfig);
        try {
            pythonEnvironmentManager.open((StreamingRuntimeContext) getRuntimeContext());
        } catch (Exception e) {
            throw new MLException("Fail to open PythonEnvironmentManager", e);
        }

        Map<String, String> properties = new HashMap<>(clusterConfig.getProperties());
        properties.put(MLConstants.GPU_INFO, ResourcesUtils.parseGpuInfo(getRuntimeContext()));
        properties.putAll(pythonEnvironmentManager.getPythonEnvProperties());

        return new MLContext(
                ExecutionMode.OTHER,
                nodeType,
                nodeIndex,
                clusterConfig.getNodeTypeCntMap(),
                clusterConfig.getEntryFuncName(),
                properties,
                clusterConfig.getPythonVirtualEnvZipPath(),
                ColumnInfos.dummy().getNameToTypeMap());
    }

    @Override
    protected Runnable getNodeServerRunnable(MLContext mlContext) {
        return new NodeServer(mlContext, nodeType);
    }

    public String getNodeType() {
        return nodeType;
    }
}
