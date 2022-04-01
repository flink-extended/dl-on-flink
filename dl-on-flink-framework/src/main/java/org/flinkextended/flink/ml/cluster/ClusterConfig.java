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

package org.flinkextended.flink.ml.cluster;

import com.google.common.base.Preconditions;

import javax.annotation.Nullable;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * A config for the deep learning cluster. It is use for the following config:
 *
 * <ul>
 *   <li>The node type and the number of nodes for each node type in the cluster.
 *   <li>The python files and the python environment to run the deep learning node.
 *   <li>Any properties for the deep learning node.
 * </ul>
 */
public class ClusterConfig implements Serializable {
    public static final String AM_NODE_TYPE = "am";

    private final Map<String, Integer> nodeTypeCntMap;
    private final Map<String, String> properties;
    private final Set<String> pythonFilePaths;
    private final String entryPythonFilePath;
    private final String entryFuncName;
    private final String pythonVirtualEnvZipPath;

    public ClusterConfig(
            Map<String, Integer> nodeTypeCntMap,
            Map<String, String> properties,
            Set<String> pythonFilePaths,
            String entryPythonFilePath,
            String entryFuncName,
            @Nullable String pythonVirtualEnvZipPath) {
        Preconditions.checkNotNull(
                entryPythonFilePath, "ClusterConfig is missing entry python file path.");
        Preconditions.checkNotNull(entryFuncName, "ClusterConfig is missing entry function name.");
        this.nodeTypeCntMap = Collections.unmodifiableMap(nodeTypeCntMap);
        this.properties = Collections.unmodifiableMap(properties);
        this.pythonFilePaths = Collections.unmodifiableSet(pythonFilePaths);
        this.entryPythonFilePath = entryPythonFilePath;
        this.entryFuncName = entryFuncName;
        this.pythonVirtualEnvZipPath = pythonVirtualEnvZipPath;
    }

    /** Create a new {@link Builder} for {@link ClusterConfig}. */
    public static Builder<?> newBuilder() {
        return new Builder<>();
    }

    /** Create a new {@link Builder} from the current immutable {@link ClusterConfig}. */
    public Builder<?> toBuilder() {
        return new Builder<>(this);
    }

    public Map<String, Integer> getNodeTypeCntMap() {
        return nodeTypeCntMap;
    }

    public Map<String, String> getProperties() {
        return properties;
    }

    public String getProperty(String key) {
        return properties.get(key);
    }

    public String getEntryPythonFilePath() {
        return entryPythonFilePath;
    }

    public String getEntryFuncName() {
        return entryFuncName;
    }

    public String getPythonVirtualEnvZipPath() {
        return pythonVirtualEnvZipPath;
    }

    public Set<String> getPythonFilePaths() {
        return pythonFilePaths;
    }

    /**
     * Get a list of the python file paths where the first file paths is the entry files of the
     * node.
     */
    public List<String> getPythonFilePathsList() {
        List<String> res = new ArrayList<>();
        res.add(entryPythonFilePath);
        for (String pythonFilePath : pythonFilePaths) {
            if (pythonFilePath.equals(entryPythonFilePath)) {
                continue;
            }
            res.add(pythonFilePath);
        }
        return res;
    }

    public Integer getNodeCount(String nodeType) {
        if (!nodeTypeCntMap.containsKey(nodeType)) {
            throw new IllegalArgumentException(
                    String.format(
                            "ClusterConfig doesn't contain count of node with node type %s",
                            nodeType));
        }
        return nodeTypeCntMap.get(nodeType);
    }

    /** Builder for {@link ClusterConfig}. */
    @SuppressWarnings("unchecked")
    public static class Builder<T extends Builder<T>> {

        protected final Map<String, Integer> nodeTypeCntMap;
        protected final Map<String, String> properties;
        protected final Set<String> pythonFilePaths;
        protected String entryPythonFilePath;
        protected String entryFuncName;
        protected String pythonVirtualEnvPath;

        protected Builder() {
            this.nodeTypeCntMap = new HashMap<>();
            this.properties = new HashMap<>();
            this.pythonFilePaths = new HashSet<>();
        }

        protected Builder(ClusterConfig clusterConfig) {
            this.nodeTypeCntMap = new HashMap<>(clusterConfig.getNodeTypeCntMap());
            this.properties = new HashMap<>(clusterConfig.getProperties());
            this.pythonFilePaths = new HashSet<>(clusterConfig.getPythonFilePaths());
            this.entryPythonFilePath = clusterConfig.getEntryPythonFilePath();
            this.entryFuncName = clusterConfig.getEntryFuncName();
            this.pythonVirtualEnvPath = clusterConfig.getPythonVirtualEnvZipPath();
        }

        /**
         * Add a node type to the deep learning cluster and specify how many node with the given
         * node type should be in the cluster.
         *
         * @param nodeType The node type to be added.
         * @param count The number of node with the node type should be in the cluster.
         */
        public T addNodeType(String nodeType, Integer count) {
            nodeTypeCntMap.put(nodeType, count);
            return (T) this;
        }

        /**
         * Set a property for the deep learning cluster and nodes.
         *
         * @param key Key of the property.
         * @param value Value of the property.
         */
        public T setProperty(String key, String value) {
            properties.put(key, value);
            return (T) this;
        }

        /**
         * Add a list of python file to the PYTHON_PATH of the python process that runs in the node.
         *
         * @param pythonFilePaths A list of path of python files.
         */
        public T addPythonFile(String... pythonFilePaths) {
            this.pythonFilePaths.addAll(Arrays.asList(pythonFilePaths));
            return (T) this;
        }

        /**
         * Add the entry python file if it is not added before and set it as the entry point of the
         * deep learning node.
         *
         * @param pythonFilePath The path of the entry python file.
         * @param funcName the entry function name in the entry python file.
         */
        public T setNodeEntry(String pythonFilePath, String funcName) {
            pythonFilePaths.add(pythonFilePath);
            entryPythonFilePath = pythonFilePath;
            entryFuncName = funcName;
            return (T) this;
        }

        /**
         * Set a zipped python virtual environment under which the deep learning process will run.
         *
         * @param pythonVirtualEnvPath The path of the zipped python virtual environment.
         */
        public T setPythonVirtualEnvZip(String pythonVirtualEnvPath) {
            this.pythonVirtualEnvPath = pythonVirtualEnvPath;
            return (T) this;
        }

        /** Return an immutable instance of {@link ClusterConfig}. */
        public ClusterConfig build() {
            return new ClusterConfig(
                    nodeTypeCntMap,
                    properties,
                    pythonFilePaths,
                    entryPythonFilePath,
                    entryFuncName,
                    pythonVirtualEnvPath);
        }
    }
}
