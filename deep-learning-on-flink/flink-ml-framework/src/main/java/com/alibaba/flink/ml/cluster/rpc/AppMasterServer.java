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

import com.alibaba.flink.ml.cluster.BaseEventReporter;
import com.alibaba.flink.ml.cluster.master.AMEvent;
import com.alibaba.flink.ml.cluster.master.AMEventType;
import com.alibaba.flink.ml.cluster.master.AMService;
import com.alibaba.flink.ml.cluster.master.AMStateMachineFactory;
import com.alibaba.flink.ml.cluster.master.AbstractAMStateMachine;
import com.alibaba.flink.ml.cluster.master.HeartbeatListener;
import com.alibaba.flink.ml.cluster.node.MLContext;
import com.alibaba.flink.ml.cluster.master.meta.AMMetaImpl;
import com.alibaba.flink.ml.cluster.master.meta.AMMeta;
import com.alibaba.flink.ml.proto.*;
import com.alibaba.flink.ml.util.*;
import io.grpc.BindableService;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * application master rpc server.
 *      management machine learning cluster life cycle.
 *      accept node register, finish, failed etc.
 */
public class AppMasterServer implements Runnable {
	private static final Logger LOG = LoggerFactory.getLogger(AppMasterServer.class);

	private Server server;
	private final AtomicBoolean end;
	private final AMMeta amMeta;
	private final AbstractAMStateMachine amStateMachine;
	private final AMService appMasterService;
	private volatile long rpcLastContact;
	private final long rpcContactTimeout;
	private volatile Throwable error = null;

	public AppMasterServer(MLContext mlContext) {
		rpcContactTimeout = Long.parseLong(mlContext.getProperties().getOrDefault(
				MLConstants.SERVER_RPC_CONTACT_TIMEOUT, MLConstants.SERVER_RPC_CONTACT_TIMEOUT_DEFAULT));
		Map<String, String> properties = mlContext.getProperties();
		if (properties.containsKey(MLConstants.AM_STATE_CLASS)) {
			String className = properties.get(MLConstants.AM_STATE_CLASS);
			Class[] classes = new Class[1];
			classes[0] = MLContext.class;
			Object[] objects = new Object[1];
			objects[0] = mlContext;
			try {
				this.amMeta = ReflectUtil.createInstance(className, classes, objects);
			} catch (Exception e) {
				e.printStackTrace();
				throw new RuntimeException(e);
			}
		} else {
			this.amMeta = new AMMetaImpl(mlContext);
		}
		// If we use the restart-all strategy, we should clear the old states and start all over again
		// TODO: use ephemeral ZK node?
		if (MLConstants.FAILOVER_RESTART_ALL_STRATEGY.equalsIgnoreCase(
				mlContext.getProperties().getOrDefault(MLConstants.FAILOVER_STRATEGY,
						MLConstants.FAILOVER_STRATEGY_DEFAULT))) {
			amMeta.clear();
		}
		this.end = new AtomicBoolean(false);

		// eventReporter
		BaseEventReporter eventReporter;
		if (properties.containsKey(MLConstants.CONFIG_EVENT_REPORTER)) {
			String className = properties.get(MLConstants.CONFIG_EVENT_REPORTER);
			try {
				eventReporter = ReflectUtil.createInstance(className, new Class[0], new Object[0]);
			} catch (Exception e) {
				throw new RuntimeException(e);
			}
		} else {
			eventReporter = new LogBaseEventReporter();
		}

		if (eventReporter != null) {
			String jobName = properties.getOrDefault(MLConstants.CONFIG_JOB_NAME, "flink-ml");
			jobName += properties.get(MLConstants.JOB_VERSION);
			eventReporter.configure(jobName, properties);
		}

		int nodeNumSum = 0;
		for (Integer i : mlContext.getRoleParallelismMap().values()) {
			nodeNumSum += i;
		}
		this.appMasterService = new AppMasterServiceImpl(this, nodeNumSum,
				Duration.ofMillis(Long.parseLong(mlContext.getProperties().getOrDefault(
				MLConstants.HEARTBEAT_TIMEOUT, MLConstants.HEARTBEAT_TIMEOUT_DEFAULT))));

		// am state machine
		try {
			amStateMachine = AMStateMachineFactory
					.getAMStateMachine(appMasterService, amMeta, mlContext, eventReporter);
		} catch (MLException e) {
			e.printStackTrace();
			throw new RuntimeException(e);
		}

	}

