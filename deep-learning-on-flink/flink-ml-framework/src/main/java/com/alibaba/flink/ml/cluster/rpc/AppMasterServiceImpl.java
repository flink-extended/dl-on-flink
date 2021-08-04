package com.alibaba.flink.ml.cluster.rpc;

import com.alibaba.flink.ml.cluster.master.AMEvent;
import com.alibaba.flink.ml.cluster.master.AMEventType;
import com.alibaba.flink.ml.cluster.master.AMService;
import com.alibaba.flink.ml.cluster.master.HeartbeatMonitor;
import com.alibaba.flink.ml.cluster.role.WorkerRole;
import com.alibaba.flink.ml.proto.AMStatus;
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
import com.alibaba.flink.ml.proto.MLClusterDef;
import com.alibaba.flink.ml.proto.MLJobDef;
import com.alibaba.flink.ml.proto.NodeRestartResponse;
import com.alibaba.flink.ml.proto.NodeSpec;
import com.alibaba.flink.ml.proto.NodeStopResponse;
import com.alibaba.flink.ml.proto.RegisterFailedNodeRequest;
import com.alibaba.flink.ml.proto.RegisterNodeRequest;
import com.alibaba.flink.ml.proto.SimpleResponse;
import com.alibaba.flink.ml.proto.StopAllWorkerRequest;
import com.alibaba.flink.ml.util.ProtoUtil;
import com.google.common.util.concurrent.ListenableFuture;
import com.google.protobuf.MessageOrBuilder;
import com.sun.jersey.json.impl.provider.entity.JSONArrayProvider;
import io.grpc.stub.StreamObserver;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.stream.Collectors;

/**
 * application master service.
 * interactive with application client.
 */
public class AppMasterServiceImpl extends AppMasterServiceGrpc.AppMasterServiceImplBase implements AMService {
	private final static Logger LOG = LoggerFactory.getLogger(AppMasterServiceImpl.class);

	private final AppMasterServer appMasterServer;
	private final ScheduledExecutorService scheduledExecutor;
	private final Duration heartbeatTimeout;
	private volatile long version = 0;
	private volatile Map<String, NodeClient> nodeClientCache = new ConcurrentHashMap<>();
	private volatile Map<String, Map<String, Integer>> nodeIndexMap = new ConcurrentHashMap<>();
	private final Map<String, HeartbeatMonitor> heartbeatMonitors = new ConcurrentHashMap<>();
	private volatile boolean isRestart = false;

	@Override
	public long version() {
		return version;
	}

	@Override
	public void setVersion(long version) {
		this.version = version;
	}


	public AppMasterServiceImpl(AppMasterServer appMasterServer, int nodeNumSum, Duration heartbeatTimeout) {
		this.appMasterServer = appMasterServer;
		this.scheduledExecutor = Executors.newScheduledThreadPool(nodeNumSum);
		this.heartbeatTimeout = heartbeatTimeout;
	}


	/**
	 * handle node register request,collect node description to create cluster
	 *
	 * @param request          node register request
	 * @param responseObserver grpc response object
	 */
	@Override
	public void registerNode(RegisterNodeRequest request, StreamObserver<SimpleResponse> responseObserver) {
		SimpleResponse.Builder response = SimpleResponse.newBuilder();

		if (checkVersionError(request.getVersion(), responseObserver)) {
			return;
		}
		appMasterServer.updateRpcLastContact();
		try {
			String clientKey = AppMasterServer.getNodeClientKey(request.getNodeSpec());
			NodeClient client = nodeClientCache.getOrDefault(clientKey, null);
			if (null != client) {
				client.close();
			}
			client = new NodeClient(request.getNodeSpec().getIp(),
					request.getNodeSpec().getClientPort());
			nodeClientCache.put(clientKey, client);
			LOG.info("register node:" + clientKey);
			startHeartBeatMonitor(request.getNodeSpec(), request.getVersion());
			appMasterServer.getAmStateMachine().handle(new AMEvent(AMEventType.REGISTER_NODE, request, request.getVersion()));
			response.setCode(RpcCode.OK.ordinal());
			response.setMessage("");
		} catch (Exception e) {
			response.setCode(RpcCode.ERROR.ordinal());
			response.setMessage(e.getMessage());
			handleStateTransitionError(request, e);
		}
		responseObserver.onNext(response.build());
		responseObserver.onCompleted();

	}

