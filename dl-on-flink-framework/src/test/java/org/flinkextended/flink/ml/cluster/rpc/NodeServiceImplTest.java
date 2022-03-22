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

package org.flinkextended.flink.ml.cluster.rpc;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.proto.ContextRequest;
import org.flinkextended.flink.ml.proto.ContextResponse;
import org.flinkextended.flink.ml.proto.FinishWorkerResponse;
import org.flinkextended.flink.ml.proto.GetFinishNodeResponse;
import org.flinkextended.flink.ml.proto.NodeRestartRequest;
import org.flinkextended.flink.ml.proto.NodeRestartResponse;
import org.flinkextended.flink.ml.proto.NodeServiceGrpc;
import org.flinkextended.flink.ml.proto.NodeSimpleRequest;
import org.flinkextended.flink.ml.proto.NodeSimpleResponse;
import org.flinkextended.flink.ml.proto.NodeSpecRequest;
import org.flinkextended.flink.ml.proto.NodeStopRequest;
import org.flinkextended.flink.ml.proto.NodeStopResponse;
import org.flinkextended.flink.ml.util.DummyContext;
import org.flinkextended.flink.ml.util.MLException;

import io.grpc.ManagedChannel;
import io.grpc.StatusRuntimeException;
import io.grpc.inprocess.InProcessChannelBuilder;
import io.grpc.inprocess.InProcessServerBuilder;
import io.grpc.testing.GrpcCleanupRule;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.mockito.Mockito;

import java.io.IOException;

import static org.junit.Assert.*;
import static org.mockito.Matchers.anyInt;
import static org.mockito.Matchers.anyLong;
import static org.mockito.Matchers.anyString;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

public class NodeServiceImplTest {

    @Rule public final GrpcCleanupRule grpcCleanupRule = new GrpcCleanupRule();
    private NodeServiceGrpc.NodeServiceBlockingStub stub;
    private NodeServer nodeServer;
    private MLContext mlContext;
    private NodeServiceImpl nodeService;
    private AMClient amClient;

    @Before
    public void setUp() throws Exception {
        final String serverName = InProcessServerBuilder.generateName();
        nodeServer = Mockito.mock(NodeServer.class);
        mlContext = DummyContext.createDummyMLContext();
        amClient = Mockito.mock(AMClient.class);
        nodeService = new NodeServiceImpl(nodeServer, mlContext, () -> amClient);
        grpcCleanupRule.register(
                InProcessServerBuilder.forName(serverName)
                        .directExecutor()
                        .addService(nodeService)
                        .build()
                        .start());
        final ManagedChannel channel =
                grpcCleanupRule.register(
                        InProcessChannelBuilder.forName(serverName).directExecutor().build());

        stub = NodeServiceGrpc.newBlockingStub(channel);
    }

    @Test(expected = StatusRuntimeException.class)
    public void testGetNodeSpec() {
        stub.getNodeSpec(NodeSpecRequest.newBuilder().build());
    }

    @Test
    public void testNodeRestart() {
        final NodeRestartResponse nodeRestartResponse =
                stub.nodeRestart(NodeRestartRequest.newBuilder().build());
        assertEquals(RpcCode.OK.ordinal(), nodeRestartResponse.getCode());
        Mockito.verify(nodeServer).setAmCommand(NodeServer.AMCommand.RESTART);
    }

    @Test
    public void testNodeStop() {
        final NodeStopResponse response = stub.nodeStop(NodeStopRequest.newBuilder().build());
        assertEquals(RpcCode.OK.ordinal(), response.getCode());
        Mockito.verify(nodeServer).setAmCommand(NodeServer.AMCommand.STOP);
    }

    @Test
    public void testGetContext() throws MLException {
        final ContextResponse response = stub.getContext(ContextRequest.newBuilder().build());
        assertEquals(RpcCode.OK.ordinal(), response.getCode());
        final MLContext actual = MLContext.fromPB(response.getContext());
        assertEquals(mlContext.getProperties(), actual.getProperties());
    }

    @Test
    public void testGetFinishWorker() throws IOException {
        when(amClient.getFinishedWorker(anyLong()))
                .thenReturn(GetFinishNodeResponse.newBuilder().addWorkers(0).build());
        final FinishWorkerResponse response =
                stub.getFinishWorker(NodeSimpleRequest.newBuilder().build());
        assertEquals(RpcCode.OK.ordinal(), response.getCode());
        assertEquals(1, response.getWorkersList().size());
        assertEquals(Integer.valueOf(0), response.getWorkersList().get(0));
    }

    @Test
    public void testFinishJob() {
        final NodeSimpleResponse response = stub.finishJob(NodeSimpleRequest.newBuilder().build());
        assertEquals(RpcCode.OK.ordinal(), response.getCode());
        verify(amClient).stopJob(anyLong(), anyString(), anyInt());
    }
}
