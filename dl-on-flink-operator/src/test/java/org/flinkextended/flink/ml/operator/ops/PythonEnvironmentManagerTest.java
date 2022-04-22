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

import org.apache.flink.api.common.JobID;
import org.apache.flink.api.common.cache.DistributedCache;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.core.fs.Path;
import org.apache.flink.python.util.PythonDependencyUtils;
import org.apache.flink.runtime.taskmanager.TaskManagerRuntimeInfo;
import org.apache.flink.streaming.api.operators.StreamingRuntimeContext;

import org.junit.Before;
import org.junit.Test;

import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;

import static org.apache.flink.python.PythonOptions.PYTHON_EXECUTABLE;
import static org.apache.flink.python.util.PythonDependencyUtils.PYTHON_ARCHIVES;
import static org.apache.flink.python.util.PythonDependencyUtils.PYTHON_FILES;
import static org.apache.flink.python.util.PythonDependencyUtils.PYTHON_REQUIREMENTS_FILE;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

/** Unit test for {@link PythonEnvironmentManager}. */
public class PythonEnvironmentManagerTest {

    private StreamingRuntimeContext context;
    private Configuration flinkConfig;

    @Before
    public void setUp() throws Exception {
        context = mock(StreamingRuntimeContext.class);
        final TaskManagerRuntimeInfo taskManagerRuntimeInfo = mock(TaskManagerRuntimeInfo.class);
        when(taskManagerRuntimeInfo.getTmpDirectories()).thenReturn(new String[] {"/tmp"});
        when(context.getTaskManagerRuntimeInfo()).thenReturn(taskManagerRuntimeInfo);
        when(context.getJobId()).thenReturn(new JobID());
        flinkConfig = new Configuration();
    }

    @Test
    public void testArchiveZipFile() throws Exception {
        final ClusterConfig config =
                ClusterConfig.newBuilder().setNodeEntry("/tmp/test.py", "main").build();
        flinkConfig.set(PYTHON_ARCHIVES, Collections.singletonMap("data", "data.zip"));
        final PythonEnvironmentManager pythonEnvironmentManager =
                new PythonEnvironmentManager(config, flinkConfig);

        final URL data = Thread.currentThread().getContextClassLoader().getResource("data.zip");
        assert data != null;
        final Future<Path> future = CompletableFuture.completedFuture(new Path(data.getPath()));
        final DistributedCache distributedCache =
                new DistributedCache(Collections.singletonMap("data", future));
        when(context.getDistributedCache()).thenReturn(distributedCache);

        pythonEnvironmentManager.open(context);
        assertTrue(
                Files.exists(
                        Paths.get(
                                pythonEnvironmentManager.getWorkingDirectory(),
                                "data.zip",
                                "data.txt")));
    }

    @Test
    public void testNoPyFlinkConfig() throws Exception {
        final ClusterConfig config =
                ClusterConfig.newBuilder().setNodeEntry("/tmp/test.py", "main").build();
        final PythonEnvironmentManager pythonEnvironmentManager =
                new PythonEnvironmentManager(config, flinkConfig);

        pythonEnvironmentManager.open(context);
        assertEquals(
                System.getProperty("user.dir"), pythonEnvironmentManager.getWorkingDirectory());
        assertEquals(":", pythonEnvironmentManager.getPythonPath());
        assertEquals("python", pythonEnvironmentManager.getPythonExec());
    }

    @Test
    public void testPythonFiles() throws Exception {
        final ClusterConfig config =
                ClusterConfig.newBuilder().setNodeEntry("/tmp/test.py", "main").build();
        Map<String, String> pythonFiles = new HashMap<>();
        pythonFiles.put("row_input.py", "row_input.py");
        pythonFiles.put("greeter.zip", "greeter.zip");
        flinkConfig.set(PYTHON_FILES, pythonFiles);
        final PythonEnvironmentManager pythonEnvironmentManager =
                new PythonEnvironmentManager(config, flinkConfig);

        final URL greeterPy =
                Thread.currentThread().getContextClassLoader().getResource("row_input.py");
        final URL greeterZip =
                Thread.currentThread().getContextClassLoader().getResource("greeter.zip");

        Map<String, Future<Path>> copyTask = new HashMap<>();
        copyTask.put(
                "row_input.py",
                CompletableFuture.completedFuture(
                        new Path(Objects.requireNonNull(greeterPy).getPath())));
        copyTask.put(
                "greeter.zip",
                CompletableFuture.completedFuture(
                        new Path(Objects.requireNonNull(greeterZip).getPath())));
        final DistributedCache distributedCache = new DistributedCache(copyTask);
        when(context.getDistributedCache()).thenReturn(distributedCache);

        pythonEnvironmentManager.open(context);
        assertTrue(checkInPythonPath("row_input.py", pythonEnvironmentManager.getPythonPath()));
        assertTrue(checkInPythonPath("greeter.py", pythonEnvironmentManager.getPythonPath()));
    }

    @Test
    public void testRequirements() throws Exception {
        final ClusterConfig config =
                ClusterConfig.newBuilder().setNodeEntry("/tmp/test.py", "main").build();
        flinkConfig.set(
                PYTHON_REQUIREMENTS_FILE,
                Collections.singletonMap(PythonDependencyUtils.FILE, "requirements.txt"));
        final PythonEnvironmentManager pythonEnvironmentManager =
                new PythonEnvironmentManager(config, flinkConfig);

        final URL requirements =
                Thread.currentThread().getContextClassLoader().getResource("requirements.txt");
        assert requirements != null;
        final Future<Path> future =
                CompletableFuture.completedFuture(new Path(requirements.getPath()));
        final DistributedCache distributedCache =
                new DistributedCache(Collections.singletonMap("requirements.txt", future));
        when(context.getDistributedCache()).thenReturn(distributedCache);

        pythonEnvironmentManager.open(context);
        checkInPythonPath(
                "dl_on_flink_framework/cluster_config.py",
                pythonEnvironmentManager.getPythonPath());
        flinkConfig.set(
                PYTHON_REQUIREMENTS_FILE,
                Collections.singletonMap(PythonDependencyUtils.FILE, "requirements.txt"));
    }

    @Test
    public void testPythonExec() throws Exception {
        final ClusterConfig config =
                ClusterConfig.newBuilder().setNodeEntry("/tmp/test.py", "main").build();
        flinkConfig.set(PYTHON_EXECUTABLE, "/my_python");
        final PythonEnvironmentManager pythonEnvironmentManager =
                new PythonEnvironmentManager(config, flinkConfig);
        pythonEnvironmentManager.open(context);
        assertEquals("/my_python", pythonEnvironmentManager.getPythonExec());
    }

    private boolean checkInPythonPath(String pythonFile, String pythonPath) {
        return Arrays.stream(pythonPath.split(":"))
                .anyMatch(path -> Files.exists(Paths.get(path, pythonFile)));
    }
}
