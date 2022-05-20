/*
 * Copyright 2022 Deep Learning on Flink Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.flinkextended.flink.ml.pytorch;

import org.flinkextended.flink.ml.cluster.ClusterConfig;
import org.flinkextended.flink.ml.operator.coding.RowCSVCoding;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.util.Preconditions;

import javax.annotation.Nullable;

import java.util.Map;
import java.util.Set;

/**
 * A config for the PyTorch cluster. It extends the {@link ClusterConfig} to provides some higher
 * level methods to config the PyTorch cluster.
 */
public class PyTorchClusterConfig extends ClusterConfig {
    public static final String WORKER_NODE_TYPE = "worker";

    protected PyTorchClusterConfig(
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

    /** Create a new {@link Builder} for {@link PyTorchClusterConfig}. */
    public static Builder newBuilder() {
        return new Builder();
    }

    /** Builder of {@link PyTorchClusterConfig}. */
    public static class Builder extends ClusterConfig.Builder<Builder> {

        private Builder() {
            // Default properties for PyTorch cluster config.
            setProperty(MLConstants.ML_RUNNER_CLASS, PyTorchRunner.class.getName());
            setProperty(MLConstants.ENCODING_CLASS, RowCSVCoding.class.getName());
            setProperty(MLConstants.DECODING_CLASS, RowCSVCoding.class.getName());
        }

        /**
         * Set the number of processes participating in the PyTorch job.
         *
         * @param worldSize Number of processes participating in the PyTorch job.
         */
        public Builder setWorldSize(int worldSize) {
            addNodeType(WORKER_NODE_TYPE, worldSize);
            return this;
        }

        /** Return an immutable instance of {@link PyTorchClusterConfig}. */
        public PyTorchClusterConfig build() {
            Preconditions.checkState(
                    nodeTypeCntMap.containsKey(WORKER_NODE_TYPE),
                    "Tensorflow cluster config doesn't have worker nodes.");
            return new PyTorchClusterConfig(
                    nodeTypeCntMap,
                    properties,
                    pythonFilePaths,
                    entryPythonFilePath,
                    entryFuncName,
                    pythonVirtualEnvPath);
        }
    }
}
