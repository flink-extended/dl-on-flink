package org.flinkextended.flink.ml.tensorflow.util;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.util.DummyContext;
import io.grpc.Server;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.junit.Before;
import org.junit.Test;

import java.io.IOException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.FutureTask;

import static org.junit.Assert.*;

public class JavaInferenceUtilTest {

	private MLContext mlContext;

	@Before
	public void setUp() throws Exception {
		mlContext = DummyContext.createDummyMLContext();
	}

	@Test
	public void testStartTFContextService() throws Exception {
		final Server server = JavaInferenceUtil.startTFContextService(mlContext);
		assertFalse(server.isShutdown());
		assertFalse(server.isTerminated());
	}

	@Test
	public void testStartInferenceProcessWatcher() throws IOException, ExecutionException, InterruptedException {
		final Process process = new ProcessBuilder("echo", "hello").start();
		final FutureTask<Void> future = JavaInferenceUtil.startInferenceProcessWatcher(process, mlContext);
		future.get();
		assertFalse(process.isAlive());
	}

	@Test
	public void testLaunchInferenceProcess() throws IOException, InterruptedException {
		final Process process =
				JavaInferenceUtil.launchInferenceProcess(mlContext, new RowTypeInfo(Types.STRING), new RowTypeInfo(Types.STRING));
		final FutureTask<Void> future = JavaInferenceUtil.startInferenceProcessWatcher(process, mlContext);
		try {
			future.get();
		} catch (ExecutionException e) {
			// expected
		}
		assertFalse(process.isAlive());
	}
}