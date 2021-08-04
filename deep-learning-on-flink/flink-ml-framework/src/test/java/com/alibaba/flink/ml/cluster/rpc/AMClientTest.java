package com.alibaba.flink.ml.cluster.rpc;

import com.alibaba.flink.ml.proto.AMStatusMessage;
import com.alibaba.flink.ml.proto.AppMasterServiceGrpc;
import com.alibaba.flink.ml.proto.FinishNodeRequest;
import com.alibaba.flink.ml.proto.GetAMStatusRequest;
import com.alibaba.flink.ml.proto.GetClusterInfoRequest;
import com.alibaba.flink.ml.proto.GetClusterInfoResponse;
import com.alibaba.flink.ml.proto.GetFinishNodeResponse;
import com.alibaba.flink.ml.proto.GetFinishedNodeRequest;
import com.alibaba.flink.ml.proto.GetTaskIndexRequest;
import com.alibaba.flink.ml.proto.GetTaskIndexResponse;
import com.alibaba.flink.ml.proto.GetVersionRequest;
import com.alibaba.flink.ml.proto.GetVersionResponse;
import com.alibaba.flink.ml.proto.HeartBeatRequest;
import com.alibaba.flink.ml.proto.NodeSpec;
import com.alibaba.flink.ml.proto.RegisterFailedNodeRequest;
import com.alibaba.flink.ml.proto.RegisterNodeRequest;
import com.alibaba.flink.ml.proto.SimpleResponse;
import com.alibaba.flink.ml.proto.StopAllWorkerRequest;
import io.grpc.ManagedChannel;
import io.grpc.inprocess.InProcessChannelBuilder;
import io.grpc.inprocess.InProcessServerBuilder;
import io.grpc.stub.StreamObserver;
import io.grpc.testing.GrpcCleanupRule;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.mockito.ArgumentCaptor;

import static org.junit.Assert.assertEquals;
import static org.mockito.AdditionalAnswers.delegatesTo;
import static org.mockito.Matchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

public class AMClientTest {
	AMClient amClient;
	private AppMasterServiceGrpc.AppMasterServiceImplBase serviceImpl =
			mock(AppMasterServiceGrpc.AppMasterServiceImplBase.class, delegatesTo(new TestAppMasterServiceImpl()));

	@Rule
	public final GrpcCleanupRule cleanupRule = new GrpcCleanupRule();
	private NodeSpec nodeSpec;
	private int version;

	@Before
	public void setUp() throws Exception {
		String serverName = InProcessServerBuilder.generateName();
		cleanupRule.register(InProcessServerBuilder.forName(serverName).directExecutor().addService(serviceImpl).build().start());
		final ManagedChannel channel = cleanupRule.register(InProcessChannelBuilder.forName(serverName).directExecutor().build());
		amClient = new AMClient("localhost", 8080, channel);
		nodeSpec = newNodeSpec("test-role", "127.0.0.1", 0, 8081);
		version = 0;
	}

	@Test
	public void testServerName() {
		assertEquals("AppMaster", amClient.serverName());
	}

	@Test
	public void testRegisterNode() {
		amClient.registerNode(version, nodeSpec);
		final ArgumentCaptor<RegisterNodeRequest> captor = ArgumentCaptor.forClass(RegisterNodeRequest.class);
		verify(serviceImpl).registerNode(captor.capture(), any());
		assertEquals(nodeSpec, captor.getValue().getNodeSpec());
		assertEquals(version, captor.getValue().getVersion());
	}

	@Test
	public void testHeartBeat() {
		amClient.heartbeat(version, nodeSpec);
		final ArgumentCaptor<HeartBeatRequest> captor = ArgumentCaptor.forClass(HeartBeatRequest.class);
		verify(serviceImpl).heartBeatNode(captor.capture(), any());
		assertEquals(nodeSpec, captor.getValue().getNodeSpec());
		assertEquals(version, captor.getValue().getVersion());
	}

	@Test
	public void testNodeFinish() {
		amClient.nodeFinish(version, nodeSpec);
		final ArgumentCaptor<FinishNodeRequest> captor = ArgumentCaptor.forClass(FinishNodeRequest.class);
		verify(serviceImpl).nodeFinish(captor.capture(), any());
		assertEquals(nodeSpec, captor.getValue().getNodeSpec());
		assertEquals(version, captor.getValue().getVersion());
	}

	@Test
	public void testGetClusterInfo() {
		amClient.getClusterInfo(version);
		final ArgumentCaptor<GetClusterInfoRequest> captor = ArgumentCaptor.forClass(GetClusterInfoRequest.class);
		verify(serviceImpl).getClusterInfo(captor.capture(), any());
		assertEquals(version, captor.getValue().getVersion());
	}

