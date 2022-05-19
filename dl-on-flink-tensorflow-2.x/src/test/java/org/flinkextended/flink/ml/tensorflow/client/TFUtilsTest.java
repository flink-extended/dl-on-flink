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

import org.flinkextended.flink.ml.operator.coding.RowCSVCoding;
import org.flinkextended.flink.ml.operator.source.DebugRowSource;
import org.flinkextended.flink.ml.operator.util.DataTypes;
import org.flinkextended.flink.ml.operator.util.TypeUtil;
import org.flinkextended.flink.ml.tensorflow.hooks.DebugHook;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.SysUtil;
import org.flinkextended.flink.ml.util.TestUtil;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableDescriptor;
import org.apache.flink.table.api.bridge.java.StreamStatementSet;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;

import org.junit.Test;

import java.net.URL;
import java.util.concurrent.ExecutionException;

import static org.junit.Assert.assertNotNull;

/** Unit test for {@link TFUtils}. */
public class TFUtilsTest {

    private static final String ckptDir =
            TestUtil.getProjectRootPath() + "/dl-on-flink-tensorflow/target/tmp/add_withtb/";

    @Test
    public void testTrainAdd() throws Exception {
        System.out.println(SysUtil._FUNC_());
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tEnv = StreamTableEnvironment.create(env);
        final StreamStatementSet statementSet = tEnv.createStatementSet();

        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setWorkerCount(2)
                        .setPsCount(1)
                        .setNodeEntry(getScriptPathFromResources("add.py"), "map_func")
                        .build();
        TFUtils.train(statementSet, config);

        statementSet.execute().await();
    }

    @Test
    public void testIterationTrain() throws ExecutionException, InterruptedException {
        System.out.println(SysUtil._FUNC_());
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tEnv = StreamTableEnvironment.create(env);
        final StreamStatementSet statementSet = tEnv.createStatementSet();

        final Table sourceTable =
                tEnv.fromDataStream(
                        env.fromElements(1, 2, 3, 4).broadcast().map(i -> i).setParallelism(2));

        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setNodeEntry(getScriptPathFromResources("print_input_iter.py"), "map_func")
                        .setWorkerCount(2)
                        .setProperty(MLConstants.ENCODING_CLASS, RowCSVCoding.class.getName())
                        .setProperty(RowCSVCoding.ENCODE_TYPES, "INT_32")
                        .build();

        TFUtils.train(statementSet, sourceTable, config, 4);
        statementSet.execute().await();
    }

    @Test
    public void testIterationTrainWithEarlyTermination()
            throws ExecutionException, InterruptedException {
        System.out.println(SysUtil._FUNC_());
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tEnv = StreamTableEnvironment.create(env);
        final StreamStatementSet statementSet = tEnv.createStatementSet();

        final Table sourceTable =
                tEnv.fromDataStream(
                        env.fromElements(1, 2, 3, 4).broadcast().map(i -> i).setParallelism(2));

        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setNodeEntry(getScriptPathFromResources("print_input_iter.py"), "map_func")
                        .setWorkerCount(2)
                        .setProperty(MLConstants.ENCODING_CLASS, RowCSVCoding.class.getName())
                        .setProperty(RowCSVCoding.ENCODE_TYPES, "INT_32")
                        .build();

        TFUtils.train(statementSet, sourceTable, config, Integer.MAX_VALUE);
        statementSet.execute().await();
    }

    @Test
    public void inferenceTable() throws Exception {
        System.out.println(SysUtil._FUNC_());
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tEnv = StreamTableEnvironment.create(env);
        final StreamStatementSet statementSet = tEnv.createStatementSet();

        StringBuilder inputSb = new StringBuilder();
        inputSb.append(DataTypes.INT_32.name()).append(",");
        inputSb.append(DataTypes.INT_64.name()).append(",");
        inputSb.append(DataTypes.FLOAT_32.name()).append(",");
        inputSb.append(DataTypes.FLOAT_64.name()).append(",");
        inputSb.append(DataTypes.STRING.name());

        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setWorkerCount(2)
                        .setPsCount(1)
                        .setNodeEntry(getScriptPathFromResources("input_output.py"), "map_func")
                        .setProperty(MLConstants.ENCODING_CLASS, RowCSVCoding.class.getName())
                        .setProperty(MLConstants.DECODING_CLASS, RowCSVCoding.class.getName())
                        .setProperty(RowCSVCoding.ENCODE_TYPES, inputSb.toString())
                        .setProperty(RowCSVCoding.DECODE_TYPES, inputSb.toString())
                        .build();

        tEnv.createTemporaryTable(
                "debug_source",
                TableDescriptor.forConnector("TableDebug")
                        .schema(TypeUtil.rowTypeInfoToSchema(DebugRowSource.typeInfo))
                        .build());

        Table input = tEnv.from("debug_source");

        final Table table =
                TFUtils.inference(
                        statementSet,
                        input,
                        config,
                        TypeUtil.rowTypeInfoToSchema(DebugRowSource.typeInfo));

        statementSet.addInsert(
                TableDescriptor.forConnector("TableDebug")
                        .schema(TypeUtil.rowTypeInfoToSchema(DebugRowSource.typeInfo))
                        .build(),
                table);

        statementSet.execute().await();
    }

    @Test
    public void testTensorBoardTable() throws Exception {
        System.out.println(SysUtil._FUNC_());
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tEnv = StreamTableEnvironment.create(env);
        final StreamStatementSet statementSet = tEnv.createStatementSet();

        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setWorkerCount(2)
                        .setPsCount(1)
                        .setNodeEntry(getScriptPathFromResources("add_withtb.py"), "map_func")
                        .setProperty(MLConstants.FLINK_HOOK_CLASSNAMES, DebugHook.class.getName())
                        .setProperty(
                                MLConstants.CHECKPOINT_DIR, ckptDir + System.currentTimeMillis())
                        .build();

        TFUtils.train(statementSet, config);
        TFUtils.tensorBoard(statementSet, config);
        statementSet.execute().await();
    }

    @Test
    public void testWorkerZeroFinish() throws Exception {
        System.out.println(SysUtil._FUNC_());
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        StreamTableEnvironment tEnv = StreamTableEnvironment.create(env);
        final StreamStatementSet statementSet = tEnv.createStatementSet();

        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setWorkerCount(3)
                        .setPsCount(2)
                        .setNodeEntry(getScriptPathFromResources("worker_0_finish.py"), "map_func")
                        .build();
        TFUtils.train(statementSet, config);
        statementSet.execute().await();
    }

    private String getScriptPathFromResources(String fileName) {
        final URL resource = Thread.currentThread().getContextClassLoader().getResource(fileName);
        assertNotNull(resource);
        return resource.getPath();
    }
}
