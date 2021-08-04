package com.alibaba.flink.ml.cluster.rpc;

import com.alibaba.flink.ml.cluster.ExecutionMode;
import com.alibaba.flink.ml.cluster.MLConfig;
import com.alibaba.flink.ml.cluster.node.MLContext;
import com.alibaba.flink.ml.cluster.role.WorkerRole;
import com.alibaba.flink.ml.util.DummyContext;
import com.alibaba.flink.ml.util.FileUtil;
import com.alibaba.flink.ml.util.MLConstants;
import org.apache.commons.io.FileUtils;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.net.URL;
import java.util.List;

import static org.junit.Assert.*;

public class NodeServerTest {
	private static final Logger LOG = LoggerFactory.getLogger(NodeServerTest.class);
	private MLContext mlContext;

	@Before
	public void setUp() throws Exception {
		MLConfig mlConfig = DummyContext.createDummyMLConfig();
		mlContext = new MLContext(ExecutionMode.TRAIN, mlConfig, new WorkerRole().name(),
				0, null, null);
	}

	@After
	public void tearDown() throws Exception {
		FileUtils.deleteDirectory(mlContext.getWorkDir());
	}

	@Test
	public void testRun() throws InterruptedException {
		mlContext.getProperties().put(MLConstants.ML_RUNNER_CLASS, TestMLRunner.class.getCanonicalName());
		final NodeServer nodeServer = new NodeServer(mlContext, "test_job");
		final Thread t = new Thread(nodeServer);
		t.start();

		TestMLRunner runner = (TestMLRunner) nodeServer.getRunner();
		while (runner == null) {
			runner = (TestMLRunner) nodeServer.getRunner();
			Thread.sleep(1000);
			LOG.info("waiting for runner {}", runner);
		}
		assertTrue(runner.isRunning());

		nodeServer.setAmCommand(NodeServer.AMCommand.STOP);
		t.join();
		assertFalse(runner.isRunning());
	}

	@Test
	public void testPrepareStartupScript() {
		NodeServer.prepareStartupScript(mlContext);
		String scriptPath = mlContext.getProperties().get(MLConstants.STARTUP_SCRIPT_FILE);
		assertNotNull(scriptPath);
		assertTrue(new File(scriptPath).exists());
	}

	@Test
	public void testPrepareRuntimeEnv() {
		final URL resource = FileUtil.class.getClassLoader().getResource("test-code.zip");
		assertNotNull(resource);
		mlContext.getProperties().put(MLConstants.REMOTE_CODE_ZIP_FILE, resource.toString());
		mlContext.setPythonFiles(new String[]{"code.py"});
		mlContext.getProperties().put(MLConstants.USER_ENTRY_PYTHON_FILE, "code.py");
		NodeServer.prepareRuntimeEnv(mlContext);

		final List<String> pythonFiles = mlContext.getPythonFiles();
		assertEquals(1, pythonFiles.size());
		assertEquals("code.py", pythonFiles.get(0));
		assertTrue(mlContext.getPythonDir().resolve(pythonFiles.get(0)).toFile().exists());
	}

}