package org.flinkextended.flink.ml.cluster.node.runner.python.log;

import org.flinkextended.flink.ml.util.DummyContext;
import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.assertEquals;

public class ProcessLoggerTest {
	@Test
	public void testProcessLoggerStdOut() throws IOException, InterruptedException {
		final ProcessBuilder builder = new ProcessBuilder("echo", "hello");
		final Process process = builder.start();

		final TestProcessOutputConsumer consumer = new TestProcessOutputConsumer(DummyContext.createDummyMLContext());
		final ProcessLogger logger = new ProcessLogger("test", process, consumer);
		logger.start_logging();
		process.waitFor();
		while (consumer.getStdOutLog().size() == 0) {
			Thread.sleep(100);
		}
		assertEquals("hello", consumer.getStdOutLog().get(0));
	}

	@Test
	public void testProcessLoggerStdErr() throws IOException, InterruptedException {
		final ProcessBuilder builder =
				new ProcessBuilder("python", "-c", "import sys;sys.stderr.write('error')");
		final Process process = builder.start();

		final TestProcessOutputConsumer consumer = new TestProcessOutputConsumer(DummyContext.createDummyMLContext());
		final ProcessLogger logger = new ProcessLogger("test", process, consumer);
		logger.start_logging();
		process.waitFor();
		while (consumer.getStdErrLog().size() == 0) {
			Thread.sleep(100);
		}
		assertEquals("error", consumer.getStdErrLog().get(0));
	}
}