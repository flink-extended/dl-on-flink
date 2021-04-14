package com.alibaba.flink.ml.cluster.node.runner.python.log;

import com.alibaba.flink.ml.cluster.node.MLContext;

import java.util.function.Consumer;

public abstract class AbstractProcessOutputConsumer {
	protected final MLContext mlContext;

	AbstractProcessOutputConsumer(MLContext mlContext) {
		this.mlContext = mlContext;
	}

	/**
	 * @return the consumer that consumes the stdout from the python process.
	 */
	abstract Consumer<String> getStdOutConsumer();

	/**
	 * @return the consumer that consumes the stderr from the python process.
	 */
	abstract Consumer<String> getStdErrConsumer();
}
