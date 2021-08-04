package com.alibaba.flink.ml.cluster.rpc;

import com.alibaba.flink.ml.cluster.master.AMEvent;
import com.alibaba.flink.ml.cluster.master.AMEventType;
import com.alibaba.flink.ml.cluster.master.HeartbeatListener;
import com.alibaba.flink.ml.proto.NodeSpec;
import com.alibaba.flink.ml.proto.RegisterFailedNodeRequest;
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
		LOG.info("Lost heartbeat of {}, marking it as failed", AppMasterServer.getNodeClientKey(nodeSpec));
		RegisterFailedNodeRequest.Builder builder = RegisterFailedNodeRequest.newBuilder();
		builder.setVersion(version).setNodeSpec(nodeSpec)
				.setMessage("heartbeat timeout");
		RegisterFailedNodeRequest request = builder.build();
		try {
			// We assume the heartbeat timeout is caused by issues in BaseMLRunner, so we can go through the FAIL_NODE
			// process (i.e. ask the node to restart)
			// We rely on Flink to handle cases like network partition, where the node can't be contacted
			appMasterServer.getAmStateMachine().handle(new AMEvent(AMEventType.FAIL_NODE, request, request.getVersion()));
		} catch (Exception e) {
			appMasterServer.getAppMasterService().handleStateTransitionError(request, e);
		}
	}
}
