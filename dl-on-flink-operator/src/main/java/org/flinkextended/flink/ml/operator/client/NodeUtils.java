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
import org.flinkextended.flink.ml.cluster.ClusterConfig.Builder;
import org.flinkextended.flink.ml.operator.ops.NodeOperator;
import org.flinkextended.flink.ml.operator.ops.source.NodeSource;
import org.flinkextended.flink.ml.operator.util.PythonFileUtil;
import org.flinkextended.flink.ml.operator.util.ReflectionUtils;
import org.flinkextended.flink.ml.operator.util.TypeUtil;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableDescriptor;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.api.bridge.java.internal.StreamTableEnvironmentImpl;
import org.apache.flink.table.api.internal.StatementSetImpl;
import org.apache.flink.table.api.internal.TableImpl;
import org.apache.flink.table.catalog.SchemaResolver;
import org.apache.flink.types.Row;

import com.google.common.base.Joiner;

import java.io.IOException;
import java.util.List;
import java.util.Set;

/**
 * NodeUtils provides methods to schedule node with various node type (e.g., worker, ps, chief) of a
 * deep learning cluster to a Flink job. The deep learning cluster is spawned when the Flink job
 * runs.
 */
public class NodeUtils {
    private static final TypeInformation<Void> DUMMY_TI = TypeInformation.of(Void.class);

    /**
     * Schedule the node of the given node type to the deep learning cluster. This will add a table
     * that runs the node to the given statement set. User should invoke {@link
     * StatementSet#execute()} to run the deep learning cluster at the end.
     *
     * @param statementSet The statement set to add the deep learning node.
     * @param clusterConfig The ClusterConfig of the added node.
     * @param nodeType The type of the node to be added to the cluster.
     */
    public static void scheduleNodes(
            StatementSet statementSet, ClusterConfig clusterConfig, String nodeType) {
        final StreamTableEnvironmentImpl tEnv =
                ReflectionUtils.getFieldValue(
                        statementSet, StatementSetImpl.class, "tableEnvironment");
        final StreamExecutionEnvironment env = tEnv.execEnv();

        final Builder<?> builder = clusterConfig.toBuilder();
        registerFileToFlinkCache(env, clusterConfig.getPythonFilePaths(), builder);
        ClusterConfig finalClusterConfig = builder.build();

        final SingleOutputStreamOperator<Void> nodeStream =
                env.addSource(NodeSource.createNodeSource(nodeType, finalClusterConfig, DUMMY_TI))
                        .setParallelism(finalClusterConfig.getNodeCount(nodeType))
                        .name(nodeType);
        final Table nodeTable = tEnv.fromDataStream(nodeStream);
        statementSet.addInsert(TableDescriptor.forConnector("blackhole").build(), nodeTable);
    }

    /**
     * Schedule the node with the given node type to the deep learning cluster. The deep learning
     * node produces Table with the given {@link Schema}. If user has added other nodes to a {@link
     * StatementSet}, the return Table should insert into the same {@link StatementSet} so that all
     * the nodes in the cluster can run in the same Flink job.
     *
     * @param tEnv The stream table environment.
     * @param clusterConfig The ClusterConfig of the added node.
     * @param outSchema The schema of the output Table.
     * @param nodeType The type of the node to be added to the cluster.
     * @return The output Table produced by the deep learning node.
     */
    public static Table scheduleNodes(
            StreamTableEnvironment tEnv,
            ClusterConfig clusterConfig,
            Schema outSchema,
            String nodeType) {

        final StreamExecutionEnvironment env = ((StreamTableEnvironmentImpl) tEnv).execEnv();

        final Builder<?> builder = clusterConfig.toBuilder();
        registerFileToFlinkCache(env, clusterConfig.getPythonFilePaths(), builder);
        ClusterConfig finalClusterConfig = builder.build();

        final SchemaResolver schemaResolver =
                ((StreamTableEnvironmentImpl) tEnv).getCatalogManager().getSchemaResolver();
        final SingleOutputStreamOperator<Row> nodeStream =
                env.addSource(
                                NodeSource.createNodeSource(
                                        nodeType,
                                        finalClusterConfig,
                                        TypeUtil.schemaToRowTypeInfo(
                                                outSchema.resolve(schemaResolver))))
                        .setParallelism(finalClusterConfig.getNodeCount(nodeType))
                        .name(nodeType);
        return tEnv.fromDataStream(nodeStream);
    }

