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

import org.flinkextended.flink.ml.cluster.role.AMRole;
import org.flinkextended.flink.ml.cluster.role.PsRole;
import org.flinkextended.flink.ml.cluster.role.WorkerRole;
import org.flinkextended.flink.ml.operator.ops.inputformat.MLInputFormat;
import org.flinkextended.flink.ml.tensorflow.client.StreamNodeMatchers.StreamNodeMatcher;
import org.flinkextended.flink.ml.tensorflow.cluster.ChiefRole;
import org.flinkextended.flink.ml.tensorflow.cluster.TensorBoardRole;
import org.flinkextended.flink.ml.tensorflow.cluster.node.runner.TensorBoardPythonRunner;
import org.flinkextended.flink.ml.tensorflow.util.TFConstants;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.api.common.io.InputFormat;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.sink.PrintSinkFunction;
import org.apache.flink.streaming.api.graph.StreamGraph;
import org.apache.flink.streaming.api.graph.StreamNode;
import org.apache.flink.streaming.api.operators.SimpleInputFormatOperatorFactory;
import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.delegation.Executor;

import org.junit.Before;
import org.junit.Test;
import org.mockito.internal.util.reflection.Whitebox;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.hamcrest.CoreMatchers.hasItem;
import static org.hamcrest.CoreMatchers.instanceOf;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertThat;

/** Unit test for {@link TFUtilsLegacy}. */
public class TFUtilsLegacyTest {

    private static final Logger LOG = LoggerFactory.getLogger(TFUtilsLegacyTest.class);

    private StreamExecutionEnvironment env;
    private TestTFConfig tfConfig;
    private StreamTableEnvironment tEnv;
    private TestExecutor executor;

    @Before
    public void setUp() throws Exception {
        env = StreamExecutionEnvironment.getExecutionEnvironment();
        tEnv = StreamTableEnvironment.create(env);
        final Executor execEnv = (Executor) Whitebox.getInternalState(tEnv, "execEnv");
        executor = new TestExecutor(execEnv);
        Whitebox.setInternalState(tEnv, "execEnv", executor);
        Map<String, String> properties = new HashMap<>();
        tfConfig = new TestTFConfig(2, 1, properties, "/tmp/test.py", "func", "/tmp/env");
    }

    // test for data stream api

    @Test
    public void testDataStreamTrainNoInputNoOutput() throws IOException {
        TFUtilsLegacy.train(env, tfConfig);
        assertNull(tfConfig.getProperty(MLConstants.CONFIG_JOB_HAS_INPUT));
        assertEquals(1, env.getCachedFiles().size());
        assertEquals("test.py", tfConfig.getProperty(MLConstants.PYTHON_FILES));
        final Map<String, Integer> roleMap = tfConfig.getMlConfig().getRoleParallelismMap();
        assertEquals(Integer.valueOf(1), roleMap.get(new PsRole().name()));
        assertEquals(Integer.valueOf(2), roleMap.get(new WorkerRole().name()));
        final StreamGraph streamGraph = env.getStreamGraph();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkAMNodeExist(streamGraph);
        checkPSRole(streamGraph, 1);
        checkWorkerRole(streamGraph, 2);
    }

    @Test
    public void testDataStreamTrainNoInputNoOutputWithChief() throws IOException {
        tfConfig.getProperties().put(TFConstants.TF_IS_CHIEF_ALONE, "true");
        TFUtilsLegacy.train(env, tfConfig);
        assertNull(tfConfig.getProperty(MLConstants.CONFIG_JOB_HAS_INPUT));
        assertEquals(1, env.getCachedFiles().size());
        assertEquals("test.py", tfConfig.getProperty(MLConstants.PYTHON_FILES));
        final Map<String, Integer> roleMap = tfConfig.getMlConfig().getRoleParallelismMap();
        assertEquals(Integer.valueOf(1), roleMap.get(new PsRole().name()));
        assertEquals(Integer.valueOf(2), roleMap.get(new WorkerRole().name()));
        final StreamGraph streamGraph = env.getStreamGraph();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkAMNodeExist(streamGraph);
        checkPSRole(streamGraph, 1);
        checkWorkerRole(streamGraph, 1);
        checkChiefRole(streamGraph, 1);
    }

