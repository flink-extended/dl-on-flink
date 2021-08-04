package com.alibaba.flink.ml.cluster.node.runner;

import com.alibaba.flink.ml.cluster.ExecutionMode;
import com.alibaba.flink.ml.cluster.MLConfig;
import com.alibaba.flink.ml.cluster.node.MLContext;
import com.alibaba.flink.ml.cluster.role.AMRole;
import com.alibaba.flink.ml.cluster.rpc.AppMasterServer;
import com.alibaba.flink.ml.cluster.rpc.NodeServer;
import com.alibaba.flink.ml.proto.GetClusterInfoResponse;
import com.alibaba.flink.ml.proto.NodeSpec;
import com.alibaba.flink.ml.util.DummyContext;
import com.alibaba.flink.ml.util.MLConstants;
import com.alibaba.flink.ml.util.MLException;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.mockito.Mockito;

import java.util.Map;
import java.util.concurrent.FutureTask;

import static org.junit.Assert.*;

public class CommonMLRunnerTest {

	private static FutureTask<Void> amFuture;
	private static AppMasterServer amServer;

	private CommonMLRunner mlRunner;
	private NodeServer nodeServer;
	private static MLConfig mlConfig;
	private MLContext mlContext;

	@Before
	public void setUp() throws Exception {
		mlConfig = DummyContext.createDummyMLConfig();
		startAMServer(mlConfig);
		nodeServer = Mockito.mock(NodeServer.class);
		mlContext = DummyContext.createDummyMLContext();
		mlContext.getProperties().put(MLConstants.SCRIPT_RUNNER_CLASS,
				TestScriptRunner.class.getCanonicalName());
		mlRunner = Mockito.spy(new CommonMLRunner(mlContext, nodeServer));
		mlRunner.initAMClient();
		assertNotNull(mlRunner.amClient);
	}

	@After
	public void tearDown() throws Exception {
		amServer.setEnd(true);
		amFuture.get();
	}

	@Test
	public void testGetCurrentJobVersion() {
		mlRunner.getCurrentJobVersion();
		assertTrue(mlRunner.version > 0);
	}

	@Test
	public void testGetTaskIndex() throws MLException, InterruptedException {
		mlRunner.getCurrentJobVersion();
		mlRunner.mlContext.setIndex(-1);
		mlRunner.getTaskIndex();
		assertEquals(0, mlRunner.mlContext.getIndex());
	}

	@Test
	public void testRegisterNode() throws Exception {
		mlRunner.registerNode();
		final GetClusterInfoResponse clusterInfo = mlRunner.amClient.getClusterInfo(mlRunner.version);
		final Map<Integer, NodeSpec> tasksMap = clusterInfo.getClusterDef().getJob(0).getTasksMap();
		final NodeSpec nodeSpec = tasksMap.get(0);
		assertEquals(mlContext.getRoleName(), nodeSpec.getRoleName());
		assertEquals(mlContext.getIndex(), nodeSpec.getIndex());
	}

	@Test
	public void testStartHeartbeat() throws Exception {
		assertNull(mlRunner.getHeartBeatRunnerFuture());
		mlRunner.startHeartBeat();
		assertNotNull(mlRunner.getHeartBeatRunnerFuture());
		assertFalse(mlRunner.getHeartBeatRunnerFuture().isDone());
	}

	@Test
	public void testWaitClusterRunning() throws Exception {
		MLConstants.TIMEOUT = 1000;
		try {
			mlRunner.waitClusterRunning();
		} catch (MLException e) {
			// expected
		}
		mlRunner.registerNode();
		mlRunner.startHeartBeat();
		mlRunner.waitClusterRunning();
	}

	@Test
	public void testGetClusterInfo() throws Exception {
		MLConstants.TIMEOUT = 1000;
		mlRunner.getCurrentJobVersion();
		mlRunner.getClusterInfo();
		assertNull(mlRunner.mlClusterDef);

		mlRunner.registerNode();
		mlRunner.getClusterInfo();
		assertNotNull(mlRunner.mlClusterDef);
	}

	@Test
	public void testResetMLContext() throws Exception {
		mlRunner.getCurrentJobVersion();
		mlRunner.registerNode();
		mlRunner.getClusterInfo();
		assertNull(mlRunner.mlContext.getProperties().get(MLConstants.CONFIG_CLUSTER_PATH));
		mlRunner.resetMLContext();
		assertNotNull(mlRunner.mlContext.getProperties().get(MLConstants.CONFIG_CLUSTER_PATH));
	}

	@Test
	public void testRunScript() throws Exception {
		mlRunner.runScript();
		assertThat(mlRunner.scriptRunner, org.hamcrest.CoreMatchers.instanceOf(TestScriptRunner.class));
		final TestScriptRunner scriptRunner = (TestScriptRunner) mlRunner.scriptRunner;
		assertTrue(scriptRunner.isRan());

	}

	@Test
	public void testRun() throws Exception {
		mlRunner.run();
		Mockito.verify(mlRunner, Mockito.atLeastOnce()).initAMClient();
		Mockito.verify(mlRunner, Mockito.atLeastOnce()).getCurrentJobVersion();
		Mockito.verify(mlRunner).getTaskIndex();
		Mockito.verify(mlRunner).registerNode();
		Mockito.verify(mlRunner).startHeartBeat();
		Mockito.verify(mlRunner).waitClusterRunning();
		Mockito.verify(mlRunner).getClusterInfo();
		Mockito.verify(mlRunner).resetMLContext();
		Mockito.verify(mlRunner).runScript();
	}

	@Test
	public void testKillByFlink() throws InterruptedException {
		final Thread t = new Thread(mlRunner);
		t.start();
		while (mlRunner.currentResultStatus != ExecutionStatus.RUNNING) {
			Thread.sleep(100);
		}
		mlRunner.notifyStop();
		t.join();
		assertEquals(ExecutionStatus.KILLED_BY_FLINK, mlRunner.resultStatus);
	}

	private static FutureTask<Void> startAMServer(MLConfig mlConfig) throws MLException {
		MLContext amContext = new MLContext(ExecutionMode.TRAIN, mlConfig, new AMRole().name(), 0, null, null);
		amServer = new AppMasterServer(amContext);
		amFuture = new FutureTask<>(amServer, null);
		Thread thread = new Thread(amFuture);
		thread.setDaemon(true);
		thread.start();
		return amFuture;
	}
}