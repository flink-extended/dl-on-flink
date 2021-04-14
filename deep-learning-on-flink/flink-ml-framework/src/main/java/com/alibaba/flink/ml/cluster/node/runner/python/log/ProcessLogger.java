package com.alibaba.flink.ml.cluster.node.runner.python.log;

import com.alibaba.flink.ml.util.ShellExec;
import org.mortbay.log.Log;

/**
 * ProcessLogger collects stdout and stderr of the given process and use the given
 * ${@link AbstractProcessOutputConsumer} to consume the stdout and stderr.
 */
public class ProcessLogger {
	private final String processIdentity;
	private final Process process;
	private final AbstractProcessOutputConsumer processOutputConsumer;

	public ProcessLogger(String processIdentity,
						 Process process,
						 AbstractProcessOutputConsumer processOutputConsumer) {
		this.processIdentity = processIdentity;
		this.process = process;
		this.processOutputConsumer = processOutputConsumer;
	}

	public void start_logging() {
		Log.info("Start logging process {} with {}", processIdentity, processOutputConsumer);
		Thread inLogger = new Thread(
				new ShellExec.ProcessLogger(process.getInputStream(),
						processOutputConsumer.getStdOutConsumer()));
		Thread errLogger = new Thread(
				new ShellExec.ProcessLogger(process.getErrorStream(),
						processOutputConsumer.getStdErrConsumer()));
		inLogger.setName(processIdentity + "-in-logger");
		inLogger.setDaemon(true);
		errLogger.setName(processIdentity + "-err-logger");
		errLogger.setDaemon(true);
		inLogger.start();
		errLogger.start();
	}
}
