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

import org.junit.Test;

import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasEntry;
import static org.hamcrest.Matchers.hasItems;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

/** Unit test for {@link ClusterConfig}. */
public class ClusterConfigTest {
    @Test
    public void testClusterConfig() {
        final ClusterConfig clusterConfig =
                ClusterConfig.newBuilder()
                        .addNodeType("a", 1)
                        .setProperty("k", "v")
                        .addPythonFile("file1", "file2")
                        .setNodeEntry("file1", "entryFunc")
                        .setPythonVirtualEnvZip("envZipPath")
                        .build();

        assertThat(clusterConfig.getNodeTypeCntMap(), hasEntry("a", 1));
        assertThat(clusterConfig.getProperties(), hasEntry("k", "v"));
        assertThat(clusterConfig.getPythonFilePaths(), hasItems("file1", "file2"));
        assertEquals("v", clusterConfig.getProperty("k"));
        assertEquals("file1", clusterConfig.getEntryPythonFilePath());
        assertEquals("entryFunc", clusterConfig.getEntryFuncName());
        assertEquals("envZipPath", clusterConfig.getPythonVirtualEnvZipPath());
    }

    @Test(expected = NullPointerException.class)
    public void testClusterConfigMissingNodeEntry() {
        ClusterConfig.newBuilder().build();
    }

    @Test(expected = NullPointerException.class)
    public void testClusterConfigWithNullPythonEntryFile() {
        ClusterConfig.newBuilder().setNodeEntry(null, "func").build();
    }

    @Test(expected = NullPointerException.class)
    public void testClusterConfigWithNullEntryFuncName() {
        ClusterConfig.newBuilder().setNodeEntry("entry1", null).build();
    }

    @Test
    public void testNodeEntryAddEntryFileIfNotExist() {
        final ClusterConfig config =
                ClusterConfig.newBuilder().setNodeEntry("entry", "func").build();
        assertThat(config.getPythonFilePaths(), hasItems("entry"));
    }

    @Test
    public void testGetNodeTypeCnt() {
        final ClusterConfig config =
                ClusterConfig.newBuilder()
                        .addNodeType("a", 2)
                        .setNodeEntry("entry.py", "main")
                        .build();
        assertEquals(Integer.valueOf(2), config.getNodeCount("a"));
    }

    @Test(expected = IllegalArgumentException.class)
    public void testGetNonExistNodeTypeCntThrowException() {
        final ClusterConfig config =
                ClusterConfig.newBuilder().setNodeEntry("entry.py", "main").build();
        config.getNodeCount("invalid-type");
    }

    @Test
    public void testConfigToBuilder() {
        final ClusterConfig config =
                ClusterConfig.newBuilder()
                        .setProperty("k", "v")
                        .setNodeEntry("entry.py", "main")
                        .build();

        final ClusterConfig config2 =
                config.toBuilder()
                        .setProperty("k", "vv")
                        .setProperty("k2", "v2")
                        .setNodeEntry("entry2.py", "main2")
                        .build();

        // The original config is unchanged.
        assertEquals("v", config.getProperty("k"));
        assertNull(config.getProperty("k2"));
        assertEquals("entry.py", config.getEntryPythonFilePath());
        assertEquals("main", config.getEntryFuncName());
        assertNull(config.getPythonVirtualEnvZipPath());

        // Check the new config
        assertEquals("vv", config2.getProperty("k"));
        assertEquals("v2", config2.getProperty("k2"));
        assertEquals("entry2.py", config2.getEntryPythonFilePath());
        assertEquals("main2", config2.getEntryFuncName());
        assertNull(config2.getPythonVirtualEnvZipPath());
    }

    @Test
    public void testGetPythonFilePathsList() {
        final ClusterConfig config =
                ClusterConfig.newBuilder()
                        .setProperty("k", "v")
                        .addPythonFile("file1", "file2")
                        .setNodeEntry("file3.py", "main")
                        .build();
        final List<String> pythonFilePathsList = config.getPythonFilePathsList();
        assertEquals(3, pythonFilePathsList.size());
        assertEquals("file3.py", pythonFilePathsList.get(0));
    }
}
