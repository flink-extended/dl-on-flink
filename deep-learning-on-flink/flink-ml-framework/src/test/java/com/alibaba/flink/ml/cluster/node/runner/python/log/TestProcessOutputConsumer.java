package com.alibaba.flink.ml.cluster.node.runner.python.log;

import com.alibaba.flink.ml.cluster.node.MLContext;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

public class TestProcessOutputConsumer extends AbstractProcessOutputConsumer {
	private final List<String> stdOutLog = new ArrayList<>();
	private final List<String> stdErrLog = new ArrayList<>();
	public TestProcessOutputConsumer(MLContext mlContext) {
		super(mlContext);
	}

	@Override
	Consumer<String> getStdOutConsumer() {
		return stdOutLog::add;
	}

	@Override
	Consumer<String> getStdErrConsumer() {
		return stdErrLog::add;
	}

	public List<String> getStdOutLog() {
		return stdOutLog;
	}

	public List<String> getStdErrLog() {
		return stdErrLog;
	}
}
