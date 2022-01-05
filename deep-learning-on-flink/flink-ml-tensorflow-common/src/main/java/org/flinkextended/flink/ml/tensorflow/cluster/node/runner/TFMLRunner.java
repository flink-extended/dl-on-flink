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

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.node.runner.CommonMLRunner;
import org.flinkextended.flink.ml.cluster.role.WorkerRole;
import org.flinkextended.flink.ml.cluster.rpc.NodeServer;
import org.flinkextended.flink.ml.proto.ContextProto;
import org.flinkextended.flink.ml.proto.NodeSpec;
import org.flinkextended.flink.ml.tensorflow.cluster.ChiefRole;
import org.flinkextended.flink.ml.tensorflow.cluster.TensorBoardRole;
import org.flinkextended.flink.ml.tensorflow.util.TFConstants;
import org.flinkextended.flink.ml.util.IpHostUtil;
import org.flinkextended.flink.ml.util.MLConstants;
import org.apache.commons.io.IOUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.ServerSocket;

/**
 * tensorflow machine learning runner.
 * tensorflow NodeSpec generate tensorflow server port.
 */
public class TFMLRunner extends CommonMLRunner {
	private static Logger LOG = LoggerFactory.getLogger(TFMLRunner.class);
	protected ServerSocket serverSocket;

	public TFMLRunner(MLContext MLContext, NodeServer server) {
		super(MLContext, server);
	}

	@Override
	public void registerNode() throws Exception {
		long startTime = System.currentTimeMillis();
		// we can register while running if
		// the failover strategy only restart individual tasks or this is tensorboard
		final boolean isTB = mlContext.getRoleName().equalsIgnoreCase(new TensorBoardRole().name());
		final boolean registerWhileRunning = mlContext.getProperties().getOrDefault(
				MLConstants.FAILOVER_STRATEGY, MLConstants.FAILOVER_STRATEGY_DEFAULT)
				.equalsIgnoreCase(MLConstants.FAILOVER_RESTART_INDIVIDUAL_STRATEGY) || isTB;
		doRegisterAction(startTime, registerWhileRunning);
	}

	@Override
	protected NodeSpec createNodeSpec(boolean reset) throws Exception {
		if (reset || (null == nodeSpec)) {
			if (serverSocket != null) {
				serverSocket.close();
			}
			boolean isWorkerZeroAlone = Boolean.valueOf(mlContext.getProperties()
					.getOrDefault(TFConstants.TF_IS_CHIEF_ALONE, "false"));
			NodeSpec.Builder builder = NodeSpec.newBuilder()
					.setIp(localIp)
					.setClientPort(server.getPort());
			if (isWorkerZeroAlone) {
				if (new ChiefRole().name().equals(mlContext.getRoleName())) {
					builder.setIndex(0);
					builder.setRoleName(new WorkerRole().name());
				} else if (new WorkerRole().name().equals(mlContext.getRoleName())) {
					builder.setIndex(mlContext.getIndex() + 1);
					builder.setRoleName(mlContext.getRoleName());
				} else {
					builder.setIndex(mlContext.getIndex())
							.setRoleName(mlContext.getRoleName());
				}
			} else {
				builder.setIndex(mlContext.getIndex())
						.setRoleName(mlContext.getRoleName());
			}
			serverSocket = IpHostUtil.getFreeSocket();
			builder.putProps(TFConstants.TF_PORT, String.valueOf(serverSocket.getLocalPort()));
			nodeSpec = builder.build();
		}
		return nodeSpec;
	}


	@Override
	public void resetMLContext() {
		super.resetMLContext();
		resetMlContextProto();
	}

	@Override
	public void startHeartBeat() throws Exception {
		if(!new TensorBoardRole().name().equals(mlContext.getRoleName())) {
			super.startHeartBeat();
		}
		serverSocket.close();
	}

	/**
	 * if tensorflow worker 0 plan as a single role, adjust the task index.
	 */
	private void resetMlContextProto() {
		// maybe reset mlContext ContextProto
		boolean isWorkerZeroAlone = Boolean.valueOf(mlContext.getProperties()
				.getOrDefault(TFConstants.TF_IS_CHIEF_ALONE, "false"));
		ContextProto.Builder builder = mlContext.toPBBuilder();
		if (isWorkerZeroAlone) {
			if (new ChiefRole().name().equals(mlContext.getRoleName())) {
				builder.setIndex(0);
				builder.setRoleName(new WorkerRole().name());
			} else if (new WorkerRole().name().equals(mlContext.getRoleName())) {
				builder.setIndex(mlContext.getIndex() + 1);
				builder.setRoleName(mlContext.getRoleName());
			}
			mlContext.setContextProto(builder.build());
		}
	}



	@Override
	protected void stopExecution(boolean success) {
		if (null != serverSocket) {
			IOUtils.closeQuietly(serverSocket);
			serverSocket = null;
		}
		super.stopExecution(success);
	}
}