    @Test
    public void testDataStreamTrainNoInputWithOutput() throws IOException {
        final DataStream<Integer> workerOutput = TFUtilsLegacy.train(env, tfConfig, Integer.class);
        workerOutput.addSink(new PrintSinkFunction<>());
        assertNull(tfConfig.getProperty(MLConstants.CONFIG_JOB_HAS_INPUT));
        assertEquals(1, env.getCachedFiles().size());
        assertEquals("test.py", tfConfig.getProperty(MLConstants.PYTHON_FILES));
        final Map<String, Integer> roleMap = tfConfig.getMlConfig().getRoleParallelismMap();
        assertEquals(Integer.valueOf(1), roleMap.get(new PsRole().name()));
        assertEquals(Integer.valueOf(2), roleMap.get(new WorkerRole().name()));
        final StreamGraph streamGraph = env.getStreamGraph();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkAMNodeExist(streamGraph);
        checkPSRole(streamGraph, 1);
        checkWorkerRole(streamGraph, 2);
    }

    @Test
    public void testDataStreamTrainWithInputNoOutput() throws IOException {
        final DataStreamSource<Integer> source = env.fromElements(1, 2, 3);
        TFUtilsLegacy.train(env, source, tfConfig);
        assertEquals("true", tfConfig.getProperty(MLConstants.CONFIG_JOB_HAS_INPUT));
        assertEquals(1, env.getCachedFiles().size());
        assertEquals("test.py", tfConfig.getProperty(MLConstants.PYTHON_FILES));
        final Map<String, Integer> roleMap = tfConfig.getMlConfig().getRoleParallelismMap();
        assertEquals(Integer.valueOf(1), roleMap.get(new PsRole().name()));
        assertEquals(Integer.valueOf(2), roleMap.get(new WorkerRole().name()));
        final StreamGraph streamGraph = env.getStreamGraph();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkAMNodeExist(streamGraph);
        checkPSRole(streamGraph, 1);
        checkWorkerRole(streamGraph, 2);
    }

    @Test
    public void testDataStreamTrainWithInputAndOutput() throws IOException {
        final DataStreamSource<Integer> source = env.fromElements(1, 2, 3);
        final DataStream<Integer> workerOutput =
                TFUtilsLegacy.train(env, source, tfConfig, Integer.class);
        workerOutput.addSink(new PrintSinkFunction<>());
        assertEquals("true", tfConfig.getProperty(MLConstants.CONFIG_JOB_HAS_INPUT));
        assertEquals(1, env.getCachedFiles().size());
        assertEquals("test.py", tfConfig.getProperty(MLConstants.PYTHON_FILES));
        final Map<String, Integer> roleMap = tfConfig.getMlConfig().getRoleParallelismMap();
        assertEquals(Integer.valueOf(1), roleMap.get(new PsRole().name()));
        assertEquals(Integer.valueOf(2), roleMap.get(new WorkerRole().name()));
        final StreamGraph streamGraph = env.getStreamGraph();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkAMNodeExist(streamGraph);
        checkPSRole(streamGraph, 1);
        checkWorkerRole(streamGraph, 2);
    }

    @Test
    public void testDataStreamInference() throws IOException {
        final DataStreamSource<Integer> source = env.fromElements(1, 2, 3);
        final DataStream<Integer> workerOutput =
                TFUtilsLegacy.inference(env, source, tfConfig, Integer.class);
        workerOutput.addSink(new PrintSinkFunction<>());
        assertEquals("true", tfConfig.getProperty(MLConstants.CONFIG_JOB_HAS_INPUT));
        assertEquals(1, env.getCachedFiles().size());
        assertEquals("test.py", tfConfig.getProperty(MLConstants.PYTHON_FILES));
        final Map<String, Integer> roleMap = tfConfig.getMlConfig().getRoleParallelismMap();
        assertEquals(Integer.valueOf(1), roleMap.get(new PsRole().name()));
        assertEquals(Integer.valueOf(2), roleMap.get(new WorkerRole().name()));
        final StreamGraph streamGraph = env.getStreamGraph();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkAMNodeExist(streamGraph);
        checkPSRole(streamGraph, 1);
        checkWorkerRole(streamGraph, 2);
    }