	@Override
	public void run() {
		Runtime.getRuntime().addShutdownHook(new Thread(() -> {
			// Use stderr here since the logger may has been reset by its JVM shutdown hook.
			if (AppMasterServer.this.server != null) {
				LOG.error("*** shutting down gRPC server since JVM is shutting down");
				AppMasterServer.this.cleanup();
				LOG.error("*** AM server shut down");
			}
		}));
		try {
			updateRpcLastContact();
			this.server = ServerBuilder.forPort(0)
					.addService((BindableService)appMasterService).build();
			this.server.start();
			this.end.set(false);
			LOG.info("App Master Server started, listening on " + server.getPort());
			amMeta.saveAMIpPort(IpHostUtil.getIpAddress(), server.getPort());
			amStateMachine.handle(new AMEvent(AMEventType.INTI_AM_STATE, null, 0));

			while (!getEnd()) {
				long duration = System.currentTimeMillis() - rpcLastContact;
				if (duration > rpcContactTimeout) {
					throw new MLException(String.format("%d seconds elapsed since last grpc contact",
							duration / 1000));
				}
				Thread.sleep(1000);
			}
			if (error != null) {
				throw new MLException("Error encountered in AM", error);
			}
		} catch (InterruptedException e) {
			LOG.warn("AM server interrupted");
		} catch (Exception e) {
			LOG.error("Fail to execute AM.");
			throw new RuntimeException(e);
		} finally {
			cleanup();
		}
	}

	public void updateRpcLastContact() {
		rpcLastContact = System.currentTimeMillis();
	}

	/** Stop serving requests and shutdown resources. */
	private void cleanup() {
		LOG.info("Clean up AM node.");
		try {
			LOG.info("before clean up am node, sleep 10 seconds to wait for node complete stop.");
			Thread.sleep(10*1000);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		if (server != null) {
			server.shutdownNow();
			try {
				server.awaitTermination(2, TimeUnit.MINUTES);
			} catch (InterruptedException e) {
				e.printStackTrace();
				LOG.error("Interrupted shutting down GRPC server.");
			}
			server = null;
		}
		LOG.info("stop am service!");
		if (amMeta != null) {
			amMeta.close();
		}
		LOG.info("stop am meta!");
		if (null != amStateMachine) {
			amStateMachine.close();
		}
		LOG.info("stop am state machine!");
		this.end.set(true);
		appMasterService.stopHeartBeatMonitorAllNode();
		LOG.info("stop heartbeat all nodes!");
		LOG.info("app master server stopped.");
	}

	public int getPort() {
		if (null == server) {
			return -1;
		} else {
			return server.getPort();
		}
	}

	private boolean getEnd() {
		return end.get();
	}

	public void setEnd(boolean end) {
		this.end.set(end);
	}

	public synchronized void onError(Throwable t) {
		if (error != null) {
			error = t;
		}
		setEnd(true);
	}

	public AbstractAMStateMachine getAmStateMachine() {
		return amStateMachine;
	}

	public AMService getAppMasterService() {
		return appMasterService;
	}

	public AMMeta getAmMeta() {
		return amMeta;
	}

	/**
	 * @param nodeSpec node information.
	 * @return node identity.
	 */
	public static String getNodeClientKey(NodeSpec nodeSpec) {
		return nodeSpec.getRoleName() + "_" + nodeSpec.getIndex();
	}

}