	@Override
	public void startHeartBeatMonitor(NodeSpec nodeSpec, long version) {
		String clientKey = AppMasterServer.getNodeClientKey(nodeSpec);

		HeartbeatMonitor heartbeatMonitor = new HeartbeatMonitor(
				new HeartbeatListenerImpl(appMasterServer, nodeSpec, version));
		heartbeatMonitor.updateTimeout(heartbeatTimeout, scheduledExecutor);
		heartbeatMonitors.put(clientKey, heartbeatMonitor);
		LOG.info("Started monitoring heartbeat for {}", clientKey);
	}

	@Override
	public void stopService() {
		appMasterServer.setEnd(true);
		scheduledExecutor.shutdownNow();
		LOG.info("stop heartbeat thread pool!");
	}


	/**
	 * handle node heartbeat request
	 *
	 * @param request          node heartbeat request
	 * @param responseObserver grpc response object
	 */
	@Override
	public void heartBeatNode(HeartBeatRequest request, StreamObserver<SimpleResponse> responseObserver) {
		if (!isRestart) {
			if (checkVersionError(request.getVersion(), responseObserver)) {
				return;
			}
		}
		appMasterServer.updateRpcLastContact();
		HeartbeatMonitor monitor = heartbeatMonitors.get(AppMasterServer.getNodeClientKey(request.getNodeSpec()));
		if (monitor != null) {
			monitor.updateTimeout(heartbeatTimeout, scheduledExecutor);
		}
		SimpleResponse.Builder builder = SimpleResponse.newBuilder();
		builder.setCode(RpcCode.OK.ordinal()).setMessage("");
		responseObserver.onNext(builder.build());
		responseObserver.onCompleted();
	}

	/**
	 * handle node finish request
	 *
	 * @param request          node finish request
	 * @param responseObserver grpc response object
	 */
	@Override
	public void nodeFinish(FinishNodeRequest request, StreamObserver<SimpleResponse> responseObserver) {
		if (checkVersionError(request.getVersion(), responseObserver)) {
			return;
		}
		appMasterServer.updateRpcLastContact();

		SimpleResponse.Builder response = SimpleResponse.newBuilder();
		try {
			NodeClient client = nodeClientCache.remove(AppMasterServer.getNodeClientKey(request.getNodeSpec()));
			if (client != null) {
				client.close();
			}
			stopHeartBeatMonitorNode(AppMasterServer.getNodeClientKey(request.getNodeSpec()));
			appMasterServer.getAmStateMachine().handle(new AMEvent(AMEventType.FINISH_NODE, request, request.getVersion()));
			response.setCode(RpcCode.OK.ordinal());
			response.setMessage("");
		} catch (Exception e) {
			response.setCode(RpcCode.ERROR.ordinal());
			response.setMessage(e.getMessage());
			handleStateTransitionError(request, e);
		}
		responseObserver.onNext(response.build());
		responseObserver.onCompleted();
	}

	private boolean checkVersionError(long version, StreamObserver<SimpleResponse> responseObserver) {
		if (this.version != version) {
			String message = String.format("version change current:%d request:%d", this.version, version);
			SimpleResponse.Builder response = SimpleResponse.newBuilder();
			response.setCode(RpcCode.VERSION_ERROR.ordinal()).setMessage(message);
			responseObserver.onNext(response.build());
			responseObserver.onCompleted();
			return true;
		}
		return false;
	}

	/**
	 * restart cluster node.
	 *
	 * @param nodeSpec cluster node information.
	 * @throws Exception
	 */
	@Override
	public void restartNode(NodeSpec nodeSpec) throws Exception {
		String clientKey = AppMasterServer.getNodeClientKey(nodeSpec);
		NodeClient client = nodeClientCache.getOrDefault(clientKey, null);
		if (null == client) {
			client = new NodeClient(nodeSpec.getIp(), nodeSpec.getClientPort());
			nodeClientCache.put(clientKey, client);
		}
		ListenableFuture<NodeRestartResponse> future = client.restartNode();
		try {
			NodeRestartResponse response1 = future.get();
			if (response1.getCode() == RpcCode.OK.ordinal()) {
				LOG.info("restart response:" + response1.getMessage());
			} else {
				LOG.info(response1.getMessage());
				throw new Exception(response1.getMessage());
			}
		} catch (ExecutionException e) {
			e.printStackTrace();
			throw e;
		}
		stopHeartBeatMonitorNode(clientKey);
	}

