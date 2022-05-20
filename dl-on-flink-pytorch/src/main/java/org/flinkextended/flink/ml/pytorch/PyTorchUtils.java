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

import org.flinkextended.flink.ml.operator.client.NodeUtils;
import org.flinkextended.flink.ml.operator.util.ReflectionUtils;

import org.apache.flink.configuration.Configuration;
import org.apache.flink.iteration.DataStreamList;
import org.apache.flink.iteration.IterationConfig;
import org.apache.flink.iteration.Iterations;
import org.apache.flink.iteration.ReplayableDataStreamList;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableDescriptor;
import org.apache.flink.table.api.bridge.java.internal.StreamTableEnvironmentImpl;
import org.apache.flink.table.api.internal.StatementSetImpl;
import org.apache.flink.types.Row;

/**
 * The {@link PyTorchUtils} class provides methods to run a distributed PyTorch cluster to do model
 * training and inference.
 */
public class PyTorchUtils {
    /**
     * Train a PyTorch deep learning model without input data from Flink. Users should read the
     * input data in their training script written with PyTorch. {@link PyTorchClusterConfig}
     * includes all the information to run the training cluster.
     *
     * <p>This method adds a number of nodes with different node types in the deep learning cluster
     * to the given {@link StatementSet}. Therefore, User should invoke {@link
     * StatementSet#execute()} to run the deep learning cluster at the end.
     *
     * @param statementSet The statement set to add the deep learning tables.
     * @param pyTorchClusterConfig The configuration of the PyTorch cluster.
     */
    public static void train(StatementSet statementSet, PyTorchClusterConfig pyTorchClusterConfig) {
        NodeUtils.scheduleAMNode(statementSet, pyTorchClusterConfig);

        NodeUtils.scheduleNodes(
                statementSet, pyTorchClusterConfig, PyTorchClusterConfig.WORKER_NODE_TYPE);
    }

    /**
     * Train a PyTorch deep learning model with the input data from Flink. {@link
     * PyTorchClusterConfig} includes all the information to run the training cluster.
     *
     * <p>This method adds a number of nodes with different node types in the deep learning cluster
     * to the given {@link StatementSet}. Therefore, User should invoke {@link
     * StatementSet#execute()} to run the deep learning cluster at the end.
     *
     * @param statementSet The statement set to add the deep learning tables.
     * @param input The input data to the training process.
     * @param pyTorchClusterConfig The configuration of the PyTorch cluster.
     */
    public static void train(
            StatementSet statementSet, Table input, PyTorchClusterConfig pyTorchClusterConfig) {
        NodeUtils.scheduleAMNode(statementSet, pyTorchClusterConfig);

        NodeUtils.scheduleNodes(
                statementSet, input, pyTorchClusterConfig, PyTorchClusterConfig.WORKER_NODE_TYPE);
    }

    /**
     * Iteratively train a PyTorch deep learning model with the input data from Flink for the given
     * number of epoch. User can terminate the training earlier by exiting the training node.
     *
     * <p>The provided input should be bounded for iterative training. Otherwise, the model is
     * trained indefinitely with the unbounded data at the first epoch. {@link PyTorchClusterConfig}
     * includes all the information to run the training cluster.
     *
     * <p>This method adds a number of nodes with different node types in the deep learning cluster
     * to the given {@link StatementSet}. Therefore, User should invoke {@link
     * StatementSet#execute()} to run the deep learning cluster at the end.
     *
     * @param statementSet The statement set to add the deep learning tables.
     * @param input input The bounded input data to the training process.
     * @param pyTorchClusterConfig The configuration of the PyTorch cluster.
     * @param epoch Number of epoch to train the model.
     */
    public static void train(
            StatementSet statementSet,
            Table input,
            PyTorchClusterConfig pyTorchClusterConfig,
            Integer epoch) {
        final StreamTableEnvironmentImpl tEnv =
                ReflectionUtils.getFieldValue(
                        statementSet, StatementSetImpl.class, "tableEnvironment");
        final StreamExecutionEnvironment env = tEnv.execEnv();
        final DataStream<Row> inputDataStream = tEnv.toDataStream(input);
        final Configuration flinkConfig = NodeUtils.mergeConfiguration(env, tEnv.getConfig());

        NodeUtils.scheduleAMNode(statementSet, pyTorchClusterConfig);

        final IterationConfig iterationConfig = IterationConfig.newBuilder().build();
        final DataStreamSource<Integer> dummyInitVariable = env.fromElements(0);
        final DataStreamList dataStreamList =
                Iterations.iterateBoundedStreamsUntilTermination(
                        DataStreamList.of(dummyInitVariable),
                        ReplayableDataStreamList.replay(inputDataStream),
                        iterationConfig,
                        new PyTorchNodeIterationBody(
                                env, pyTorchClusterConfig, epoch, flinkConfig));

        final DataStream<Integer> trainResDataStream = dataStreamList.get(0);
        statementSet.addInsert(
                TableDescriptor.forConnector("blackhole").build(),
                tEnv.fromDataStream(trainResDataStream));
    }

    /**
     * Stream inference with PyTorch model for the input table. {@link PyTorchClusterConfig}
     * includes all the information to run the training cluster.
     *
     * <p>This method adds a number of nodes with different node types in the deep learning cluster
     * to the given {@link StatementSet}. Therefore, User should invoke {@link
     * StatementSet#execute()} to run the deep learning cluster at the end.
     *
     * <p>User is responsible to insert the returned table into the {@link StatementSet} so that the
     * PyTorch cluster runs in the same Flink job.
     *
     * @param statementSet The statement set to add the deep learning tables.
     * @param input The input data to inference.
     * @param pyTorchClusterConfig The configuration of the PyTorch cluster.
     * @param outputSchema The schema of the output Table.
     * @return The output Table produced by PyTorch model inference process.
     */
    public static Table inference(
            StatementSet statementSet,
            Table input,
            PyTorchClusterConfig pyTorchClusterConfig,
            Schema outputSchema) {
        NodeUtils.scheduleAMNode(statementSet, pyTorchClusterConfig);

        return NodeUtils.scheduleNodes(
                input, pyTorchClusterConfig, outputSchema, PyTorchClusterConfig.WORKER_NODE_TYPE);
    }
}
