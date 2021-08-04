package com.alibaba.flink.ml.cluster.node;

import com.alibaba.flink.ml.cluster.ExecutionMode;
import com.alibaba.flink.ml.cluster.MLConfig;
import com.alibaba.flink.ml.proto.ContextProto;
import com.alibaba.flink.ml.util.DummyContext;
import com.alibaba.flink.ml.util.MLConstants;
import com.alibaba.flink.ml.util.MLException;
import org.junit.Before;
import org.junit.Test;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.Assert.*;

public class MLContextTest {

	private MLContext mlContext;
	private String envPath;

	@Before
	public void setUp() throws Exception {
		final MLConfig mlConfig = DummyContext.createDummyMLConfig();
		envPath = "/tmp/env_path";
		mlContext = new MLContext(ExecutionMode.TRAIN, mlConfig, "worker", 0, envPath,
				Collections.emptyMap());
	}

	@Test
	public void testGetEnvPath() {
		assertEquals(envPath, mlContext.getEnvPath());
	}

	@Test
	public void testGetPythonFiles() {
		String[] pythonFiles = new String[]{"file1.py", "file2.py"};
		mlContext.setPythonFiles(pythonFiles);
		assertEquals(Arrays.asList(pythonFiles), mlContext.getPythonFiles());
	}

	@Test
	public void testGetEnd() {
		mlContext.setEnd(99);
		assertEquals(99, mlContext.getEnd());
	}

	@Test
	public void testGetHookClassNames() {
		assertEquals(0, mlContext.getHookClassNames().size());

		mlContext.getProperties().put(MLConstants.FLINK_HOOK_CLASSNAMES, "org.example.hook,org.example.hook2");
		final List<String> hookClassNames = mlContext.getHookClassNames();
		assertEquals(2, hookClassNames.size());
		assertEquals(Arrays.asList("org.example.hook", "org.example.hook2"), hookClassNames);
	}

	@Test
	public void testBatchStreamMode() {
		assertTrue(mlContext.isBatchMode());
		assertFalse(mlContext.isStreamMode());

		mlContext.getProperties().put(MLConstants.CONFIG_JOB_HAS_INPUT, "true");
		assertFalse(mlContext.isBatchMode());
		assertTrue(mlContext.isStreamMode());
	}

	@Test
	public void testGetFailNum() {
		mlContext.setFailNum(99);
		assertEquals(99, mlContext.getFailNum());

		mlContext.addFailNum();
		assertEquals(100, mlContext.getFailNum());
	}

	@Test
	public void testGetMode() throws MLException {
		assertEquals(ExecutionMode.TRAIN.toString(), mlContext.getMode());

		MLContext context = new MLContext(null, DummyContext.createDummyMLConfig(), "worker", 0, envPath,
				Collections.emptyMap());
		assertEquals(ExecutionMode.OTHER.toString(), context.getMode());
	}

	@Test
	public void testFromPb() throws MLException {
		final ContextProto build = mlContext.toPBBuilder().build();
		final MLContext myMlConfig = MLContext.fromPB(build);
		assertEquals(mlContext.getMode(), myMlConfig.getMode());
	}

	@Test
	public void testClose() throws IOException {
		mlContext.close();
		assertNull(mlContext.inputQueueFile);
		assertNull(mlContext.outputQueueFile);
	}

	@Test
	public void testReset() {
		mlContext.reset();
		assertEquals(MLConstants.END_STATUS_NORMAL, mlContext.getEnd());
	}

	@Test
	public void testGetWorkDir() {
		final File workDir = mlContext.getWorkDir();
		assertTrue(workDir.exists());
		assertTrue(workDir.isDirectory());
		assertEquals(workDir.getAbsolutePath(), mlContext.getWorkDir().getAbsolutePath());
	}

	@Test
	public void testStartWithStartup() {
		assertTrue(mlContext.startWithStartup());

		mlContext.getProperties().put(MLConstants.START_WITH_STARTUP, "true");
		assertTrue(mlContext.startWithStartup());

		mlContext.getProperties().put(MLConstants.START_WITH_STARTUP, "false");
		assertFalse(mlContext.startWithStartup());
	}

	@Test
	public void testUseDistributedCache() {
		assertTrue(mlContext.useDistributeCache());
		mlContext.getProperties().put(MLConstants.REMOTE_CODE_ZIP_FILE, "/tmp/code.zip");
		assertFalse(mlContext.useDistributeCache());

		mlContext.getProperties().put(MLConstants.USE_DISTRIBUTE_CACHE, "true");
		assertTrue(mlContext.useDistributeCache());

		mlContext.getProperties().put(MLConstants.USE_DISTRIBUTE_CACHE, "false");
		assertFalse(mlContext.useDistributeCache());

	}
}