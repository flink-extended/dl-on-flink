package com.alibaba.flink.ml.util;

import com.alibaba.flink.ml.cluster.ExecutionMode;
import com.alibaba.flink.ml.cluster.MLConfig;
import com.alibaba.flink.ml.cluster.node.MLContext;
import com.alibaba.flink.ml.cluster.role.WorkerRole;
import org.junit.Before;
import org.junit.Test;

import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.Assert.*;

public class PythonUtilTest {

	private MLContext mlContext;

	@Before
	public void setUp() throws Exception {
		final MLConfig mlConfig = DummyContext.createDummyMLConfig();
		final URL resource = FileUtil.class.getClassLoader().getResource("venv.zip");
		assertNotNull(resource);
		mlContext = new MLContext(ExecutionMode.TRAIN, mlConfig, new WorkerRole().name(), 0,
				resource.toString(), null);
		Path workDir = Files.createTempDirectory(FileUtilTest.class.getName());
		mlContext.getProperties().put(MLConstants.WORK_DIR, workDir.toFile().getAbsolutePath());
	}

	@Test
	public void testSetupVirtualEnvProcess() throws IOException {
		PythonUtil.setupVirtualEnv(mlContext);
		assertNotEquals("", mlContext.getEnvProperty(MLConstants.LD_LIBRARY_PATH));
		final String pythonEnvPath = mlContext.getEnvProperty(MLConstants.PYTHONPATH_ENV);
		assertTrue(new File(pythonEnvPath).exists());
		assertTrue(new File(pythonEnvPath, "test.py").exists());
	}

	@Test
	public void testSetupVirtualEnv() throws IOException {
		ProcessBuilder builder = new ProcessBuilder("echo", "hello");
		PythonUtil.setupVirtualEnvProcess(mlContext, builder);
		assertNotNull(builder.environment().get(MLConstants.LD_LIBRARY_PATH));
		final String pythonEnvPath = builder.environment().get(MLConstants.PYTHONPATH_ENV);
		assertTrue(new File(pythonEnvPath).exists());
		assertTrue(new File(pythonEnvPath, "test.py").exists());
	}
}