	@Test
	public void testGetVersion() {
		amClient.getVersion();
		verify(serviceImpl).getVersion(any(GetVersionRequest.class), any());
	}

	@Test
	public void testGetAMStatus() {
		amClient.getAMStatus();
		verify(serviceImpl).getAMStatus(any(GetAMStatusRequest.class), any());
	}

	@Test
	public void testReportFailedNode() {
		amClient.reportFailedNode(version, nodeSpec);
		final ArgumentCaptor<RegisterFailedNodeRequest> captor = ArgumentCaptor.forClass(RegisterFailedNodeRequest.class);
		verify(serviceImpl).registerFailNode(captor.capture(), any());
		assertEquals(version, captor.getValue().getVersion());
		assertEquals(nodeSpec, captor.getValue().getNodeSpec());
		assertEquals("", captor.getValue().getMessage());
	}

	@Test
	public void testStopJob() {
		final String roleName = "test-role";
		final int index = 0;
		amClient.stopJob(version, roleName, index);
		final ArgumentCaptor<StopAllWorkerRequest> captor = ArgumentCaptor.forClass(StopAllWorkerRequest.class);
		verify(serviceImpl).stopAllWorker(captor.capture(), any());
		assertEquals(version, captor.getValue().getVersion());
		assertEquals(roleName, captor.getValue().getJobName());
		assertEquals(index, captor.getValue().getIndex());
	}

	@Test
	public void testGetFinishedWorker() {
		amClient.getFinishedWorker(version);
		final ArgumentCaptor<GetFinishedNodeRequest> captor = ArgumentCaptor.forClass(GetFinishedNodeRequest.class);
		verify(serviceImpl).getFinishedNode(captor.capture(), any());
		assertEquals(version, captor.getValue().getVersion());
	}

	@Test
	public void testGetTaskIndex() {
		final String scope = "test-scope";
		final String key = "key";
		amClient.getTaskIndex(version, scope, key);
		final ArgumentCaptor<GetTaskIndexRequest> captor = ArgumentCaptor.forClass(GetTaskIndexRequest.class);
		verify(serviceImpl).getTaskIndex(captor.capture(), any());
		assertEquals(version, captor.getValue().getVersion());
		assertEquals(scope, captor.getValue().getScope());
		assertEquals(key, captor.getValue().getKey());
	}

	NodeSpec newNodeSpec(String roleName, String ip, int index, int clientPort) {
		NodeSpec node = NodeSpec.newBuilder()
				.setRoleName(roleName)
				.setClientPort(clientPort)
				.setIndex(index)
				.setIp(ip)
				.build();
		return node;
	}

	private static class TestAppMasterServiceImpl extends AppMasterServiceGrpc.AppMasterServiceImplBase {
		@Override
		public void registerNode(RegisterNodeRequest request, StreamObserver<SimpleResponse> responseObserver) {
			responseObserver.onNext(SimpleResponse.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void heartBeatNode(HeartBeatRequest request, StreamObserver<SimpleResponse> responseObserver) {
			responseObserver.onNext(SimpleResponse.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void nodeFinish(FinishNodeRequest request, StreamObserver<SimpleResponse> responseObserver) {
			responseObserver.onNext(SimpleResponse.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void getClusterInfo(GetClusterInfoRequest request, StreamObserver<GetClusterInfoResponse> responseObserver) {
			responseObserver.onNext(GetClusterInfoResponse.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void getVersion(GetVersionRequest request, StreamObserver<GetVersionResponse> responseObserver) {
			responseObserver.onNext(GetVersionResponse.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void stopAllWorker(StopAllWorkerRequest request, StreamObserver<SimpleResponse> responseObserver) {
			responseObserver.onNext(SimpleResponse.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void getAMStatus(GetAMStatusRequest request, StreamObserver<AMStatusMessage> responseObserver) {
			responseObserver.onNext(AMStatusMessage.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void registerFailNode(RegisterFailedNodeRequest request, StreamObserver<SimpleResponse> responseObserver) {
			responseObserver.onNext(SimpleResponse.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void getTaskIndex(GetTaskIndexRequest request, StreamObserver<GetTaskIndexResponse> responseObserver) {
			responseObserver.onNext(GetTaskIndexResponse.newBuilder().build());
			responseObserver.onCompleted();
		}

		@Override
		public void getFinishedNode(GetFinishedNodeRequest request, StreamObserver<GetFinishNodeResponse> responseObserver) {
			responseObserver.onNext(GetFinishNodeResponse.newBuilder().build());
			responseObserver.onCompleted();
		}
	}
}