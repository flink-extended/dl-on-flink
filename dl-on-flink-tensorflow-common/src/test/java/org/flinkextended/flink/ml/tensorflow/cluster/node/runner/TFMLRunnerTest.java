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

package org.flinkextended.flink.ml.tensorflow.cluster.node.runner;

import org.flinkextended.flink.ml.cluster.ExecutionMode;
import org.flinkextended.flink.ml.cluster.MLConfig;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.role.AMRole;
import org.flinkextended.flink.ml.cluster.rpc.AppMasterServer;
import org.flinkextended.flink.ml.cluster.rpc.NodeServer;
import org.flinkextended.flink.ml.proto.GetClusterInfoResponse;
import org.flinkextended.flink.ml.proto.NodeSpec;
import org.flinkextended.flink.ml.util.DummyContext;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.MLException;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;

import java.util.Map;
import java.util.concurrent.FutureTask;

import static org.junit.Assert.*;

public class TFMLRunnerTest {
    private FutureTask<Void> amFuture;
    private AppMasterServer amServer;

    private TFMLRunner mlRunner;
    private NodeServer nodeServer;
    private static MLConfig mlConfig;
    private MLContext mlContext;

    @Before
    public void setUp() throws Exception {
        mlConfig = DummyContext.createDummyMLConfig();
        startAMServer(mlConfig);
        nodeServer = Mockito.mock(NodeServer.class);
        mlContext = DummyContext.createDummyMLContext();
        mlContext
                .getProperties()
                .put(MLConstants.SCRIPT_RUNNER_CLASS, TestScriptRunner.class.getCanonicalName());
        mlRunner = Mockito.spy(new TFMLRunner(mlContext, nodeServer));
        mlRunner.initAMClient();
        assertNotNull(mlRunner.getAMClient());
    }

    @After
    public void tearDown() throws Exception {
        amServer.setEnd(true);
        amFuture.get();
    }

    @Test
    public void testRegisterNode() throws Exception {
        mlRunner.registerNode();
        final GetClusterInfoResponse clusterInfo =
                mlRunner.getAMClient().getClusterInfo(mlRunner.getVersion());
        final Map<Integer, NodeSpec> tasksMap = clusterInfo.getClusterDef().getJob(0).getTasksMap();
        final NodeSpec nodeSpec = tasksMap.get(0);
        assertEquals(mlContext.getRoleName(), nodeSpec.getRoleName());
        assertEquals(mlContext.getIndex(), nodeSpec.getIndex());
    }

    @Test
    public void testResetMLContext() throws Exception {
        mlRunner.getCurrentJobVersion();
        mlRunner.registerNode();
        mlRunner.getClusterInfo();
        assertNull(mlRunner.getMLContext().getProperties().get(MLConstants.CONFIG_CLUSTER_PATH));
        mlRunner.resetMLContext();
        assertNotNull(mlRunner.getMLContext().getProperties().get(MLConstants.CONFIG_CLUSTER_PATH));
    }

    @Test
    public void testRun() throws Exception {
        mlRunner.run();
        Mockito.verify(mlRunner, Mockito.atLeastOnce()).initAMClient();
        Mockito.verify(mlRunner, Mockito.atLeastOnce()).getCurrentJobVersion();
        Mockito.verify(mlRunner).getTaskIndex();
        Mockito.verify(mlRunner).registerNode();
        Mockito.verify(mlRunner).startHeartBeat();
        Mockito.verify(mlRunner).waitClusterRunning();
        Mockito.verify(mlRunner).getClusterInfo();
        Mockito.verify(mlRunner).resetMLContext();
        Mockito.verify(mlRunner).runScript();
    }

    private FutureTask<Void> startAMServer(MLConfig mlConfig) throws MLException {
        MLContext amContext =
                new MLContext(ExecutionMode.TRAIN, mlConfig, new AMRole().name(), 0, null, null);
        amServer = new AppMasterServer(amContext);
        amFuture = new FutureTask<>(amServer, null);
        Thread thread = new Thread(amFuture);
        thread.setDaemon(true);
        thread.start();
        return amFuture;
    }
}
