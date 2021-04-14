package com.alibaba.flink.ml.cluster.node.runner.python.log;

import com.alibaba.flink.ml.cluster.node.MLContext;
import com.alibaba.flink.ml.util.ShellExec;

import java.util.function.Consumer;

public class StdOutErrorProcessOutputConsumer extends AbstractProcessOutputConsumer {
	StdOutErrorProcessOutputConsumer(MLContext mlContext) {
		super(mlContext);
	}

	@Override
	public Consumer<String> getStdOutConsumer() {
		return new ShellExec.StdOutConsumer();
	}

	@Override
	public Consumer<String> getStdErrConsumer() {
		return new ShellExec.StdErrorConsumer();
	}
}
