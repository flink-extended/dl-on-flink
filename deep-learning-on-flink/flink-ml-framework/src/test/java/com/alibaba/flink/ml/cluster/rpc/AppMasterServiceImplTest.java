package com.alibaba.flink.ml.cluster.rpc;

import com.alibaba.flink.ml.cluster.master.meta.AMMeta;
import com.alibaba.flink.ml.cluster.master.meta.AMMetaImpl;
import com.alibaba.flink.ml.cluster.node.MLContext;
import com.alibaba.flink.ml.proto.AppMasterServiceGrpc;
import com.alibaba.flink.ml.proto.GetClusterInfoRequest;
import com.alibaba.flink.ml.proto.GetClusterInfoResponse;
import com.alibaba.flink.ml.proto.GetFinishNodeResponse;
import com.alibaba.flink.ml.proto.GetFinishedNodeRequest;
import com.alibaba.flink.ml.proto.GetTaskIndexRequest;
import com.alibaba.flink.ml.proto.GetTaskIndexResponse;
import com.alibaba.flink.ml.proto.HeartBeatRequest;
import com.alibaba.flink.ml.proto.MLClusterDef;
import com.alibaba.flink.ml.proto.MLJobDef;
import com.alibaba.flink.ml.proto.NodeRestartResponse;
import com.alibaba.flink.ml.proto.NodeSpec;
import com.alibaba.flink.ml.proto.NodeStopResponse;
import com.alibaba.flink.ml.proto.SimpleResponse;
import com.alibaba.flink.ml.proto.StopAllWorkerRequest;
import com.alibaba.flink.ml.util.DummyContext;
import com.google.common.util.concurrent.Futures;
import com.google.common.util.concurrent.ListenableFuture;
import io.grpc.ManagedChannel;
import io.grpc.inprocess.InProcessChannelBuilder;
import io.grpc.inprocess.InProcessServerBuilder;
import io.grpc.testing.GrpcCleanupRule;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.Mockito;

import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import static org.junit.Assert.*;

public class AppMasterServiceImplTest {
	@Rule
	public final GrpcCleanupRule grpcCleanupRule = new GrpcCleanupRule();
	private AppMasterServiceGrpc.AppMasterServiceBlockingStub stub;
	private AppMasterServer appMasterServer;
	private AppMasterServiceImpl appMasterService;

	@Before
	public void setUp() throws Exception {
		final String serverName = InProcessServerBuilder.generateName();
		appMasterServer = Mockito.mock(AppMasterServer.class);
		appMasterService = Mockito.spy(new AppMasterServiceImpl(appMasterServer, 2, Duration.ofMinutes(1)));
		grpcCleanupRule.register(InProcessServerBuilder.forName(serverName).directExecutor().addService(appMasterService).build().start());
		final ManagedChannel channel
				= grpcCleanupRule.register(InProcessChannelBuilder.forName(serverName).directExecutor().build());

		stub = AppMasterServiceGrpc.newBlockingStub(channel);
	}


	@Test
	public void testHeartBeatNode() {
		final SimpleResponse response = stub.heartBeatNode(HeartBeatRequest.newBuilder().build());
		Mockito.verify(appMasterServer).updateRpcLastContact();
		assertEquals(RpcCode.OK.ordinal(), response.getCode());
	}

	@Test
	public void testHearBeatNodeWithVersionError() {
		final SimpleResponse response = stub.heartBeatNode(HeartBeatRequest.newBuilder()
				.setVersion(1).build());
		assertEquals(RpcCode.VERSION_ERROR.ordinal(), response.getCode());
	}

	@Test
	public void testRestartNode() throws Exception {
		final NodeClient nodeClient = Mockito.mock(NodeClient.class);
		Mockito.when(nodeClient.restartNode()).thenReturn(Futures.immediateFuture(NodeRestartResponse.newBuilder().build()));
		final NodeSpec nodeSpec = NodeSpec.newBuilder().setRoleName("worker").setIndex(0).build();
		appMasterService.updateNodeClient(AppMasterServer.getNodeClientKey(nodeSpec), nodeClient);

		appMasterService.restartNode(nodeSpec);
		Mockito.verify(nodeClient).restartNode();
		Mockito.verify(appMasterService).stopHeartBeatMonitorNode(Mockito.anyString());
	}

