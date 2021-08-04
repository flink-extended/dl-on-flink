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

package com.alibaba.flink.ml.cluster.rpc;

import com.alibaba.flink.ml.proto.*;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * client to communicate with application master.
 */
public class AMClient extends AbstractGrpcClient {
	private static final Logger LOG = LoggerFactory.getLogger(AMClient.class);

	private AppMasterServiceGrpc.AppMasterServiceBlockingStub blockingStub;

	/** Construct client for accessing AM server using the existing channel. */
	public AMClient(String host, int port, ManagedChannel channel) {
		super(host, port, channel);
		blockingStub = AppMasterServiceGrpc.newBlockingStub(grpcChannel);
	}

	public AMClient(String host, int port) {
		this(host, port, ManagedChannelBuilder.forAddress(host, port)
				.enableRetry()
				.maxRetryAttempts(3)
				// Channels are secure by default (via SSL/TLS). For the example we disable TLS to avoid
				// needing certificates.
				.usePlaintext()
				.build());
	}

	@Override
	String serverName() {
		return "AppMaster";
	}

	/**
	 * register machine learning cluster node
	 * @param version
	 *      machine learning job instance id
	 * @param nodeSpec
	 *      machine learning cluster node description
	 * @return SimpleResponse
	 */
	public SimpleResponse registerNode(long version, NodeSpec nodeSpec) {
		RegisterNodeRequest request = RegisterNodeRequest.newBuilder()
				.setVersion(version).setNodeSpec(nodeSpec).build();
		return blockingStub.registerNode(request);
	}

	/**
	 * cluster node report heartbeat to application master
	 * @param version
	 *      machine learning job instance id
	 * @param nodeSpec
	 *      machine learning cluster node description
	 * @return SimpleResponse
	 */
	public SimpleResponse heartbeat(long version, NodeSpec nodeSpec) {
		HeartBeatRequest request = HeartBeatRequest.newBuilder().setVersion(version).setNodeSpec(nodeSpec).build();
		return blockingStub.heartBeatNode(request);
	}

	/**
	 * cluster node report finished
	 * @param version
	 *      machine learning job instance id
	 * @param nodeSpec
	 *      machine learning cluster node description
	 * @return SimpleResponse
	 */
	public SimpleResponse nodeFinish(long version, NodeSpec nodeSpec) {
		FinishNodeRequest request = FinishNodeRequest.newBuilder().setVersion(version).setNodeSpec(nodeSpec).build();
		return blockingStub.nodeFinish(request);
	}

	/**
	 * get cluster information
	 * @param version
	 *      machine learning job instance id
	 * @return cluster information
	 */
	public GetClusterInfoResponse getClusterInfo(long version) {
		GetClusterInfoRequest request = GetClusterInfoRequest.newBuilder().setVersion(version).setMessage("").build();
		return blockingStub.getClusterInfo(request);
	}

	/**
	 * get job version
	 * @return current job version
	 */
	public GetVersionResponse getVersion() {
		GetVersionRequest request = GetVersionRequest.newBuilder().setMessage("").build();
		return blockingStub.getVersion(request);
	}

	/**
	 * get application master status
	 * @return application master status
	 */
	public AMStatus getAMStatus() {
		GetAMStatusRequest request = GetAMStatusRequest.newBuilder().setMessage("").build();
		return blockingStub.getAMStatus(request).getStatus();
	}

	/**
	 * node report failed to application master
	 * @param version
	 *      machine learning job instance id
	 * @param nodeSpec
	 *      machine learning cluster node description
	 * @return SimpleResponse
	 */
	public SimpleResponse reportFailedNode(long version, NodeSpec nodeSpec) {
		return blockingStub.registerFailNode(
				RegisterFailedNodeRequest.newBuilder().setVersion(version).setNodeSpec(nodeSpec).build());
	}

	/***
	 *
	 * @param version
	 *      machine learning job instance id
	 * @param roleName
	 *      machine learning cluster role name
	 * @param index
	 *      cluster a role index
	 * @return SimpleResponse
	 */
	public SimpleResponse stopJob(long version, String roleName, int index) {
		StopAllWorkerRequest request = StopAllWorkerRequest.newBuilder()
				.setVersion(version)
				.setJobName(roleName)
				.setIndex(index)
				.build();
		return blockingStub.stopAllWorker(request);
	}

	/**
	 * get finished workers
	 * @param version
	 *      machine learning job instance id
	 * @return finished workers information
	 */
	public GetFinishNodeResponse getFinishedWorker(long version) {
		GetFinishedNodeRequest request = GetFinishedNodeRequest.newBuilder()
				.setVersion(version)
				.build();
		return blockingStub.getFinishedNode(request);
	}

	public int getTaskIndex(long version, String scope, String key) {
		GetTaskIndexResponse response = blockingStub.getTaskIndex(GetTaskIndexRequest.newBuilder()
				.setScope(scope).setKey(key).setVersion(version).build());
		if (response.getCode() == RpcCode.OK.ordinal()) {
			return response.getIndex();
		} else {
			throw new RuntimeException(response.getMessage());
		}
	}

}
