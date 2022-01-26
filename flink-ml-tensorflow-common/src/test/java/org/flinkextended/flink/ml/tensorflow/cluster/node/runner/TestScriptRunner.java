package org.flinkextended.flink.ml.tensorflow.cluster.node.runner;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.node.runner.AbstractScriptRunner;

import java.io.IOException;

public class TestScriptRunner extends AbstractScriptRunner {

	public TestScriptRunner(MLContext mlContext) {
		super(mlContext);
	}

	@Override
	public void runScript() throws IOException {

	}

	@Override
	public void notifyKillSignal() {

	}

	@Override
	public void close() throws IOException {

	}
}