	@Test
	public void testStopNode() throws Exception {
		final NodeClient nodeClient = Mockito.mock(NodeClient.class);
		Mockito.when(nodeClient.stopNode()).thenReturn(Futures.immediateFuture(NodeStopResponse.newBuilder().build()));
		final NodeSpec nodeSpec = NodeSpec.newBuilder().setRoleName("worker").setIndex(0).build();
		appMasterService.updateNodeClient(AppMasterServer.getNodeClientKey(nodeSpec), nodeClient);

		appMasterService.stopNode(nodeSpec);
		Mockito.verify(nodeClient).stopNode();
	}

	@Test
	public void testStopAllNode() {
		final NodeClient nodeClient1 = Mockito.mock(NodeClient.class);
		Mockito.when(nodeClient1.stopNode()).thenReturn(Futures.immediateFuture(NodeStopResponse.newBuilder().build()));

		final NodeClient nodeClient2 = Mockito.mock(NodeClient.class);
		Mockito.when(nodeClient2.stopNode()).thenReturn(Futures.immediateFuture(NodeStopResponse.newBuilder().build()));

		final NodeSpec nodeSpec1 = NodeSpec.newBuilder().setRoleName("worker").setIndex(0).build();
		appMasterService.updateNodeClient(AppMasterServer.getNodeClientKey(nodeSpec1), nodeClient1);

		final NodeSpec nodeSpec2 = NodeSpec.newBuilder().setRoleName("worker").setIndex(1).build();
		appMasterService.updateNodeClient(AppMasterServer.getNodeClientKey(nodeSpec2), nodeClient2);

		appMasterService.stopAllNodes();
		Mockito.verify(nodeClient1).stopNode();
		Mockito.verify(nodeClient2).stopNode();
	}

	@Test
	public void testGetClusterInfoWithVersionError() {
		final GetClusterInfoResponse response = stub.getClusterInfo(
				GetClusterInfoRequest.newBuilder().setVersion(1).build());
		assertEquals(RpcCode.VERSION_ERROR.ordinal(), response.getCode());
	}

	@Test
	public void testStopAllWorker() {
		final SimpleResponse response = stub.stopAllWorker(StopAllWorkerRequest.newBuilder().build());
		assertEquals(RpcCode.OK.ordinal(), response.getCode());
	}

	@Test
	public void testGetTaskIndex() {
		GetTaskIndexResponse response = stub.getTaskIndex(GetTaskIndexRequest.newBuilder().build());
		assertEquals(RpcCode.OK.ordinal(), response.getCode());
		assertEquals(0, response.getIndex());

		response = stub.getTaskIndex(GetTaskIndexRequest.newBuilder().setKey("key1").build());
		assertEquals(RpcCode.OK.ordinal(), response.getCode());
		assertEquals(1, response.getIndex());

		response = stub.getTaskIndex(GetTaskIndexRequest.newBuilder().setScope("scope1").setKey("key1").build());
		assertEquals(RpcCode.OK.ordinal(), response.getCode());
		assertEquals(0, response.getIndex());
	}

	@Test
	public void testGetTaskIndexWithVersionError() {
		GetTaskIndexResponse response = stub.getTaskIndex(
				GetTaskIndexRequest.newBuilder().setVersion(1).build());
		assertEquals(RpcCode.VERSION_ERROR.ordinal(), response.getCode());
	}

	@Test
	public void testGetFinishedNode() throws IOException {
		final AMMeta amMeta = Mockito.mock(AMMeta.class);
		final MLClusterDef clusterDef = MLClusterDef.newBuilder()
				.addJob(MLJobDef.newBuilder().setName("worker")
						.putTasks(0, NodeSpec.newBuilder().build())
						.putTasks(1, NodeSpec.newBuilder().build()))
				.build();
		Mockito.when(amMeta.restoreFinishClusterDef()).thenReturn(clusterDef);
		Mockito.when(appMasterServer.getAmMeta()).thenReturn(amMeta);
		final GetFinishNodeResponse response =
				stub.getFinishedNode(GetFinishedNodeRequest.newBuilder().build());

		assertEquals(RpcCode.OK.ordinal(), response.getCode());
		assertEquals(2, response.getWorkersCount());
	}
}