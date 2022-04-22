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

package org.flinkextended.flink.ml.tensorflow.client;

import org.flinkextended.flink.ml.cluster.ClusterConfig;
import org.flinkextended.flink.ml.operator.coding.RowCSVCoding;
import org.flinkextended.flink.ml.tensorflow.cluster.TFAMStateMachineImpl;
import org.flinkextended.flink.ml.tensorflow.cluster.node.runner.TFMLRunner;
import org.flinkextended.flink.ml.tensorflow.data.TFRecordReaderImpl;
import org.flinkextended.flink.ml.tensorflow.data.TFRecordWriterImpl;
import org.flinkextended.flink.ml.tensorflow.util.TFConstants;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.util.Preconditions;

import javax.annotation.Nullable;

import java.util.Map;
import java.util.Set;

/**
 * A config for the Tensorflow cluster. It extends the {@link ClusterConfig} to provides some higher
 * level methods to config the Tensorflow cluster.
 */
public class TFClusterConfig extends ClusterConfig {

    public static final String WORKER_NODE_TYPE = "worker";
    public static final String PS_NODE_TYPE = "ps";
    public static final String TENSORBOARD_NODE_TYPE = "tensorboard";

    private TFClusterConfig(
            Map<String, Integer> nodeTypeCntMap,
            Map<String, String> properties,
            Set<String> pythonFilePaths,
            String entryPythonFilePath,
            String entryFuncName,
            @Nullable String pythonVirtualEnvZipPath) {
        super(
                nodeTypeCntMap,
                properties,
                pythonFilePaths,
                entryPythonFilePath,
                entryFuncName,
                pythonVirtualEnvZipPath);
    }

    /** Create a new {@link Builder} for {@link TFClusterConfig}. */
    public static Builder newBuilder() {
        return new Builder();
    }

    /**
     * Create a new {@link ClusterConfig.Builder} from the current immutable {@link ClusterConfig}.
     */
    public Builder toBuilder() {
        return new Builder(this);
    }

    /** Builder for {@link TFClusterConfig}. */
    public static class Builder extends ClusterConfig.Builder<Builder> {

        private Builder() {
            // Default properties for Tensorflow cluster config.
            setProperty(MLConstants.ML_RUNNER_CLASS, TFMLRunner.class.getName());
            setProperty(MLConstants.AM_STATE_MACHINE_CLASS, TFAMStateMachineImpl.class.getName());
            setProperty(MLConstants.RECORD_READER_CLASS, TFRecordReaderImpl.class.getName());
            setProperty(MLConstants.RECORD_WRITER_CLASS, TFRecordWriterImpl.class.getName());
            setProperty(MLConstants.ENCODING_CLASS, RowCSVCoding.class.getName());
            setProperty(MLConstants.DECODING_CLASS, RowCSVCoding.class.getName());
        }

        private Builder(TFClusterConfig tfClusterConfig) {
            super(tfClusterConfig);
        }

        /**
         * Set the number of workers in the Tensorflow cluster.
         *
         * <p>The node type of the worker nodes is "worker", i.e., the return value of
         * dl_on_flink_framework.context.Context.get_node_type is "worker".
         *
         * @param count Number of workers.
         */
        public Builder setWorkerCount(Integer count) {
            addNodeType(WORKER_NODE_TYPE, count);
            return this;
        }

        /**
         * Set the number of parameter servers in the Tensorflow cluster.
         *
         * <p>The node type of the worker nodes is "ps", i.e., the return value of
         * dl_on_flink_framework.context.Context.get_node_type is "ps".
         *
         * @param count Number of parameter servers.
         */
        public Builder setPsCount(Integer count) {
            addNodeType(PS_NODE_TYPE, count);
            return this;
        }

        /**
         * Specify whether the worker with index 0 should be designated as the chief.
         *
         * @param isChief Whether the worker 0 should be chief.
         */
        public Builder setIsWorkerZeroChief(boolean isChief) {
            setProperty(TFConstants.TF_IS_WORKER_ZERO_CHIEF, String.valueOf(isChief));
            return this;
        }

        /** Return an immutable instance of {@link TFClusterConfig}. */
        public TFClusterConfig build() {
            Preconditions.checkState(
                    nodeTypeCntMap.containsKey(WORKER_NODE_TYPE),
                    "Tensorflow cluster config doesn't have worker nodes.");
            return new TFClusterConfig(
                    nodeTypeCntMap,
                    properties,
                    pythonFilePaths,
                    entryPythonFilePath,
                    entryFuncName,
                    pythonVirtualEnvPath);
        }
    }
}
