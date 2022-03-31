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

package org.flinkextended.flink.ml.operator.client;

import org.flinkextended.flink.ml.cluster.ClusterConfig;
import org.flinkextended.flink.ml.operator.coding.RowCSVCoding;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableDescriptor;
import org.apache.flink.table.api.bridge.java.StreamStatementSet;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;

import org.junit.Before;
import org.junit.Test;

import java.net.URL;
import java.util.concurrent.ExecutionException;

import static org.junit.Assert.assertNotNull;

/** Unit test for {@link NodeUtils}. */
public class NodeUtilsTest {

    private StreamTableEnvironment tEnv;
    private StreamStatementSet statementSet;
    private StreamExecutionEnvironment env;

    @Before
    public void setUp() throws Exception {
        env = StreamExecutionEnvironment.getExecutionEnvironment();
        tEnv = StreamTableEnvironment.create(env);
        statementSet = tEnv.createStatementSet();
    }

    @Test
    public void testScheduleNodeNoInputNoOutput() throws InterruptedException, ExecutionException {
        final ClusterConfig config =
                ClusterConfig.newBuilder()
                        .addNodeType("worker", 2)
                        .setNodeEntry(getScriptPathFromResources("greeter.py"), "map_func")
                        .build();

        NodeUtils.scheduleAMNode(statementSet, config);
        NodeUtils.scheduleNodes(statementSet, config, "worker");

        statementSet.execute().await();
        // Test pass if the job finished successfully.
    }

    @Test
    public void testScheduleNodeWithTwoNodeTypes() throws InterruptedException, ExecutionException {
        final ClusterConfig config =
                ClusterConfig.newBuilder()
                        .addNodeType("worker", 2)
                        .addNodeType("ps", 2)
                        .setNodeEntry(getScriptPathFromResources("greeter.py"), "map_func")
                        .build();

        NodeUtils.scheduleAMNode(statementSet, config);
        NodeUtils.scheduleNodes(statementSet, config, "worker");
        NodeUtils.scheduleNodes(statementSet, config, "ps");

        statementSet.execute().await();
        // Test pass if the job finished successfully.
    }

    @Test
    public void testScheduleNodeNoInputWithOutput()
            throws ExecutionException, InterruptedException {
        final ClusterConfig config =
                ClusterConfig.newBuilder()
                        .addNodeType("worker", 2)
                        .setNodeEntry(getScriptPathFromResources("row_output.py"), "map_func")
                        .setProperty(MLConstants.DECODING_CLASS, RowCSVCoding.class.getName())
                        .setProperty(RowCSVCoding.DECODE_TYPES, "STRING,INT_32")
                        .build();

        final Schema outSchema =
                Schema.newBuilder()
                        .column("name", DataTypes.STRING())
                        .column("value", DataTypes.INT())
                        .build();
        NodeUtils.scheduleAMNode(statementSet, config);
        final Table output = NodeUtils.scheduleNodes(tEnv, config, outSchema, "worker");
        statementSet.addInsert(TableDescriptor.forConnector("print").build(), output);
        statementSet.execute().await();
        // Test pass if the job finished successfully.
    }

    @Test
    public void testScheduleNodeWithInputNoOutput()
            throws ExecutionException, InterruptedException {
        final DataStreamSource<Tuple2<String, Integer>> dataStreamSource =
                env.fromElements(
                        new Tuple2<>("1", 1),
                        new Tuple2<>("2", 2),
                        new Tuple2<>("3", 3),
                        new Tuple2<>("4", 4));
        final Table sourceTable = tEnv.fromDataStream(dataStreamSource);

        final ClusterConfig config =
                ClusterConfig.newBuilder()
                        .addNodeType("worker", 2)
                        .setNodeEntry(getScriptPathFromResources("row_input.py"), "map_func")
                        .setProperty(MLConstants.ENCODING_CLASS, RowCSVCoding.class.getName())
                        .setProperty(RowCSVCoding.ENCODE_TYPES, "STRING,INT_32")
                        .build();

        NodeUtils.scheduleAMNode(statementSet, config);
        NodeUtils.scheduleNodes(statementSet, sourceTable, config, "worker");
        statementSet.execute().await();
        // Test pass if the job finished successfully.
    }

    @Test
    public void testScheduleNodeWithInputWithOutput()
            throws ExecutionException, InterruptedException {
        final DataStreamSource<Tuple2<String, Integer>> dataStreamSource =
                env.fromElements(
                        new Tuple2<>("1", 1),
                        new Tuple2<>("2", 2),
                        new Tuple2<>("3", 3),
                        new Tuple2<>("4", 4));
        final Table sourceTable = tEnv.fromDataStream(dataStreamSource);

        final ClusterConfig config =
                ClusterConfig.newBuilder()
                        .addNodeType("worker", 2)
                        .setNodeEntry(getScriptPathFromResources("row_input_output.py"), "map_func")
                        .setProperty(MLConstants.ENCODING_CLASS, RowCSVCoding.class.getName())
                        .setProperty(MLConstants.DECODING_CLASS, RowCSVCoding.class.getName())
                        .setProperty(RowCSVCoding.ENCODE_TYPES, "STRING,INT_32")
                        .setProperty(RowCSVCoding.DECODE_TYPES, "STRING,FLOAT_64")
                        .build();

        Schema outSchema =
                Schema.newBuilder()
                        .column("key", DataTypes.STRING())
                        .column("value", DataTypes.DOUBLE())
                        .build();

        NodeUtils.scheduleAMNode(statementSet, config);
        final Table output = NodeUtils.scheduleNodes(sourceTable, config, outSchema, "worker");
        statementSet.addInsert(TableDescriptor.forConnector("print").build(), output);
        statementSet.execute().await();
        // Test pass if the job finished successfully.
    }

    private String getScriptPathFromResources(String fileName) {
        final URL resource = Thread.currentThread().getContextClassLoader().getResource(fileName);
        assertNotNull(resource);
        return resource.getPath();
    }
}
