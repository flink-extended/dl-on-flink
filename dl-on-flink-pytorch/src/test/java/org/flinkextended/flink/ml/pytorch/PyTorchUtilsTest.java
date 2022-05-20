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

import org.flinkextended.flink.ml.operator.coding.RowCSVCoding;

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

/** Unit test for {@link PyTorchUtils}. */
public class PyTorchUtilsTest {

    private StreamExecutionEnvironment env;
    private StreamTableEnvironment tEnv;
    private StreamStatementSet statementSet;

    @Before
    public void setUp() throws Exception {
        this.env = StreamExecutionEnvironment.getExecutionEnvironment();
        this.tEnv = StreamTableEnvironment.create(env);
        this.statementSet = tEnv.createStatementSet();
    }

    @Test
    public void testTrainWithoutInput() throws ExecutionException, InterruptedException {
        final PyTorchClusterConfig clusterConfig =
                PyTorchClusterConfig.newBuilder()
                        .setNodeEntry(getScriptPathFromResources("all_gather.py"), "main")
                        .setWorldSize(3)
                        .build();
        PyTorchUtils.train(statementSet, clusterConfig);

        statementSet.execute().await();
    }

    @Test
    public void testTrainWithInput() throws ExecutionException, InterruptedException {
        final Table sourceTable = tEnv.fromDataStream(env.fromElements(1, 2, 3, 4, 5, 6));
        final PyTorchClusterConfig clusterConfig =
                PyTorchClusterConfig.newBuilder()
                        .setNodeEntry(getScriptPathFromResources("with_input.py"), "main")
                        .setWorldSize(3)
                        .build();
        PyTorchUtils.train(statementSet, sourceTable, clusterConfig);

        statementSet.execute().await();
    }

    @Test
    public void testIterationTrain() throws ExecutionException, InterruptedException {
        final Table sourceTable =
                tEnv.fromDataStream(env.fromElements(1, 2, 3, 4).map(i -> i).setParallelism(2));

        final PyTorchClusterConfig config =
                PyTorchClusterConfig.newBuilder()
                        .setNodeEntry(getScriptPathFromResources("with_input_iter.py"), "main")
                        .setWorldSize(2)
                        .setProperty(RowCSVCoding.ENCODE_TYPES, "INT_32")
                        .build();

        PyTorchUtils.train(statementSet, sourceTable, config, 4);
        statementSet.execute().await();
    }

    @Test
    public void testIterationTrainWithEarlyTermination()
            throws ExecutionException, InterruptedException {
        final Table sourceTable =
                tEnv.fromDataStream(env.fromElements(1, 2, 3, 4).map(i -> i).setParallelism(2));

        final PyTorchClusterConfig config =
                PyTorchClusterConfig.newBuilder()
                        .setNodeEntry(getScriptPathFromResources("with_input_iter.py"), "main")
                        .setWorldSize(2)
                        .setProperty(RowCSVCoding.ENCODE_TYPES, "INT_32")
                        .build();

        PyTorchUtils.train(statementSet, sourceTable, config, Integer.MAX_VALUE);
        statementSet.execute().await();
    }

    @Test
    public void testInference() throws ExecutionException, InterruptedException {

        final Table sourceTable = tEnv.fromDataStream(env.fromElements(1, 2, 3, 4, 5, 6));
        final PyTorchClusterConfig clusterConfig =
                PyTorchClusterConfig.newBuilder()
                        .setNodeEntry(getScriptPathFromResources("inference.py"), "main")
                        .setProperty(RowCSVCoding.DECODE_TYPES, "INT_32,INT_32")
                        .setWorldSize(3)
                        .build();
        final Schema schema =
                Schema.newBuilder()
                        .column("x", DataTypes.INT())
                        .column("y", DataTypes.INT())
                        .build();
        final Table resTable =
                PyTorchUtils.inference(statementSet, sourceTable, clusterConfig, schema);

        statementSet.addInsert(TableDescriptor.forConnector("print").build(), resTable);
        statementSet.execute().await();
    }

    private String getScriptPathFromResources(String fileName) {
        final URL resource = Thread.currentThread().getContextClassLoader().getResource(fileName);
        assertNotNull(resource);
        return resource.getPath();
    }
}