	/**
	 * restart all cluster node.
	 *
	 * @throws Exception
	 */
	@Override
	public void restartAllNodes() throws Exception {
		isRestart = true;
		version = System.currentTimeMillis();
		LOG.info("current version:" + this.version);
		List<ListenableFuture<NodeRestartResponse>> listenableFutures = new ArrayList<>();
		Set<String> toRemove = new HashSet<>();
		for (Map.Entry<String, NodeClient> client : nodeClientCache.entrySet()) {
			ListenableFuture<NodeRestartResponse> future = client.getValue().restartNode();
			listenableFutures.add(future);
			LOG.info("send restart to node:" + client.getKey());
			toRemove.add(client.getKey());
		}
		for (ListenableFuture<NodeRestartResponse> future : listenableFutures) {
			try {
				NodeRestartResponse response1 = future.get();
				if (response1.getCode() == RpcCode.OK.ordinal()) {
					LOG.info("restart response:" + response1.getMessage());
				} else {
					LOG.info(response1.getMessage());
					//throw new Exception(response1.getMessage());
				}
			} catch (ExecutionException e) {
				e.printStackTrace();
				LOG.info("restart err:" + e.getMessage());
				//throw new Exception(e);
			}
		}

		for (NodeClient client : nodeClientCache.values()) {
			client.close();
		}
		for (String key : toRemove) {
			nodeClientCache.remove(key);
			stopHeartBeatMonitorNode(key);
		}
		isRestart = false;
	}

	@Override
	public void stopHeartBeatMonitorNode(String clientKey) {
		HeartbeatMonitor monitor = heartbeatMonitors.remove(clientKey);
		if (monitor != null) {
			monitor.cancel();
			LOG.info("Stopped monitoring heartbeat for {}", clientKey);
		}
	}

	@Override
	public void stopHeartBeatMonitorAllNode() {
		for (String clientKey : heartbeatMonitors.keySet()) {
			stopHeartBeatMonitorNode(clientKey);
		}
	}


	/**
	 * stop a cluster node.
	 *
	 * @param nodeSpec node information.
	 * @throws Exception
	 */
	@Override
	public void stopNode(NodeSpec nodeSpec) throws Exception {
		String clientKey = AppMasterServer.getNodeClientKey(nodeSpec);
		NodeClient client = nodeClientCache.getOrDefault(clientKey, null);
		if (null == client) {
			client = new NodeClient(nodeSpec.getIp(), nodeSpec.getClientPort());
			nodeClientCache.put(clientKey, client);
		}
		ListenableFuture<NodeStopResponse> future = client.stopNode();
		try {
			NodeStopResponse response1 = future.get();
			if (response1.getCode() == RpcCode.OK.ordinal()) {
				LOG.info("stop response:" + response1.getMessage());
			} else {
				LOG.info(response1.getMessage());
				throw new Exception(response1.getMessage());
			}
		} catch (ExecutionException e) {
			e.printStackTrace();
			throw e;
		}
	}

	public void stopAllNodes() {
		if (nodeClientCache.isEmpty()) {
			return;
		}
		List<ListenableFuture<NodeStopResponse>> listenableFutures = new ArrayList<>();
		LOG.info("client size:" + nodeClientCache.size());
		for (Map.Entry<String, NodeClient> client : nodeClientCache.entrySet()) {
			ListenableFuture<NodeStopResponse> future = client.getValue().stopNode();
			listenableFutures.add(future);
			LOG.info("send stop to node:" + client.getKey());
		}
		for (ListenableFuture<NodeStopResponse> future : listenableFutures) {
			try {
				NodeStopResponse response1 = future.get();
				if (response1.getCode() == RpcCode.OK.ordinal()) {
					// do nothing
				} else {
					LOG.info(response1.getMessage());
				}
			} catch (InterruptedException | ExecutionException e) {
				//this error is expected as we are asking the TFNodeServers to stop their service.
				LOG.debug("Stop node server.", e);
			}
		}

		for (NodeClient client : nodeClientCache.values()) {
			client.close();
		}
		nodeClientCache.clear();
		stopHeartBeatMonitorAllNode();
	}

