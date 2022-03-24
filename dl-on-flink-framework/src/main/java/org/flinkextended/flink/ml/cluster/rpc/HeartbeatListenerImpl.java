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

import org.flinkextended.flink.ml.cluster.master.AMEvent;
import org.flinkextended.flink.ml.cluster.master.AMEventType;
import org.flinkextended.flink.ml.cluster.master.HeartbeatListener;
import org.flinkextended.flink.ml.proto.NodeSpec;
import org.flinkextended.flink.ml.proto.RegisterFailedNodeRequest;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class HeartbeatListenerImpl implements HeartbeatListener {

    private static final Logger LOG = LoggerFactory.getLogger(HeartbeatListenerImpl.class);

    private final AppMasterServer appMasterServer;
    private final NodeSpec nodeSpec;
    private final long version;

    HeartbeatListenerImpl(AppMasterServer appMasterServer, NodeSpec nodeSpec, long version) {
        this.appMasterServer = appMasterServer;
        this.nodeSpec = nodeSpec;
        this.version = version;
    }

    @Override
    public void notifyHeartbeatTimeout() {
        LOG.info(
                "Lost heartbeat of {}, marking it as failed",
                AppMasterServer.getNodeClientKey(nodeSpec));
        RegisterFailedNodeRequest.Builder builder = RegisterFailedNodeRequest.newBuilder();
        builder.setVersion(version).setNodeSpec(nodeSpec).setMessage("heartbeat timeout");
        RegisterFailedNodeRequest request = builder.build();
        try {
            // We assume the heartbeat timeout is caused by issues in BaseMLRunner, so we can go
            // through the FAIL_NODE
            // process (i.e. ask the node to restart)
            // We rely on Flink to handle cases like network partition, where the node can't be
            // contacted
            appMasterServer
                    .getAmStateMachine()
                    .handle(new AMEvent(AMEventType.FAIL_NODE, request, request.getVersion()));
        } catch (Exception e) {
            appMasterServer.getAppMasterService().handleStateTransitionError(request, e);
        }
    }
}
