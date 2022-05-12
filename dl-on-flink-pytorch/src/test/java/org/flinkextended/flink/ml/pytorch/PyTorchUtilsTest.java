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

package org.flinkextended.flink.ml.pytorch;

import org.flinkextended.flink.ml.operator.coding.RowCSVCoding;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableDescriptor;
import org.apache.flink.table.api.bridge.java.StreamStatementSet;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;

import org.junit.Test;

import java.net.URL;
import java.util.concurrent.ExecutionException;

import static org.junit.Assert.assertNotNull;

/** Unit test for {@link PyTorchUtils}. */
public class PyTorchUtilsTest {
    @Test
    public void testTrainWithoutInput() throws ExecutionException, InterruptedException {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tEnv = StreamTableEnvironment.create(env);
        final StreamStatementSet statementSet = tEnv.createStatementSet();

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
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tEnv = StreamTableEnvironment.create(env);
        final StreamStatementSet statementSet = tEnv.createStatementSet();

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
    public void testInference() throws ExecutionException, InterruptedException {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tEnv = StreamTableEnvironment.create(env);
        final StreamStatementSet statementSet = tEnv.createStatementSet();

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