    @Test
    public void testStartTensorboard() throws IOException {
        TFUtilsLegacy.startTensorBoard(env, tfConfig);
        final StreamGraph streamGraph = env.getStreamGraph();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkTensorboardRole(streamGraph, 1);
        final List<StreamNode> streamNodes =
                getStreamNodesByName(streamGraph, new TensorBoardRole().name());
        assertEquals(1, streamNodes.size());
        final StreamNode streamNode = streamNodes.get(0);
        final MLInputFormat<?> inputFormat = getMLInputFormatFromStreamNode(streamNode);
        assertEquals(
                TensorBoardPythonRunner.class.getCanonicalName(),
                inputFormat.getMlConfig().getProperty(MLConstants.SCRIPT_RUNNER_CLASS));
        assertEquals(new TensorBoardRole().name(), inputFormat.getRole().name());
    }

    // test for table api

    @Test
    public void testTableTrainNoInputNoOutput() throws IOException {
        final StatementSet statementSet = tEnv.createStatementSet();
        TFUtilsLegacy.train(env, tEnv, statementSet, null, tfConfig, null);
        assertNull(tfConfig.getProperty(MLConstants.CONFIG_JOB_HAS_INPUT));
        assertEquals(1, env.getCachedFiles().size());
        assertEquals("test.py", tfConfig.getProperty(MLConstants.PYTHON_FILES));
        final Map<String, Integer> roleMap = tfConfig.getMlConfig().getRoleParallelismMap();
        assertEquals(Integer.valueOf(1), roleMap.get(new PsRole().name()));
        assertEquals(Integer.valueOf(2), roleMap.get(new WorkerRole().name()));

        statementSet.execute();
        assertThat(executor.getPipeline(), instanceOf(StreamGraph.class));
        final StreamGraph streamGraph = (StreamGraph) executor.getPipeline();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkAMNodeExist(streamGraph);
        checkPSRole(streamGraph, 1);
        checkWorkerRole(streamGraph, 2);
    }

    @Test
    public void testTableTrainNoInputNoOutputWithChief() throws IOException {
        tfConfig.getProperties().put(TFConstants.TF_IS_CHIEF_ALONE, "true");
        final StatementSet statementSet = tEnv.createStatementSet();
        TFUtilsLegacy.train(env, tEnv, statementSet, null, tfConfig, null);
        assertNull(tfConfig.getProperty(MLConstants.CONFIG_JOB_HAS_INPUT));
        assertEquals(1, env.getCachedFiles().size());
        final Map<String, Integer> roleMap = tfConfig.getMlConfig().getRoleParallelismMap();
        assertEquals(Integer.valueOf(1), roleMap.get(new PsRole().name()));
        assertEquals(Integer.valueOf(2), roleMap.get(new WorkerRole().name()));

        statementSet.execute();
        assertThat(executor.getPipeline(), instanceOf(StreamGraph.class));
        final StreamGraph streamGraph = (StreamGraph) executor.getPipeline();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkAMNodeExist(streamGraph);
        checkPSRole(streamGraph, 1);
        checkWorkerRole(streamGraph, 1);
        checkChiefRole(streamGraph, 1);
    }

