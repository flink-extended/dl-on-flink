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
import org.flinkextended.flink.ml.tensorflow.util.TFConstants;

import javax.annotation.Nullable;

import java.util.Map;
import java.util.Set;

/**
 * A config for the Tensorflow cluster. It extends the {@link ClusterConfig} to provides some higher
 * level methods to config the Tensorflow cluster.
 */
public class TFClusterConfig extends ClusterConfig {

    public TFClusterConfig(
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

        private Builder() {}

        private Builder(TFClusterConfig tfClusterConfig) {
            super(tfClusterConfig);
        }

        /**
         * Set the number of workers in the Tensorflow cluster.
         *
         * @param count Number of workers.
         */
        public Builder setWorkerCount(Integer count) {
            addNodeType("worker", count);
            return this;
        }

        /**
         * Set the number of parameter servers in the Tensorflow cluster.
         *
         * @param count Number of parameter servers.
         */
        public Builder setPsCount(Integer count) {
            addNodeType("ps", count);
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
