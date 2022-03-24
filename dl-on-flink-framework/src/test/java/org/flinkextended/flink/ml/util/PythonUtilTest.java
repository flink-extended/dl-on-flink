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

package org.flinkextended.flink.ml.util;

import org.flinkextended.flink.ml.cluster.ExecutionMode;
import org.flinkextended.flink.ml.cluster.MLConfig;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.role.WorkerRole;

import org.junit.Before;
import org.junit.Test;

import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/** Unit test for {@link PythonUtil}. */
public class PythonUtilTest {

    private MLContext mlContext;

    @Before
    public void setUp() throws Exception {
        final MLConfig mlConfig = DummyContext.createDummyMLConfig();
        final URL resource = FileUtil.class.getClassLoader().getResource("venv.zip");
        assertNotNull(resource);
        mlContext =
                new MLContext(
                        ExecutionMode.TRAIN,
                        mlConfig,
                        new WorkerRole().name(),
                        0,
                        resource.toString(),
                        null);
        Path workDir = Files.createTempDirectory(FileUtilTest.class.getName());
        mlContext.getProperties().put(MLConstants.WORK_DIR, workDir.toFile().getAbsolutePath());
    }

    @Test
    public void testSetupVirtualEnvProcess() throws IOException {
        PythonUtil.setupVirtualEnv(mlContext);
        assertNotEquals("", mlContext.getEnvProperty(MLConstants.LD_LIBRARY_PATH));
        final String pythonEnvPath = mlContext.getEnvProperty(MLConstants.PYTHONPATH_ENV);
        assertTrue(new File(pythonEnvPath).exists());
        assertTrue(new File(pythonEnvPath, "test.py").exists());
    }

    @Test
    public void testSetupVirtualEnv() throws IOException {
        ProcessBuilder builder = new ProcessBuilder("echo", "hello");
        PythonUtil.setupVirtualEnvProcess(mlContext, builder);
        assertNotNull(builder.environment().get(MLConstants.LD_LIBRARY_PATH));
        final String pythonEnvPath = builder.environment().get(MLConstants.PYTHONPATH_ENV);
        assertTrue(new File(pythonEnvPath).exists());
        assertTrue(new File(pythonEnvPath, "test.py").exists());
    }
}