    @Test
    public void testTableTrainNoInputWithOutput() throws IOException {
        final StatementSet statementSet = tEnv.createStatementSet();
        final Schema outSchema = Schema.newBuilder().column("field", DataTypes.INT()).build();
        final Table outTable =
                TFUtilsLegacy.train(env, tEnv, statementSet, null, tfConfig, outSchema);

        tEnv.executeSql("CREATE TABLE table_sink(field INTEGER) WITH ('connector'='print')");
        statementSet.addInsert("table_sink", outTable);

        assertNull(tfConfig.getProperty(MLConstants.CONFIG_JOB_HAS_INPUT));
        assertEquals(1, env.getCachedFiles().size());
        assertEquals("test.py", tfConfig.getProperty(MLConstants.PYTHON_FILES));
        final Map<String, Integer> roleMap = tfConfig.getMlConfig().getRoleParallelismMap();
        assertEquals(Integer.valueOf(1), roleMap.get(new PsRole().name()));
        assertEquals(Integer.valueOf(2), roleMap.get(new WorkerRole().name()));

        statementSet.execute();
        assertThat(executor.getPipeline(), instanceOf(StreamGraph.class));
        final StreamGraph streamGraph = (StreamGraph) executor.getPipeline();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkAMNodeExist(streamGraph);
        checkPSRole(streamGraph, 1);
        checkWorkerRole(streamGraph, 2);
    }

    @Test
    public void testTableTrainWithInputNoOutput() throws IOException {
        tEnv.executeSql("CREATE TABLE table_source(field INTEGER) WITH ('connector'='datagen')");
        final Table source = tEnv.from("table_source");

        final StatementSet statementSet = tEnv.createStatementSet();
        TFUtilsLegacy.train(env, tEnv, statementSet, source, tfConfig, null);

        assertEquals("true", tfConfig.getProperty(MLConstants.CONFIG_JOB_HAS_INPUT));
        assertEquals(1, env.getCachedFiles().size());
        assertEquals("test.py", tfConfig.getProperty(MLConstants.PYTHON_FILES));
        final Map<String, Integer> roleMap = tfConfig.getMlConfig().getRoleParallelismMap();
        assertEquals(Integer.valueOf(1), roleMap.get(new PsRole().name()));
        assertEquals(Integer.valueOf(2), roleMap.get(new WorkerRole().name()));

        statementSet.execute();
        assertThat(executor.getPipeline(), instanceOf(StreamGraph.class));
        final StreamGraph streamGraph = (StreamGraph) executor.getPipeline();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkAMNodeExist(streamGraph);
        checkPSRole(streamGraph, 1);
        checkWorkerRole(streamGraph, 2);
    }

    @Test
    public void testTableTrainWithInputAndOutput() throws IOException {
        tEnv.executeSql("CREATE TABLE table_source(field INTEGER) WITH ('connector'='datagen')");
        final Table source = tEnv.from("table_source");

        final StatementSet statementSet = tEnv.createStatementSet();

        final Schema outSchema = Schema.newBuilder().column("field", DataTypes.INT()).build();
        final Table outTable =
                TFUtilsLegacy.train(env, tEnv, statementSet, source, tfConfig, outSchema);

        tEnv.executeSql("CREATE TABLE table_sink(field INTEGER) WITH ('connector'='print')");
        statementSet.addInsert("table_sink", outTable);

        assertEquals("true", tfConfig.getProperty(MLConstants.CONFIG_JOB_HAS_INPUT));
        assertEquals(1, env.getCachedFiles().size());
        assertEquals("test.py", tfConfig.getProperty(MLConstants.PYTHON_FILES));
        final Map<String, Integer> roleMap = tfConfig.getMlConfig().getRoleParallelismMap();
        assertEquals(Integer.valueOf(1), roleMap.get(new PsRole().name()));
        assertEquals(Integer.valueOf(2), roleMap.get(new WorkerRole().name()));

        statementSet.execute();
        assertThat(executor.getPipeline(), instanceOf(StreamGraph.class));
        final StreamGraph streamGraph = (StreamGraph) executor.getPipeline();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkAMNodeExist(streamGraph);
        checkPSRole(streamGraph, 1);
        checkWorkerRole(streamGraph, 2);
    }

