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
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.rpc.NodeServer;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.MLException;

import org.apache.flink.api.common.JobID;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.runtime.taskmanager.TaskManagerRuntimeInfo;
import org.apache.flink.streaming.api.operators.StreamingRuntimeContext;

import org.junit.Before;
import org.junit.Test;

import java.io.IOException;
import java.util.Arrays;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasItems;
import static org.hamcrest.Matchers.isA;
import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

/** Unit test for {@link NodeInputFormat}. */
public class NodeInputFormatTest {

    private NodeInputFormat<Integer> nodeInputFormat;

    @Before
    public void setUp() throws Exception {
        final ClusterConfig clusterConfig =
                ClusterConfig.newBuilder()
                        .addNodeType("worker", 2)
                        .setNodeEntry("entry.py", "main")
                        .build();
        nodeInputFormat = new NodeInputFormat<>("worker", clusterConfig);
        StreamingRuntimeContext mockRuntimeContext = mock(StreamingRuntimeContext.class);
        final TaskManagerRuntimeInfo taskManagerRuntimeInfo = mock(TaskManagerRuntimeInfo.class);
        when(taskManagerRuntimeInfo.getTmpDirectories()).thenReturn(new String[] {"/tmp"});
        when(mockRuntimeContext.getTaskManagerRuntimeInfo()).thenReturn(taskManagerRuntimeInfo);
        when(mockRuntimeContext.getJobId()).thenReturn(new JobID());

        nodeInputFormat.setRuntimeContext(mockRuntimeContext);
    }

    @Test
    public void testCreateInputSplits() throws IOException {
        final NodeInputSplit[] inputSplits = nodeInputFormat.createInputSplits(2);
        assertEquals(2, inputSplits.length);
        assertThat(
                Arrays.asList(inputSplits),
                hasItems(new NodeInputSplit(2, 0), new NodeInputSplit(2, 1)));
    }

    @Test(expected = IllegalStateException.class)
    public void testCreatInputSplitsThrowExceptionWhenMoreSplitAreDesired() throws IOException {
        nodeInputFormat.createInputSplits(3);
    }

    @Test
    public void testPrepareMLContext() throws MLException {
        final MLContext mlContext = nodeInputFormat.prepareMLContext(0);
        assertEquals("", mlContext.getEnvProperty(MLConstants.GPU_INFO));
    }

    @Test
    public void testGetNodeServerRunnable() throws MLException {
        final MLContext mlContext = nodeInputFormat.prepareMLContext(0);
        final Runnable runnable = nodeInputFormat.getNodeServerRunnable(mlContext);
        assertThat(runnable, isA(NodeServer.class));
    }

    @Test
    public void testConfigure() {
        nodeInputFormat.configure(new Configuration());
    }
}