    /**
     * Schedule the node with the given node type to the deep learning cluster. The deep learning
     * node consumes the input Table. This will add a table that runs the deep learning node to the
     * given statement set. User should invoke {@link StatementSet#execute()} to run the deep
     * learning cluster at the end.
     *
     * @param statementSet The statement set to add the deep learning node.
     * @param input The input Table for the deep learning node.
     * @param clusterConfig The ClusterConfig of the added node.
     * @param nodeType The type of the node to be added to the cluster.
     */
    public static void scheduleNodes(
            StatementSet statementSet, Table input, ClusterConfig clusterConfig, String nodeType) {
        final StreamTableEnvironmentImpl tEnv =
                ReflectionUtils.getFieldValue(
                        statementSet, StatementSetImpl.class, "tableEnvironment");
        final StreamExecutionEnvironment env = tEnv.execEnv();

        final Builder<?> builder = clusterConfig.toBuilder();
        registerFileToFlinkCache(env, clusterConfig.getPythonFilePaths(), builder);
        ClusterConfig finalClusterConfig = builder.build();

        final SingleOutputStreamOperator<Void> nodeStream =
                tEnv.toDataStream(input)
                        .transform(
                                nodeType,
                                DUMMY_TI,
                                new NodeOperator<>(nodeType, finalClusterConfig))
                        .setParallelism(finalClusterConfig.getNodeCount(nodeType));

        statementSet.addInsert(
                TableDescriptor.forConnector("blackhole").build(), tEnv.fromDataStream(nodeStream));
    }

    /**
     * Schedule the node with the given node type to the deep learning cluster. The deep learning
     * node consumes the input Table and produces Table with the given {@link Schema}. If user has
     * added other nodes to a {@link StatementSet}, the return Table should insert into the same
     * {@link StatementSet} so that all the nodes can be run in the same Flink job.
     *
     * @param input The input Table for the deep learning node.
     * @param clusterConfig The ClusterConfig of the added node.
     * @param outSchema The schema of the output Table.
     * @param nodeType The type of node to be added to the cluster.
     */
    public static Table scheduleNodes(
            Table input, ClusterConfig clusterConfig, Schema outSchema, String nodeType) {
        final StreamTableEnvironmentImpl tEnv =
                (StreamTableEnvironmentImpl) ((TableImpl) input).getTableEnvironment();
        final StreamExecutionEnvironment env = tEnv.execEnv();

        final Builder<?> builder = clusterConfig.toBuilder();
        registerFileToFlinkCache(env, clusterConfig.getPythonFilePaths(), builder);
        ClusterConfig finalClusterConfig = builder.build();

        final SchemaResolver schemaResolver = tEnv.getCatalogManager().getSchemaResolver();
        final DataStream<Row> outputDataStream =
                tEnv.toDataStream(input)
                        .transform(
                                nodeType,
                                TypeUtil.schemaToRowTypeInfo(outSchema.resolve(schemaResolver)),
                                new NodeOperator<>(nodeType, finalClusterConfig))
                        .setParallelism(finalClusterConfig.getNodeCount(nodeType));

        return tEnv.fromDataStream(outputDataStream);
    }

    /**
     * Schedule an application master node to machine learning cluster. The application master
     * manage the life cycle of other nodes in the cluster.
     *
     * @param statementSet The statement set to add the deep learning node.
     * @param clusterConfig The ClusterConfig of the added AM node.
     */
    public static void scheduleAMNode(StatementSet statementSet, ClusterConfig clusterConfig) {
        final StreamTableEnvironmentImpl tEnv =
                ReflectionUtils.getFieldValue(
                        statementSet, StatementSetImpl.class, "tableEnvironment");
        final StreamExecutionEnvironment env = tEnv.execEnv();
        final SingleOutputStreamOperator<Void> nodeStream =
                env.addSource(NodeSource.createAMNodeSource(clusterConfig))
                        .setParallelism(1)
                        .name(ClusterConfig.AM_NODE_TYPE);
        final Table nodeTable = tEnv.fromDataStream(nodeStream);
        statementSet.addInsert(TableDescriptor.forConnector("blackhole").build(), nodeTable);
    }

    /**
     * Register the file to Flink cache and set the properties to the given cluster config builder.
     */
    private static void registerFileToFlinkCache(
            StreamExecutionEnvironment env, Set<String> filePaths, Builder<?> configBuilder) {
        try {
            final List<String> pythonFiles =
                    PythonFileUtil.registerPythonLibFilesIfNotExist(
                            env, filePaths.toArray(new String[0]));
            configBuilder.setProperty(MLConstants.PYTHON_FILES, Joiner.on(",").join(pythonFiles));
            configBuilder.setProperty(MLConstants.USE_DISTRIBUTE_CACHE, "true");
        } catch (IOException e) {
            throw new RuntimeException("Fail to register python files to Flink job", e);
        }
    }
}