    @Test
    public void testTableInference() throws IOException {
        tEnv.executeSql("CREATE TABLE table_source(field INTEGER) WITH ('connector'='datagen')");
        final Table source = tEnv.from("table_source");

        final StatementSet statementSet = tEnv.createStatementSet();

        final Schema outSchema = Schema.newBuilder().column("field", DataTypes.INT()).build();
        final Table outTable =
                TFUtilsLegacy.inference(env, tEnv, statementSet, source, tfConfig, outSchema);

        tEnv.executeSql("CREATE TABLE table_sink(field INTEGER) WITH ('connector'='print')");
        statementSet.addInsert("table_sink", outTable);

        assertEquals("true", tfConfig.getProperty(MLConstants.CONFIG_JOB_HAS_INPUT));
        assertEquals(1, env.getCachedFiles().size());
        assertEquals("test.py", tfConfig.getProperty(MLConstants.PYTHON_FILES));
        final Map<String, Integer> roleMap = tfConfig.getMlConfig().getRoleParallelismMap();
        assertEquals(Integer.valueOf(1), roleMap.get(new PsRole().name()));
        assertEquals(Integer.valueOf(2), roleMap.get(new WorkerRole().name()));

        statementSet.execute();
        assertThat(executor.getPipeline(), instanceOf(StreamGraph.class));
        final StreamGraph streamGraph = (StreamGraph) executor.getPipeline();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkAMNodeExist(streamGraph);
        checkPSRole(streamGraph, 1);
        checkWorkerRole(streamGraph, 2);
    }

    @Test
    public void testTableStartTensorboard() throws IOException {
        final StatementSet statementSet = tEnv.createStatementSet();
        TFUtilsLegacy.startTensorBoard(env, tEnv, statementSet, tfConfig);

        statementSet.execute();
        assertThat(executor.getPipeline(), instanceOf(StreamGraph.class));
        final StreamGraph streamGraph = (StreamGraph) executor.getPipeline();
        LOG.info(streamGraph.getStreamingPlanAsJSON());
        checkTensorboardRole(streamGraph, 1);
        final List<StreamNode> streamNodes =
                getStreamNodesByName(streamGraph, "Source: " + new TensorBoardRole().name());
        assertEquals(1, streamNodes.size());
        final StreamNode streamNode = streamNodes.get(0);
        final MLInputFormat<?> inputFormat = getMLInputFormatFromStreamNode(streamNode);
        assertEquals(
                TensorBoardPythonRunner.class.getCanonicalName(),
                inputFormat.getMlConfig().getProperty(MLConstants.SCRIPT_RUNNER_CLASS));
        assertEquals(new TensorBoardRole().name(), inputFormat.getRole().name());
    }

    private MLInputFormat<?> getMLInputFormatFromStreamNode(StreamNode streamNode) {
        final InputFormat<?, ?> inputFormat =
                ((SimpleInputFormatOperatorFactory<?>) streamNode.getOperatorFactory())
                        .getInputFormat();
        return (MLInputFormat<?>) inputFormat;
    }

    private List<StreamNode> getStreamNodesByName(StreamGraph streamGraph, String name) {
        List<StreamNode> res = new ArrayList<>();
        for (StreamNode streamNode : streamGraph.getStreamNodes()) {
            if (streamNode.getOperatorName().contains(name)) {
                res.add(streamNode);
            }
        }
        return res;
    }

    private void checkChiefRole(StreamGraph streamGraph, int parallelism) {
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new StreamNodeMatcher(new ChiefRole().name(), parallelism)));
    }

    private void checkTensorboardRole(StreamGraph streamGraph, int parallelism) {
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new StreamNodeMatcher(new TensorBoardRole().name(), parallelism)));
    }

    private void checkWorkerRole(StreamGraph streamGraph, int parallelism) {
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new StreamNodeMatcher(new WorkerRole().name(), parallelism)));
    }

    private void checkAMNodeExist(StreamGraph streamGraph) {
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new StreamNodeMatcher(new AMRole().name(), 1)));
    }

    private void checkPSRole(StreamGraph streamGraph, int parallelism) {
        assertThat(
                streamGraph.getStreamNodes(),
                hasItem(new StreamNodeMatcher(new PsRole().name(), parallelism)));
    }
}
