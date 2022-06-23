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

package org.flinkextended.examples.pytorch.linear;

import org.flinkextended.flink.ml.pytorch.PyTorchClusterConfig;
import org.flinkextended.flink.ml.pytorch.PyTorchUtils;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.api.java.utils.MultipleParameterTool;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableDescriptor;
import org.apache.flink.table.api.bridge.java.StreamStatementSet;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;

import java.net.URL;
import java.util.concurrent.ExecutionException;

import static org.apache.flink.table.api.Expressions.$;

/** Example to train a model with Tensorflow. */
public class Linear {
    private static final String MODEL_PATH = "model-path";
    private static final String EPOCH = "epoch";
    private static final String SAMPLE_COUNT = "sample-count";
    private static final String MODE = "mode";
    private static final String INFERENCE_OUTPUT_PATH = "inference-output-path";

    public static void main(String[] args) throws ExecutionException, InterruptedException {

        final MultipleParameterTool params = MultipleParameterTool.fromArgs(args);
        final String mode = params.get(MODE, "train");
        final String inferenceOutputPath =
                params.get(INFERENCE_OUTPUT_PATH, "/tmp/linear/output.csv");
        final String modelPath =
                params.get(MODEL_PATH, String.format("/tmp/linear/%s", System.currentTimeMillis()));
        final Integer epoch = Integer.valueOf(params.get(EPOCH, "1"));
        final Integer sampleCount = Integer.valueOf(params.get(SAMPLE_COUNT, "256000"));

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(2);
        StreamTableEnvironment tEnv = StreamTableEnvironment.create(env);
        final StreamStatementSet statementSet = tEnv.createStatementSet();

        // Generate input sample
        final Table sample =
                tEnv.from(
                        TableDescriptor.forConnector("datagen")
                                .schema(
                                        Schema.newBuilder()
                                                .column("x", DataTypes.DOUBLE())
                                                .columnByExpression("y", "2 * x + 1")
                                                .build())
                                .option("fields.x.min", "0")
                                .option("fields.x.max", "1")
                                .option("number-of-rows", String.valueOf(sampleCount))
                                .build());
        if ("train".equals(mode)) {
            System.out.printf(
                    "Model will be trained with %d samples for %d epochs and saved at: %s%n",
                    sampleCount, epoch, modelPath);
            train(modelPath, epoch, statementSet, sample);
        } else if ("inference".equals(mode)) {
            System.out.printf(
                    "Inference with model at %s, output will be at %s%n",
                    modelPath, inferenceOutputPath);
            inference(modelPath, statementSet, sample, inferenceOutputPath);
        } else {
            throw new RuntimeException(String.format("Unknown mode %s", mode));
        }
    }

    private static void inference(
            String modelPath,
            StreamStatementSet statementSet,
            Table sample,
            String inferenceOutputPath)
            throws ExecutionException, InterruptedException {
        Table table = sample.dropColumns($("y"));
        final PyTorchClusterConfig config =
                PyTorchClusterConfig.newBuilder()
                        .setWorldSize(2)
                        .setNodeEntry(getScriptPathFromResources(), "inference")
                        .setProperty(
                                MLConstants.CONFIG_STORAGE_TYPE, MLConstants.STORAGE_LOCAL_FILE)
                        .setProperty("model_save_path", modelPath)
                        .setProperty("input_types", "FLOAT_64")
                        .setProperty("output_types", "FLOAT_64,FLOAT_64")
                        .build();
        final Table output =
                PyTorchUtils.inference(
                        statementSet,
                        table,
                        config,
                        Schema.newBuilder()
                                .column("x", DataTypes.DOUBLE())
                                .column("y", DataTypes.DOUBLE())
                                .build());
        statementSet.addInsert(
                TableDescriptor.forConnector("filesystem")
                        .format("csv")
                        .option("path", inferenceOutputPath)
                        .build(),
                output);
        statementSet.execute().await();
    }

    private static void train(
            String modelPath, Integer epoch, StreamStatementSet statementSet, Table sample)
            throws InterruptedException, ExecutionException {
        final PyTorchClusterConfig config =
                PyTorchClusterConfig.newBuilder()
                        .setWorldSize(2)
                        .setNodeEntry(getScriptPathFromResources(), "train")
                        .setProperty(
                                MLConstants.CONFIG_STORAGE_TYPE, MLConstants.STORAGE_LOCAL_FILE)
                        .setProperty("model_save_path", modelPath)
                        .setProperty("input_types", "FLOAT_64,FLOAT_64")
                        .build();

        PyTorchUtils.train(statementSet, sample, config, epoch);
        statementSet.execute().await();
    }

    private static String getScriptPathFromResources() {
        final URL resource =
                Thread.currentThread().getContextClassLoader().getResource("linear.py");
        if (resource == null) {
            throw new RuntimeException(String.format("Fail to find resource %s", "linear.py"));
        }
        return resource.getPath();
    }
}
