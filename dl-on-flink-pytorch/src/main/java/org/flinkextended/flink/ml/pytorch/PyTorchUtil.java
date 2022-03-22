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

import org.flinkextended.flink.ml.cluster.ExecutionMode;
import org.flinkextended.flink.ml.cluster.role.WorkerRole;
import org.flinkextended.flink.ml.operator.client.RoleUtils;
import org.flinkextended.flink.ml.operator.util.PythonFileUtil;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;

import java.io.IOException;

public class PyTorchUtil {

    /**
     * Run ML program for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param mode The mode of the program - can be either TRAIN or INFERENCE.
     * @param input The input DataStream.
     * @param pytorchConfig Configurations for the program.
     * @param outTI The TypeInformation for the output DataStream. If it's null, a dummy sink will
     *     be connected
     * @return to the returned DataStream. Otherwise, caller is responsible to add sink to the
     *     output DataStream before executing the graph.
     */
    public static <IN, OUT> DataStream<OUT> run(
            StreamExecutionEnvironment streamEnv,
            ExecutionMode mode,
            DataStream<IN> input,
            PyTorchConfig pytorchConfig,
            TypeInformation<OUT> outTI)
            throws IOException {
        pytorchConfig
                .getMlConfig()
                .getProperties()
                .put(MLConstants.ML_RUNNER_CLASS, PyTorchRunner.class.getCanonicalName());
        // flink register python script has bug
        PythonFileUtil.registerPythonFiles(streamEnv, pytorchConfig.getMlConfig());
        RoleUtils.addAMRole(streamEnv, pytorchConfig.getMlConfig());
        return RoleUtils.addRole(
                streamEnv, mode, input, pytorchConfig.getMlConfig(), outTI, new WorkerRole());
    }

    /**
     * Run ML program for table.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param tableEnv The Flink TableEnvironment.
     * @param statementSet
     * @param mode The mode of the program - can be either TRAIN or INFERENCE.
     * @param input The input DataStream.
     * @param pytorchConfig Configurations for the program.
     * @param outputSchema The TypeInformation for the output DataStream. If it's null, a dummy sink
     *     will be connected
     * @return to the returned DataStream. Otherwise, caller is responsible to add sink to the
     *     output DataStream before executing the graph.
     */
    public static Table run(
            StreamExecutionEnvironment streamEnv,
            TableEnvironment tableEnv,
            StatementSet statementSet,
            ExecutionMode mode,
            Table input,
            PyTorchConfig pytorchConfig,
            Schema outputSchema)
            throws IOException {
        pytorchConfig
                .getMlConfig()
                .getProperties()
                .put(MLConstants.ML_RUNNER_CLASS, PyTorchRunner.class.getCanonicalName());
        PythonFileUtil.registerPythonFiles(streamEnv, pytorchConfig.getMlConfig());
        RoleUtils.addAMRole(tableEnv, statementSet, pytorchConfig.getMlConfig());

        return RoleUtils.addRole(
                tableEnv,
                statementSet,
                mode,
                input,
                pytorchConfig.getMlConfig(),
                outputSchema,
                new WorkerRole());
    }

    /**
     * Run machine learning train job program for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param input The input DataStream.
     * @param pytorchConfig Configurations for the program.
     * @param outTI The TypeInformation for the output DataStream. If it's null, a dummy sink will
     *     be connected
     * @return to the returned DataStream. Otherwise, caller is responsible to add sink to the
     *     output DataStream before executing the graph.
     */
    public static <IN, OUT> DataStream<OUT> train(
            StreamExecutionEnvironment streamEnv,
            DataStream<IN> input,
            PyTorchConfig pytorchConfig,
            TypeInformation<OUT> outTI)
            throws IOException {

        return run(streamEnv, ExecutionMode.TRAIN, input, pytorchConfig, outTI);
    }

    /**
     * Run machine learning inference job program for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param input The input DataStream.
     * @param pytorchConfig Configurations for the program.
     * @param outTI The TypeInformation for the output DataStream. If it's null, a dummy sink will
     *     be connected
     * @return to the returned DataStream. Otherwise, caller is responsible to add sink to the
     *     output DataStream before executing the graph.
     */
    public static <IN, OUT> DataStream<OUT> inference(
            StreamExecutionEnvironment streamEnv,
            DataStream<IN> input,
            PyTorchConfig pytorchConfig,
            TypeInformation<OUT> outTI)
            throws IOException {

        return run(streamEnv, ExecutionMode.INFERENCE, input, pytorchConfig, outTI);
    }

    /**
     * Run machine learning train job program for table.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param statementSet The StatementSet created by the given TableEnvironment
     * @param input The input DataStream.
     * @param pytorchConfig Configurations for the program.
     * @param outputSchema The TableSchema for the output table. If it's null, a dummy sink will be
     *     connected
     * @return to the returned table. Otherwise, caller is responsible to add sink to the output
     *     DataStream before executing the graph.
     */
    public static Table train(
            StreamExecutionEnvironment streamEnv,
            TableEnvironment tableEnv,
            StatementSet statementSet,
            Table input,
            PyTorchConfig pytorchConfig,
            Schema outputSchema)
            throws IOException {
        return run(
                streamEnv,
                tableEnv,
                statementSet,
                ExecutionMode.TRAIN,
                input,
                pytorchConfig,
                outputSchema);
    }

    /**
     * Run machine learning inference job program for table.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param statementSet The StatementSet created by the given TableEnvironment
     * @param input The input DataStream.
     * @param pytorchConfig Configurations for the program.
     * @param outputSchema The TableSchema for the output table. If it's null, a dummy sink will be
     *     connected
     * @return to the returned table. Otherwise, caller is responsible to add sink to the output
     *     DataStream before executing the graph.
     */
    public static Table inference(
            StreamExecutionEnvironment streamEnv,
            TableEnvironment tableEnv,
            StatementSet statementSet,
            Table input,
            PyTorchConfig pytorchConfig,
            Schema outputSchema)
            throws IOException {
        return run(
                streamEnv,
                tableEnv,
                statementSet,
                ExecutionMode.INFERENCE,
                input,
                pytorchConfig,
                outputSchema);
    }
}
