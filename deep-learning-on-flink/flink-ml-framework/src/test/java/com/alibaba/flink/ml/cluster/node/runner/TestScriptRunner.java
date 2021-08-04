package com.alibaba.flink.ml.cluster.node.runner;

import com.alibaba.flink.ml.cluster.node.MLContext;

import java.io.IOException;

public class TestScriptRunner extends AbstractScriptRunner {
	private boolean ran = false;

	public TestScriptRunner(MLContext mlContext) {
		super(mlContext);
	}

	@Override
	public void runScript() throws IOException {
		ran = true;
		// do nothing
	}

	@Override
	public void notifyKillSignal() {
		// do nothing
	}

	public boolean isRan() {
		return ran;
	}
}
