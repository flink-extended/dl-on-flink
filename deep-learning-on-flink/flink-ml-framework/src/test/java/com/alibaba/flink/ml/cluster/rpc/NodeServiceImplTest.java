package com.alibaba.flink.ml.cluster.rpc;

import com.alibaba.flink.ml.cluster.node.MLContext;
import com.alibaba.flink.ml.proto.ContextProto;
import com.alibaba.flink.ml.proto.ContextRequest;
import com.alibaba.flink.ml.proto.ContextResponse;
import com.alibaba.flink.ml.proto.FinishWorkerResponse;
import com.alibaba.flink.ml.proto.GetFinishNodeResponse;
import com.alibaba.flink.ml.proto.NodeRestartRequest;
import com.alibaba.flink.ml.proto.NodeRestartResponse;
import com.alibaba.flink.ml.proto.NodeServiceGrpc;
import com.alibaba.flink.ml.proto.NodeSimpleRequest;
import com.alibaba.flink.ml.proto.NodeSimpleResponse;
import com.alibaba.flink.ml.proto.NodeSpec;
import com.alibaba.flink.ml.proto.NodeSpecRequest;
import com.alibaba.flink.ml.proto.NodeSpecResponse;
import com.alibaba.flink.ml.proto.NodeStopRequest;
import com.alibaba.flink.ml.proto.NodeStopResponse;
import com.alibaba.flink.ml.util.DummyContext;
import com.alibaba.flink.ml.util.MLException;
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
import java.util.Collections;

import static org.junit.Assert.*;
import static org.mockito.AdditionalAnswers.delegatesTo;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.anyInt;
import static org.mockito.Matchers.anyLong;
import static org.mockito.Matchers.anyString;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

public class NodeServiceImplTest {

	@Rule
	public final GrpcCleanupRule grpcCleanupRule = new GrpcCleanupRule();
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
				InProcessServerBuilder.forName(serverName).directExecutor().addService(nodeService).build().start());
		final ManagedChannel channel =
				grpcCleanupRule.register(InProcessChannelBuilder.forName(serverName).directExecutor().build());

		stub = NodeServiceGrpc.newBlockingStub(channel);
	}

	@Test( expected = StatusRuntimeException.class )
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
		final NodeStopResponse response =
				stub.nodeStop(NodeStopRequest.newBuilder().build());
		assertEquals(RpcCode.OK.ordinal(), response.getCode());
		Mockito.verify(nodeServer).setAmCommand(NodeServer.AMCommand.STOP);
	}

	@Test
	public void testGetContext() throws MLException {
		final ContextResponse response =
				stub.getContext(ContextRequest.newBuilder().build());
		assertEquals(RpcCode.OK.ordinal(), response.getCode());
		final MLContext actual = MLContext.fromPB(response.getContext());
		assertEquals(mlContext.getProperties(), actual.getProperties());
	}

	@Test
	public void testGetFinishWorker() throws IOException {
		when(amClient.getFinishedWorker(anyLong())).thenReturn(GetFinishNodeResponse.newBuilder().addWorkers(0).build());
		final FinishWorkerResponse response = stub.getFinishWorker(NodeSimpleRequest.newBuilder().build());
		assertEquals(RpcCode.OK.ordinal(), response.getCode());
		assertEquals(1, response.getWorkersList().size());
		assertEquals(Integer.valueOf(0), response.getWorkersList().get(0));
	}

	@Test
	public void testFinishJob() {
		final NodeSimpleResponse response =
				stub.finishJob(NodeSimpleRequest.newBuilder().build());
		assertEquals(RpcCode.OK.ordinal(), response.getCode());
		verify(amClient).stopJob(anyLong(), anyString(), anyInt());
	}
}