	private boolean checkVersionError(long version, StreamObserver responseObserver,
									  GetClusterInfoResponse.Builder builder) {
		if (this.version != version) {
			String message = String.format("version change current:%d request:%d", this.version, version);
			builder.setCode(RpcCode.VERSION_ERROR.ordinal()).setMessage(message)
					.setClusterDef(MLClusterDef.newBuilder());
			responseObserver.onNext(builder.build());
			responseObserver.onCompleted();
			return true;
		}
		return false;
	}

	/**
	 * handle node get cluster information request
	 *
	 * @param request          get cluster information request
	 * @param responseObserver grpc response object
	 */
	@Override
	public void getClusterInfo(GetClusterInfoRequest request,
							   StreamObserver<GetClusterInfoResponse> responseObserver) {
		GetClusterInfoResponse.Builder responseBuilder = GetClusterInfoResponse.newBuilder();
		if (checkVersionError(request.getVersion(), responseObserver, responseBuilder)) {
			return;
		}
		appMasterServer.updateRpcLastContact();
		try {
			MLClusterDef clusterDef = appMasterServer.getAmMeta().restoreClusterDef();
			if (null != clusterDef) {
				MLClusterDef merged = mergeFinishedClusterDef(clusterDef, appMasterServer.getAmMeta().restoreFinishClusterDef());
				responseBuilder.setCode(RpcCode.OK.ordinal()).setClusterDef(merged);
			} else {
				responseBuilder.setCode(RpcCode.NOT_READY.ordinal())
						.setMessage("cluster is null!");
			}
		} catch (IOException e) {
			e.printStackTrace();
			responseBuilder.setCode(RpcCode.ERROR.ordinal());
		}
		responseObserver.onNext(responseBuilder.build());
		responseObserver.onCompleted();
	}

	/**
	 * handle node get current job version request
	 *
	 * @param request          get current job version request
	 * @param responseObserver grpc response object
	 */
	@Override
	public void getVersion(GetVersionRequest request, StreamObserver<GetVersionResponse> responseObserver) {
		appMasterServer.updateRpcLastContact();
		GetVersionResponse.Builder builder = GetVersionResponse.newBuilder()
				.setVersion(this.version);
		responseObserver.onNext(builder.build());
		responseObserver.onCompleted();
	}

	/**
	 * handle stop cluster request
	 *
	 * @param request          stop cluster request
	 * @param responseObserver grpc response object
	 */
	@Override
	public void stopAllWorker(StopAllWorkerRequest request, StreamObserver<SimpleResponse> responseObserver) {
		appMasterServer.updateRpcLastContact();
		SimpleResponse response = SimpleResponse.newBuilder().setMessage("").setCode(RpcCode.OK.ordinal()).build();
		responseObserver.onNext(response);
		responseObserver.onCompleted();
		try {
			appMasterServer.getAmStateMachine().handle(new AMEvent(AMEventType.STOP_JOB, request, request.getVersion()));
		} catch (Exception e) {
			handleStateTransitionError(request, e);
		}
	}

	/**
	 * handle node get application master status
	 *
	 * @param request          get application master status request
	 * @param responseObserver grpc response object
	 */
	@Override
	public void getAMStatus(GetAMStatusRequest request, StreamObserver<AMStatusMessage> responseObserver) {
		appMasterServer.updateRpcLastContact();
		AMStatus status = appMasterServer.getAmStateMachine().getInternalState();
		AMStatusMessage message = AMStatusMessage.newBuilder()
				.setStatus(status).build();
		responseObserver.onNext(message);
		responseObserver.onCompleted();
	}

	/**
	 * handle node report failed request
	 *
	 * @param request          node report failed request
	 * @param responseObserver grpc response object
	 */
	@Override
	public void registerFailNode(RegisterFailedNodeRequest request,
								 StreamObserver<SimpleResponse> responseObserver) {
		if (checkVersionError(request.getVersion(), responseObserver)) {
			return;
		}
		appMasterServer.updateRpcLastContact();
		SimpleResponse.Builder builder = SimpleResponse.newBuilder();
		try {
			appMasterServer.getAmStateMachine().handle(new AMEvent(AMEventType.FAIL_NODE, request, request.getVersion()));
			builder.setCode(RpcCode.OK.ordinal()).setMessage("");
			responseObserver.onNext(builder.build());
			responseObserver.onCompleted();
		} catch (Exception e) {
			builder.setCode(RpcCode.ERROR.ordinal()).setMessage(e.getMessage());
			responseObserver.onNext(builder.build());
			responseObserver.onCompleted();
			handleStateTransitionError(request, e);
		}

	}

