package com.alibaba.flink.ml.cluster.node.runner.python.log;

import com.alibaba.flink.ml.cluster.node.MLContext;
import com.alibaba.flink.ml.util.MLConstants;
import com.alibaba.flink.ml.util.ReflectUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ProcessOutputConsumerFactory {
	private static final Logger LOG = LoggerFactory.getLogger(ProcessOutputConsumerFactory.class);
	public static AbstractProcessOutputConsumer createMLRunner(MLContext mlContext) {
		String className = mlContext.getProperties().get(MLConstants.PYTHON_PROCESS_LOGGER_CONSUMER_CLASS);
		
		// default logger consumer
		if (className == null) {
			LOG.info("property {} is not set. Python process log will send to stdout/stderr",
					MLConstants.PYTHON_PROCESS_LOGGER_CONSUMER_CLASS);
			return getDefaultLoggerConsumer(mlContext);
		}

		try {
			Class[] classes = new Class[1];
			classes[0] = MLContext.class;
			Object[] objects = new Object[1];
			objects[0] = mlContext;
			return ReflectUtil.createInstance(className, classes, objects);
		} catch (Exception e) {
			LOG.warn("Fail to instantiate ProcessLoggerConsumer {}. Process log will send to stdout/stderr",
					className, e);
		}

		return getDefaultLoggerConsumer(mlContext);
	}

	private static AbstractProcessOutputConsumer getDefaultLoggerConsumer(MLContext context) {
		return new StdOutErrorProcessOutputConsumer(context);
	}
}
