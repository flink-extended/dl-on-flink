/*
 * Copyright 2022 Deep Learning on Flink Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.flinkextended.flink.ml.tensorflow.client;

import org.flinkextended.flink.ml.tensorflow.storage.DummyStorage;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.SysUtil;

import org.apache.flink.core.execution.JobClient;
import org.apache.flink.runtime.client.JobCancellationException;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.bridge.java.StreamStatementSet;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.URL;
import java.time.Duration;
import java.util.concurrent.ExecutionException;

import static org.apache.flink.api.common.JobStatus.RUNNING;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/** Failover unit test. */
public class RunWithFailTest {

    private static final Logger LOG = LoggerFactory.getLogger(RunWithFailTest.class);

    private static final String simple_print = getScriptPathFromResources("simple_print.py");
    private static final String failover = getScriptPathFromResources("failover.py");
    private static final String failover2 = getScriptPathFromResources("failover2.py");
    private static final String alwaysFail = getScriptPathFromResources("always_fail.py");
    private StreamStatementSet statementSet;
    private StreamExecutionEnvironment env;
    private StreamTableEnvironment tEnv;

    @Before
    public void setUp() {
        env = StreamExecutionEnvironment.getExecutionEnvironment();
        tEnv = StreamTableEnvironment.create(env);
        statementSet = tEnv.createStatementSet();
    }

    private TFClusterConfig buildTFConfig(String pyFile) {
        return buildTFConfig(pyFile, String.valueOf(System.currentTimeMillis()), 2, 1);
    }

    private TFClusterConfig buildTFConfig(String pyFile, String version, int worker, int ps) {
        System.out.println("buildTFConfig: " + SysUtil._FUNC_());
        System.out.println("Current version:" + version);
        return TFClusterConfig.newBuilder()
                .setWorkerCount(worker)
                .setPsCount(ps)
                .setNodeEntry(pyFile, "map_func")
                .build();
    }

    @Test
    public void simpleStartupTest() throws Exception {
        TFClusterConfig config = buildTFConfig(simple_print, "1", 1, 1);

        TFUtils.train(statementSet, config);
        statementSet.execute().await();
    }

    @Test
    public void workerFailoverTest() throws Exception {
        LOG.info("############ Start failover test.");
        TFClusterConfig config =
                buildTFConfig(failover, String.valueOf(System.currentTimeMillis()), 2, 1);

        TFUtils.train(statementSet, config);
        statementSet.execute().await();
    }

    @Test
    public void testFailoverWithFinishedNode() throws Exception {
        TFClusterConfig config =
                buildTFConfig(failover2, String.valueOf(System.currentTimeMillis()), 2, 1);

        TFUtils.train(statementSet, config);
        statementSet.execute().await();
    }

    @Rule public ExpectedException expectedException = ExpectedException.none();

    @Test
    public void testJobTimeout() throws Exception {
        TFClusterConfig tfConfig = buildTFConfig(simple_print);
        tfConfig =
                tfConfig.toBuilder()
                        .setWorkerCount(1)
                        .setProperty(MLConstants.CONFIG_STORAGE_TYPE, MLConstants.STORAGE_CUSTOM)
                        .setProperty(MLConstants.STORAGE_IMPL_CLASS, DummyStorage.class.getName())
                        .setProperty(
                                MLConstants.AM_REGISTRY_TIMEOUT,
                                String.valueOf(Duration.ofSeconds(10).toMillis()))
                        .setProperty(
                                MLConstants.NODE_IDLE_TIMEOUT,
                                String.valueOf(Duration.ofSeconds(10).toMillis()))
                        .build();

        TFUtils.train(statementSet, tfConfig);

        expectedException.expect(ExecutionException.class);
        expectedException.expectMessage("Failed to wait job finish");
        statementSet.execute().await();
    }

    @Test
    public void testCancelWhileFailover() throws InterruptedException, ExecutionException {
        Table table = tEnv.fromDataStream(env.fromElements(1, 2, 3, 4));
        TFClusterConfig config = buildTFConfig(alwaysFail);
        TFUtils.train(statementSet, config);
        //        statementSet.execute()

        final JobClient jobClient = statementSet.execute().getJobClient().get();
        while (jobClient.getJobStatus().get() != RUNNING) {
            Thread.sleep(1000);
        }
        Thread.sleep(10_000);
        jobClient.cancel().get();
        while (jobClient.getJobStatus().get() == RUNNING) {
            Thread.sleep(1000);
        }

        try {
            jobClient.getJobExecutionResult().get();
        } catch (ExecutionException e) {
            assertTrue(e.getCause() instanceof JobCancellationException);
        }
    }

    @Test
    public void testTrainWithInputCancelWhileFailover()
            throws InterruptedException, ExecutionException {
        Table table = tEnv.fromDataStream(env.fromElements(1, 2, 3, 4));
        TFClusterConfig config = buildTFConfig(alwaysFail);
        TFUtils.train(statementSet, table, config);
        //        statementSet.execute()

        final JobClient jobClient = statementSet.execute().getJobClient().get();
        while (jobClient.getJobStatus().get() != RUNNING) {
            Thread.sleep(1000);
        }
        Thread.sleep(10_000);
        jobClient.cancel().get();
        while (jobClient.getJobStatus().get() == RUNNING) {
            Thread.sleep(1000);
        }

        try {
            jobClient.getJobExecutionResult().get();
        } catch (ExecutionException e) {
            assertTrue(e.getCause() instanceof JobCancellationException);
        }
    }

    private static String getScriptPathFromResources(String fileName) {
        final URL resource = Thread.currentThread().getContextClassLoader().getResource(fileName);
        assertNotNull(resource);
        return resource.getPath();
    }
}
