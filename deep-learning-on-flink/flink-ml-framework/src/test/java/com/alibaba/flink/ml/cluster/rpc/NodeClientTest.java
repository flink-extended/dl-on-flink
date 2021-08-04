package com.alibaba.flink.ml.cluster.rpc;

import com.alibaba.flink.ml.proto.ContextRequest;
import com.alibaba.flink.ml.proto.ContextResponse;
import com.alibaba.flink.ml.proto.FinishWorkerResponse;
import com.alibaba.flink.ml.proto.NodeRestartRequest;
import com.alibaba.flink.ml.proto.NodeRestartResponse;
import com.alibaba.flink.ml.proto.NodeServiceGrpc;
import com.alibaba.flink.ml.proto.NodeSimpleRequest;
import com.alibaba.flink.ml.proto.NodeSimpleResponse;
import com.alibaba.flink.ml.proto.NodeSpecRequest;
import com.alibaba.flink.ml.proto.NodeSpecResponse;
import com.alibaba.flink.ml.proto.NodeStopRequest;
import com.alibaba.flink.ml.proto.NodeStopResponse;
import io.grpc.ManagedChannel;
import io.grpc.inprocess.InProcessChannelBuilder;
import io.grpc.inprocess.InProcessServerBuilder;
import io.grpc.stub.StreamObserver;
import io.grpc.testing.GrpcCleanupRule;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.mockito.AdditionalAnswers.delegatesTo;
import static org.mockito.Matchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

public class NodeClientTest {
	NodeClient nodeClient;
	private final NodeServiceGrpc.NodeServiceImplBase serviceImpl =
			mock(NodeServiceGrpc.NodeServiceImplBase.class, delegatesTo(new TestNodeServiceImplBase()));

	@Rule
	public final GrpcCleanupRule cleanupRule = new GrpcCleanupRule();

	@Before
	public void setUp() throws Exception {
		String serverName = InProcessServerBuilder.generateName();
		cleanupRule.register(InProcessServerBuilder.forName(serverName).directExecutor().addService(serviceImpl).build().start());
		final ManagedChannel channel = cleanupRule.register(InProcessChannelBuilder.forName(serverName).directExecutor().build());
		nodeClient = new NodeClient("localhost", 8080, channel);
	}

	@Test
	public void testServerName() {
		assertEquals("Node(localhost:8080)", nodeClient.serverName());
	}

	@Test
	public void testGetMLContext() {
		nodeClient.getMLContext();
		verify(serviceImpl).getContext(any(ContextRequest.class), any());
	}

	@Test
	public void testStopNode() {
		nodeClient.stopNode();
		verify(serviceImpl).nodeStop(any(NodeStopRequest.class), any());
	}

	@Test
	public void testStopNodeBlocking() {
		nodeClient.stopNodeBlocking();
		verify(serviceImpl).nodeStop(any(NodeStopRequest.class), any());
	}

	@Test
	public void testRestartNode() {
		nodeClient.restartNode();
		verify(serviceImpl).nodeRestart(any(NodeRestartRequest.class), any());
	}

	@Test
	public void testGetFinishWorker() {
		nodeClient.getFinishWorker();
		verify(serviceImpl).getFinishWorker(any(NodeSimpleRequest.class), any());
	}

	@Test
	public void testStopJob() {
		nodeClient.stopJob();
		verify(serviceImpl).finishJob(any(NodeSimpleRequest.class), any());
	}

	private static class TestNodeServiceImplBase extends NodeServiceGrpc.NodeServiceImplBase {
		@Override
		public void getNodeSpec(NodeSpecRequest request, StreamObserver<NodeSpecResponse> responseObserver) {
			responseObserver.onNext(NodeSpecResponse.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void nodeRestart(NodeRestartRequest request, StreamObserver<NodeRestartResponse> responseObserver) {
			responseObserver.onNext(NodeRestartResponse.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void nodeStop(NodeStopRequest request, StreamObserver<NodeStopResponse> responseObserver) {
			responseObserver.onNext(NodeStopResponse.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void getContext(ContextRequest request, StreamObserver<ContextResponse> responseObserver) {
			responseObserver.onNext(ContextResponse.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void getFinishWorker(NodeSimpleRequest request, StreamObserver<FinishWorkerResponse> responseObserver) {
			responseObserver.onNext(FinishWorkerResponse.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void finishJob(NodeSimpleRequest request, StreamObserver<NodeSimpleResponse> responseObserver) {
			responseObserver.onNext(NodeSimpleResponse.newBuilder().build());
			responseObserver.onCompleted();
		}
	}
}