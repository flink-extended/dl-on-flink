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

package org.flinkextended.flink.ml.pytorch;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.rpc.NodeServer;
import org.flinkextended.flink.ml.proto.NodeSpec;
import org.flinkextended.flink.ml.cluster.node.runner.CommonMLRunner;
import org.flinkextended.flink.ml.util.IpHostUtil;

/**
 * PyTorch node machine learning scriptRunner.
 */
public class PyTorchRunner extends CommonMLRunner {

	public PyTorchRunner(MLContext mlContext, NodeServer server) {
		super(mlContext, server);
	}

	/**
	 * create PyTorch cluster node information.
	 * @param reset true: create new node information.
	 * @return PyTorch cluster node information.
	 * @throws Exception
	 */
	@Override
	protected NodeSpec createNodeSpec(boolean reset) throws Exception {
		if (reset || (null == nodeSpec)) {
			NodeSpec.Builder builder = NodeSpec.newBuilder()
					.setIp(localIp)
					.setIndex(mlContext.getIndex())
					.setClientPort(server.getPort())
					.setRoleName(mlContext.getRoleName());
			if (0 == mlContext.getIndex()) {
				int port = IpHostUtil.getFreePort();
				builder.putProps(PyTorchConstants.PYTORCH_MASTER_IP, localIp);
				builder.putProps(PyTorchConstants.PYTORCH_MASTER_PORT, String.valueOf(port));
			}
			nodeSpec = builder.build();
		}
		return nodeSpec;
	}

}
