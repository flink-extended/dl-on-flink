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

package org.flinkextended.flink.ml.operator.ops;

import org.flinkextended.flink.ml.cluster.ClusterConfig;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.operator.util.ReflectionUtils;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.configuration.Configuration;
import org.apache.flink.python.PythonConfig;
import org.apache.flink.python.env.PythonDependencyInfo;
import org.apache.flink.python.env.beam.ProcessPythonEnvironmentManager;
import org.apache.flink.streaming.api.operators.StreamingRuntimeContext;

import com.google.common.annotations.VisibleForTesting;

import java.util.HashMap;
import java.util.Map;

import static org.apache.flink.python.env.beam.ProcessPythonEnvironmentManager.PYTHON_WORKING_DIR;

/**
 * PythonEnvironmentManager prepare the python execution environment from the pyFlink configuration.
 * Use the {@link PythonEnvironmentManager#getPythonEnvProperties} to get the properties for the
 * {@link MLContext}.
 */
public class PythonEnvironmentManager {

    private final ClusterConfig clusterConfig;
    private final PythonConfig pythonConfig;
    private Map<String, String> pythonEnv;

    public PythonEnvironmentManager(ClusterConfig clusterConfig, Configuration flinkConfig) {
        this.clusterConfig = clusterConfig;
        this.pythonConfig = new PythonConfig(flinkConfig);
    }

    public void open(StreamingRuntimeContext context) throws Exception {
        final PythonDependencyInfo dependencyInfo =
                PythonDependencyInfo.create(pythonConfig, context.getDistributedCache());

        ProcessPythonEnvironmentManager pythonEnvironmentManager =
                new ProcessPythonEnvironmentManager(
                        dependencyInfo,
                        context.getTaskManagerRuntimeInfo().getTmpDirectories(),
                        new HashMap<>(System.getenv()),
                        context.getJobId());
        pythonEnvironmentManager.open();
        pythonEnv =
                ReflectionUtils.callMethod(
                        pythonEnvironmentManager,
                        ProcessPythonEnvironmentManager.class,
                        "getPythonEnv");
    }

    @VisibleForTesting
    String getWorkingDirectory() {
        final String workDir = pythonEnv.get(PYTHON_WORKING_DIR);
        if (workDir != null) {
            return workDir;
        }
        return System.getProperty("user.dir");
    }

    @VisibleForTesting
    String getPythonPath() {
        String pythonPath = pythonEnv.get("PYTHONPATH");
        if (pythonPath == null) {
            pythonPath = "";
        }
        final String originalPath =
                clusterConfig
                        .getProperties()
                        .getOrDefault(
                                MLConstants.ENV_PROPERTY_PREFIX + MLConstants.PYTHONPATH_ENV, "");
        return String.join(":", originalPath, pythonPath);
    }

    @VisibleForTesting
    String getPythonExec() {
        return pythonEnv.get("python");
    }

    public Map<String, String> getPythonEnvProperties() {
        Map<String, String> properties = new HashMap<>();
        properties.put(MLConstants.WORK_DIR, getWorkingDirectory());
        properties.put(
                MLConstants.ENV_PROPERTY_PREFIX + MLConstants.PYTHONPATH_ENV, getPythonPath());
        properties.put(MLConstants.PYTHON_EXEC, getPythonExec());
        return properties;
    }
}
