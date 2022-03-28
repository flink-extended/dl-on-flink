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
import org.flinkextended.flink.ml.cluster.rpc.AppMasterServer;
import org.flinkextended.flink.ml.operator.util.ColumnInfos;
import org.flinkextended.flink.ml.util.MLException;

import org.apache.flink.configuration.Configuration;
import org.apache.flink.util.Preconditions;

import java.io.IOException;

/** The InputFormat that runs Application Master Node. */
public class AMInputFormat extends AbstractNodeInputFormat<Void> {
    public AMInputFormat(ClusterConfig clusterConfig) {
        super(clusterConfig);
    }

    @Override
    public void configure(Configuration parameters) {}

    @Override
    public NodeInputSplit[] createInputSplits(int minNumSplits) throws IOException {
        Preconditions.checkState(
                minNumSplits <= 1,
                "AMNode cannot has more than one split but minimum of %s splits are desired",
                minNumSplits);
        return new NodeInputSplit[] {new NodeInputSplit(1, 0)};
    }

    @Override
    protected MLContext prepareMLContext(Integer nodeIndex) throws MLException {
        Preconditions.checkState(
                0 == nodeIndex, "AM cannot has index other than 0 but got %s", nodeIndex);
        return new MLContext(
                ExecutionMode.OTHER,
                "AM",
                nodeIndex,
                clusterConfig.getNodeTypeCntMap(),
                clusterConfig.getEntryFuncName(),
                clusterConfig.getProperties(),
                clusterConfig.getPythonVirtualEnvZipPath(),
                ColumnInfos.dummy().getNameToTypeMap());
    }

    @Override
    protected Runnable getNodeServerRunnable(MLContext mlContext) {
        return new AppMasterServer(mlContext);
    }

    @Override
    public boolean reachedEnd() throws IOException {
        return true;
    }
}
