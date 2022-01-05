package org.flinkextended.flink.ml.cluster.node.runner.python.log;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.function.Consumer;

public class Slf4JProcessOutputConsumer extends AbstractProcessOutputConsumer {
	private final Logger logger;

	public Slf4JProcessOutputConsumer(MLContext mlContext) {
		super(mlContext);
		logger = LoggerFactory.getLogger(mlContext.getIdentity());
	}

	@Override
	Consumer<String> getStdOutConsumer() {
		return logger::info;
	}

	@Override
	Consumer<String> getStdErrConsumer() {
		return logger::error;
	}
}
