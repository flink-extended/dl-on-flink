package org.flinkextended.flink.ml.cluster.node.runner;

import org.flinkextended.flink.ml.util.MLException;

/**
 * throw exception cause by flink kill signal.
 */
public class FlinkKillException extends MLException {
	public FlinkKillException(String message) {
		super(message);
	}

	public FlinkKillException(String message, Throwable cause) {
		super(message, cause);
	}
}