	private boolean checkVersionError(long version, StreamObserver responseObserver,
									  GetTaskIndexResponse.Builder builder) {
		if (this.version != version) {
			String message = String.format("version change current:%d request:%d", this.version, version);
			builder.setCode(RpcCode.VERSION_ERROR.ordinal()).setMessage(message).setIndex(0);
			responseObserver.onNext(builder.build());
			responseObserver.onCompleted();
			return true;
		}
		return false;
	}

	/**
	 * handle node generate task index request
	 *
	 * @param request          node get task index request
	 * @param responseObserver grpc response object
	 */
	@Override
	public synchronized void getTaskIndex(GetTaskIndexRequest request,
										  StreamObserver<GetTaskIndexResponse> responseObserver) {
		GetTaskIndexResponse.Builder builder = GetTaskIndexResponse.newBuilder();
		if (checkVersionError(request.getVersion(), responseObserver, builder)) {
			return;
		}
		appMasterServer.updateRpcLastContact();
		Map<String, Integer> map = nodeIndexMap
				.computeIfAbsent(request.getScope(), k -> new ConcurrentHashMap<>());
		int index = map.computeIfAbsent(request.getKey(), k -> map.size());
		builder.setIndex(index);
		builder.setCode(RpcCode.OK.ordinal());
		responseObserver.onNext(builder.build());
		responseObserver.onCompleted();
	}

	/**
	 * handle node get finished nodes request
	 *
	 * @param request          get finished nodes request
	 * @param responseObserver grpc response object
	 */
	@Override
	public void getFinishedNode(GetFinishedNodeRequest request,
								StreamObserver<GetFinishNodeResponse> responseObserver) {
		appMasterServer.updateRpcLastContact();
		GetFinishNodeResponse.Builder builder = GetFinishNodeResponse.newBuilder();
		try {
			builder.setCode(0)
					.setMessage("");
			MLClusterDef clusterDef = appMasterServer.getAmMeta().restoreFinishClusterDef();
			if (null != clusterDef) {
				for (MLJobDef jobDef : clusterDef.getJobList()) {
					if (jobDef.getName().equals(new WorkerRole().name())) {
						for (Integer index : jobDef.getTasksMap().keySet()) {
							builder.addWorkers(index);
						}
					}
				}
			}
		} catch (IOException e) {
			e.printStackTrace();
			builder.setCode(1)
					.setMessage(e.getMessage());
		}
		responseObserver.onNext(builder.build());
		responseObserver.onCompleted();
	}

	private MLClusterDef mergeFinishedClusterDef(MLClusterDef clusterDef, MLClusterDef finishDef) {
		if (finishDef == null) {
			return clusterDef;
		}
		MLClusterDef.Builder clusterBuilder = MLClusterDef.newBuilder();
		Map<String, MLJobDef> nameToRunningDef = clusterDef.getJobList().stream().collect(
				Collectors.toMap(MLJobDef::getName, def -> def));
		for (MLJobDef finishedJob : finishDef.getJobList()) {
			if (!nameToRunningDef.containsKey(finishedJob.getName())) {
				clusterBuilder.addJob(finishedJob);
			} else {
				MLJobDef.Builder jobBuilder = MLJobDef.newBuilder();
				MLJobDef runningJobDef = nameToRunningDef.get(finishedJob.getName());
				jobBuilder.mergeFrom(runningJobDef);
				for (Integer index : finishedJob.getTasksMap().keySet()) {
					// a task may exist in both running and finished def due to race condition
					if (!runningJobDef.getTasksMap().containsKey(index)) {
						jobBuilder.putTasks(index, finishedJob.getTasksMap().get(index));
					}
				}
				clusterBuilder.addJob(jobBuilder.build());
				nameToRunningDef.remove(finishedJob.getName());
			}
		}
		clusterBuilder.addAllJob(nameToRunningDef.values());
		return clusterBuilder.build();
	}

	public void handleStateTransitionError(MessageOrBuilder request, Throwable t) {
		String msg = request != null ?
				String.format("Failed to handle request %s:\n%s",
						request.getClass().getName(), ProtoUtil.protoToJson(request)) :
				"State transition failed";
		LOG.error(msg, t);
		// currently we don't recover from state transition errors, so fail the job
		appMasterServer.onError(t);
	}

	@Override
	public void updateNodeClient(String key, NodeClient client) {
		nodeClientCache.put(key, client);
	}

}
