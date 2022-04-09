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
import org.flinkextended.flink.ml.cluster.rpc.AppMasterServer;
import org.flinkextended.flink.ml.util.MLException;

import org.apache.flink.api.common.functions.RuntimeContext;
import org.apache.flink.configuration.Configuration;

import org.junit.Before;
import org.junit.Test;

import java.io.IOException;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.isA;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.mockito.Mockito.mock;

/** Unit test for {@link AMInputFormat}. */
public class AMInputFormatTest {
    private AMInputFormat amInputFormat;

    @Before
    public void setUp() throws Exception {
        final ClusterConfig clusterConfig =
                ClusterConfig.newBuilder()
                        .addNodeType("worker", 2)
                        .setNodeEntry("entry.py", "main")
                        .build();
        amInputFormat = new AMInputFormat(clusterConfig);
        RuntimeContext mockRuntimeContext = mock(RuntimeContext.class);
        amInputFormat.setRuntimeContext(mockRuntimeContext);
    }

    @Test
    public void testConfigure() {
        amInputFormat.configure(new Configuration());
    }

    @Test
    public void testCreateInputSplits() throws IOException {
        final NodeInputSplit[] inputSplits = amInputFormat.createInputSplits(1);
        assertEquals(1, inputSplits.length);
        assertEquals(new NodeInputSplit(1, 0), inputSplits[0]);
    }

    @Test(expected = IllegalStateException.class)
    public void testCreateMoreThanOneInputSplitsThrowException() throws IOException {
        amInputFormat.createInputSplits(2);
    }

    @Test
    public void testPrepareMLContext() throws MLException {
        final MLContext mlContext = amInputFormat.prepareMLContext(0);
        assertEquals("AM", mlContext.getRoleName());
        assertEquals(0, mlContext.getIndex());
    }

    @Test(expected = IllegalStateException.class)
    public void testPrepareMLContextWithIndexGreaterThanZeroThrowException() throws MLException {
        amInputFormat.prepareMLContext(1);
    }

    @Test
    public void testGetNodeServerRunnable() throws MLException {
        final MLContext mlContext = amInputFormat.prepareMLContext(0);
        final Runnable runnable = amInputFormat.getNodeServerRunnable(mlContext);
        assertThat(runnable, isA(AppMasterServer.class));
    }

    @Test
    public void testReachedEnd() throws IOException, InterruptedException {
        amInputFormat.open(new NodeInputSplit(1, 0));

        final Thread thread =
                new Thread(
                        () -> {
                            try {
                                assertTrue(amInputFormat.reachedEnd());
                            } catch (IOException e) {
                                e.printStackTrace();
                            }
                        });

        thread.start();

        Thread.sleep(1000);
        assertEquals(Thread.State.WAITING, thread.getState());
        amInputFormat.getServerFuture().cancel(true);
        thread.join();
    }
}
