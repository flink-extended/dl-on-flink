/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
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

import org.flinkextended.flink.ml.tensorflow.client.StreamNodeMatchers.AMNodeMatcher;
import org.flinkextended.flink.ml.tensorflow.client.StreamNodeMatchers.IterativeNodeOperatorMatcher;
import org.flinkextended.flink.ml.tensorflow.client.StreamNodeMatchers.NodeOperatorMatcher;
import org.flinkextended.flink.ml.tensorflow.client.StreamNodeMatchers.SourceNodeMatcher;

import org.apache.flink.api.common.cache.DistributedCache;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.graph.StreamGraph;
import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableDescriptor;
import org.apache.flink.table.api.bridge.java.StreamStatementSet;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.delegation.Executor;

import org.junit.Before;
import org.junit.Test;
import org.mockito.internal.util.reflection.Whitebox;

import java.util.Collection;
import java.util.concurrent.ExecutionException;

import static org.hamcrest.CoreMatchers.hasItem;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.Assert.assertEquals;

/** Unit test for {@link TFUtils}. */
public class TFUtilsTest {

    private StreamStatementSet statementSet;
    private TestExecutor executor;
    private StreamExecutionEnvironment env;
    private StreamTableEnvironment tEnv;

    @Before
    public void setUp() throws Exception {
        env = StreamExecutionEnvironment.getExecutionEnvironment();
        tEnv = StreamTableEnvironment.create(env);
        final Executor execEnv = (Executor) Whitebox.getInternalState(tEnv, "execEnv");
        executor = new TestExecutor(execEnv);
        Whitebox.setInternalState(tEnv, "execEnv", executor);
        statementSet = tEnv.createStatementSet();
    }

    @Test
    public void testTrainNoInput() throws ExecutionException, InterruptedException {
        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setWorkerCount(3)
                        .setPsCount(2)
                        .setNodeEntry("entry.py", "main")
                        .build();
        TFUtils.train(statementSet, config);
        statementSet.execute().await();
        final StreamGraph streamGraph = (StreamGraph) executor.getPipeline();
        final Collection<Tuple2<String, DistributedCache.DistributedCacheEntry>> userArtifacts =
                streamGraph.getUserArtifacts();
        assertEquals(1, userArtifacts.size());
        assertEquals("entry.py", userArtifacts.iterator().next().f0);
        checkAMNodeExist(streamGraph);
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new SourceNodeMatcher(TFClusterConfig.WORKER_NODE_TYPE, 3)));
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new SourceNodeMatcher(TFClusterConfig.PS_NODE_TYPE, 2)));
    }

    @Test
    public void testTrainWithoutPs() throws ExecutionException, InterruptedException {
        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setWorkerCount(3)
                        .setNodeEntry("entry.py", "main")
                        .build();
        TFUtils.train(statementSet, config);
        statementSet.execute().await();
        final StreamGraph streamGraph = (StreamGraph) executor.getPipeline();
        final Collection<Tuple2<String, DistributedCache.DistributedCacheEntry>> userArtifacts =
                streamGraph.getUserArtifacts();
        assertEquals(1, userArtifacts.size());
        assertEquals("entry.py", userArtifacts.iterator().next().f0);
        checkAMNodeExist(streamGraph);
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new SourceNodeMatcher(TFClusterConfig.WORKER_NODE_TYPE, 3)));
    }

    @Test
    public void testTrainWithInput() throws ExecutionException, InterruptedException {
        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setPsCount(2)
                        .setWorkerCount(3)
                        .setNodeEntry("entry.py", "main")
                        .build();
        final Table sourceTable = tEnv.fromDataStream(env.fromElements(1, 2, 3));
        TFUtils.train(statementSet, sourceTable, config);
        statementSet.execute().await();
        final StreamGraph streamGraph = (StreamGraph) executor.getPipeline();
        final Collection<Tuple2<String, DistributedCache.DistributedCacheEntry>> userArtifacts =
                streamGraph.getUserArtifacts();
        assertEquals(1, userArtifacts.size());
        assertEquals("entry.py", userArtifacts.iterator().next().f0);
        checkAMNodeExist(streamGraph);
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new NodeOperatorMatcher(TFClusterConfig.WORKER_NODE_TYPE, 3)));
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new SourceNodeMatcher(TFClusterConfig.PS_NODE_TYPE, 2)));
    }

    @Test
    public void testInference() throws ExecutionException, InterruptedException {
        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setPsCount(2)
                        .setWorkerCount(3)
                        .setNodeEntry("entry.py", "main")
                        .build();
        final Table sourceTable = tEnv.fromDataStream(env.fromElements(1, 2, 3));
        final Schema schema =
                Schema.newBuilder()
                        .column("feature", DataTypes.INT())
                        .column("label", DataTypes.INT())
                        .build();
        final Table table = TFUtils.inference(statementSet, sourceTable, config, schema);
        statementSet.addInsert(TableDescriptor.forConnector("blackhole").build(), table);
        statementSet.execute().await();
        final StreamGraph streamGraph = (StreamGraph) executor.getPipeline();
        final Collection<Tuple2<String, DistributedCache.DistributedCacheEntry>> userArtifacts =
                streamGraph.getUserArtifacts();
        assertEquals(1, userArtifacts.size());
        assertEquals("entry.py", userArtifacts.iterator().next().f0);
        checkAMNodeExist(streamGraph);
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new NodeOperatorMatcher(TFClusterConfig.WORKER_NODE_TYPE, 3)));
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new SourceNodeMatcher(TFClusterConfig.PS_NODE_TYPE, 2)));
    }

    @Test
    public void testTensorBoard() throws ExecutionException, InterruptedException {
        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setPsCount(2)
                        .setWorkerCount(3)
                        .setNodeEntry("entry.py", "main")
                        .build();
        TFUtils.tensorBoard(statementSet, config);
        statementSet.execute().await();
        final StreamGraph streamGraph = (StreamGraph) executor.getPipeline();
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new SourceNodeMatcher(TFClusterConfig.TENSORBOARD_NODE_TYPE, 1)));
    }

    @Test
    public void testIterativeTrain() throws ExecutionException, InterruptedException {
        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setPsCount(2)
                        .setWorkerCount(3)
                        .setNodeEntry("entry.py", "main")
                        .build();
        final Table sourceTable = tEnv.fromDataStream(env.fromElements(1, 2, 3));

        TFUtils.train(statementSet, sourceTable, config, 3);
        statementSet.execute().await();

        final StreamGraph streamGraph = (StreamGraph) executor.getPipeline();
        checkAMNodeExist(streamGraph);
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new IterativeNodeOperatorMatcher(TFClusterConfig.WORKER_NODE_TYPE, 3)));
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new SourceNodeMatcher(TFClusterConfig.PS_NODE_TYPE, 2)));
    }

    private void checkAMNodeExist(StreamGraph streamGraph) {
        assertThat(streamGraph.getStreamNodes(), hasItem(new AMNodeMatcher(1)));
    }
}
