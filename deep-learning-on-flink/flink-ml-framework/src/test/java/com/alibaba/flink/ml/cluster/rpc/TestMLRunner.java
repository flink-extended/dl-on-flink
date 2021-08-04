package com.alibaba.flink.ml.cluster.rpc;

import com.alibaba.flink.ml.cluster.node.MLContext;
import com.alibaba.flink.ml.cluster.node.runner.ExecutionStatus;
import com.alibaba.flink.ml.cluster.node.runner.MLRunner;


public class TestMLRunner implements MLRunner {

	private final MLContext context;
	private final NodeServer server;

	private boolean running;

	public TestMLRunner(MLContext context, NodeServer server) {
		this.context = context;
		this.server = server;
	}

	@Override
	public void initAMClient() throws Exception {

	}

	@Override
	public void getCurrentJobVersion() throws Exception {

	}

	@Override
	public void registerNode() throws Exception {

	}

	@Override
	public void startHeartBeat() throws Exception {

	}

	@Override
	public void waitClusterRunning() throws Exception {

	}

	@Override
	public void getClusterInfo() throws Exception {

	}

	@Override
	public void resetMLContext() throws Exception {

	}

	@Override
	public void runScript() throws Exception {
	}

	@Override
	public void notifyStop() throws Exception {
		running = false;
	}

	@Override
	public ExecutionStatus getResultStatus() {
		return null;
	}

	@Override
	public void run() {
		running = true;
	}

	public boolean isRunning() {
		return running;
	}
}
