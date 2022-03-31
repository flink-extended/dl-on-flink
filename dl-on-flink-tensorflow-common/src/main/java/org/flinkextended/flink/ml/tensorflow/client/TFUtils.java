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

import org.flinkextended.flink.ml.operator.client.NodeUtils;
import org.flinkextended.flink.ml.tensorflow.cluster.node.runner.TensorBoardPythonRunner;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.Table;

import java.util.Map;

/** TFUtils provides methods to run training and inference Tensorflow job in Flink. */
public class TFUtils {
    /**
     * Train a Tensorflow deep learning model without input data from Flink. Users should read the
     * input data in their training script written with Tensorflow. {@link TFClusterConfig} includes
     * all the information to run the training cluster.
     *
     * <p>This method add couple operators that run nodes with different node types in the deep
     * learning cluster to the given {@link StatementSet}. Therefore, User should invoke {@link
     * StatementSet#execute()} to run the deep learning cluster at the end.
     *
     * @param statementSet The statement set to add the deep learning tables.
     * @param tfClusterConfig The configuration of the Tensorflow cluster.
     */
    public static void train(StatementSet statementSet, TFClusterConfig tfClusterConfig) {
        NodeUtils.scheduleAMNode(statementSet, tfClusterConfig);

        final Map<String, Integer> nodeTypeCntMap = tfClusterConfig.getNodeTypeCntMap();

        maybeSchedulePsNodes(nodeTypeCntMap, statementSet, tfClusterConfig);
        NodeUtils.scheduleNodes(statementSet, tfClusterConfig, TFClusterConfig.WORKER_NODE_TYPE);
    }

    /**
     * Train a Tensorflow deep learning model with the input data from Flink. Users should read the
     * input data in their training script with the FlinkStreamTFDataSet in the python library.
     * {@link TFClusterConfig} includes all the information to run the training cluster.
     *
     * <p>This method add couple operators that run nodes with different node types in the deep
     * learning cluster to the given {@link StatementSet}. Therefore, User should invoke {@link
     * StatementSet#execute()} to run the deep learning cluster at the end.
     *
     * @param statementSet The statement set to add the deep learning tables.
     * @param input The input data to the training process.
     * @param tfClusterConfig The configuration of the Tensorflow cluster.
     */
    public static void train(
            StatementSet statementSet, Table input, TFClusterConfig tfClusterConfig) {
        NodeUtils.scheduleAMNode(statementSet, tfClusterConfig);

        final Map<String, Integer> nodeTypeCntMap = tfClusterConfig.getNodeTypeCntMap();

        maybeSchedulePsNodes(nodeTypeCntMap, statementSet, tfClusterConfig);
        NodeUtils.scheduleNodes(
                statementSet, input, tfClusterConfig, TFClusterConfig.WORKER_NODE_TYPE);
    }

    /**
     * Stream inference with Tensorflow model for the input table. {@link TFClusterConfig} includes
     * all the information to run the training cluster.
     *
     * <p>This method add couple operators that run nodes with different node types in the deep
     * learning cluster to the given {@link StatementSet}. Therefore, User should invoke {@link
     * StatementSet#execute()} to run the deep learning cluster at the end.
     *
     * <p>User is responsible to insert the returned table into the {@link StatementSet} so that the
     * Tensorflow cluster runs in the same Flink job.
     *
     * @param statementSet The statement set to add the deep learning tables.
     * @param input The input data to inference.
     * @param tfClusterConfig The configuration of the Tensorflow cluster.
     * @param outputSchema The schema of the output Table.
     * @return The output Table produced by Tensorflow model inference process.
     */
    public static Table inference(
            StatementSet statementSet,
            Table input,
            TFClusterConfig tfClusterConfig,
            Schema outputSchema) {
        NodeUtils.scheduleAMNode(statementSet, tfClusterConfig);

        final Map<String, Integer> nodeTypeCntMap = tfClusterConfig.getNodeTypeCntMap();

        maybeSchedulePsNodes(nodeTypeCntMap, statementSet, tfClusterConfig);
        return NodeUtils.scheduleNodes(
                input, tfClusterConfig, outputSchema, TFClusterConfig.WORKER_NODE_TYPE);
    }

    /**
     * Start a TensorBoard service in the Tensorflow cluster. This method is commonly used with the
     * {@link TFUtils#train} methods. The started TensorBoard service will look for the model
     * checkpoint at the path specified in {@link TFClusterConfig}. User should make sure that the
     * training script write the checkpoint to the same path.
     *
     * @param statementSet The statement set to add the deep learning tables.
     * @param tfClusterConfig The configuration of the Tensorflow cluster.
     */
    public static void tensorBoard(StatementSet statementSet, TFClusterConfig tfClusterConfig) {
        final TFClusterConfig finalConfig =
                tfClusterConfig
                        .toBuilder()
                        .setProperty(
                                MLConstants.SCRIPT_RUNNER_CLASS,
                                TensorBoardPythonRunner.class.getName())
                        .addNodeType(TFClusterConfig.TENSORBOARD_NODE_TYPE, 1)
                        .build();
        NodeUtils.scheduleNodes(statementSet, finalConfig, TFClusterConfig.TENSORBOARD_NODE_TYPE);
    }

    private static void maybeSchedulePsNodes(
            Map<String, Integer> nodeTypeCntMap,
            StatementSet statementSet,
            TFClusterConfig tfClusterConfig) {
        if (nodeTypeCntMap.containsKey(TFClusterConfig.PS_NODE_TYPE)) {
            NodeUtils.scheduleNodes(statementSet, tfClusterConfig, TFClusterConfig.PS_NODE_TYPE);
        }
    }
}
