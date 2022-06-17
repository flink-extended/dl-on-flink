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

package org.flinkextended.flink.ml.pytorch;

import org.apache.flink.core.execution.JobClient;
import org.apache.flink.runtime.client.JobCancellationException;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.bridge.java.StreamStatementSet;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;

import org.junit.Before;
import org.junit.Test;

import java.net.URL;
import java.util.concurrent.ExecutionException;

import static org.apache.flink.api.common.JobStatus.RUNNING;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/** Test for failover. */
public class FailOverTest {

    private StreamExecutionEnvironment env;
    private StreamTableEnvironment tEnv;
    private StreamStatementSet statementSet;
    private final String alwaysFail = getScriptPathFromResources("always_fail.py");

    @Before
    public void setUp() {
        env = StreamExecutionEnvironment.getExecutionEnvironment();
        tEnv = StreamTableEnvironment.create(env);
        statementSet = tEnv.createStatementSet();
    }

    @Test
    public void testCancelWhileFailover() throws InterruptedException, ExecutionException {
        PyTorchClusterConfig config = buildTFConfig(alwaysFail);
        PyTorchUtils.train(statementSet, config);

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
        PyTorchClusterConfig config = buildTFConfig(alwaysFail);
        PyTorchUtils.train(statementSet, table, config);
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

    private PyTorchClusterConfig buildTFConfig(String pyFile) {
        return PyTorchClusterConfig.newBuilder()
                .setWorldSize(3)
                .setNodeEntry(pyFile, "map_func")
                .build();
    }

    private static String getScriptPathFromResources(String fileName) {
        final URL resource = Thread.currentThread().getContextClassLoader().getResource(fileName);
        assertNotNull(resource);
        return resource.getPath();
    }
}
