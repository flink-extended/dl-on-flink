package org.flinkextended.flink.ml.cluster.node.runner.python.log;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.util.DummyContext;
import org.flinkextended.flink.ml.util.MLConstants;
import org.junit.Test;

import static org.hamcrest.CoreMatchers.instanceOf;
import static org.junit.Assert.*;

public class ProcessOutputConsumerFactoryTest {
	@Test
	public void testGetDefaultLoggerConsumer() {
		final AbstractProcessOutputConsumer loggerConsumer =
				ProcessOutputConsumerFactory.createMLRunner(DummyContext.createDummyMLContext());
		assertTrue(loggerConsumer instanceof StdOutErrorProcessOutputConsumer);
	}

	@Test
	public void testGetLoggerConsumer() {
		final MLContext mlContext = DummyContext.createDummyMLContext();
		mlContext.getProperties().put(MLConstants.PYTHON_PROCESS_LOGGER_CONSUMER_CLASS, TestProcessOutputConsumer.class.getCanonicalName());
		final AbstractProcessOutputConsumer loggerConsumer = ProcessOutputConsumerFactory.createMLRunner(mlContext);
		assertThat(loggerConsumer, instanceOf(TestProcessOutputConsumer.class));
	}

}