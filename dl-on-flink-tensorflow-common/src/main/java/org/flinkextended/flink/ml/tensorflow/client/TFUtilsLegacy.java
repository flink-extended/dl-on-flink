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

import org.flinkextended.flink.ml.cluster.ExecutionMode;
import org.flinkextended.flink.ml.cluster.role.PsRole;
import org.flinkextended.flink.ml.cluster.role.WorkerRole;
import org.flinkextended.flink.ml.operator.client.RoleUtils;
import org.flinkextended.flink.ml.operator.util.PythonFileUtil;
import org.flinkextended.flink.ml.operator.util.TypeUtil;
import org.flinkextended.flink.ml.tensorflow.cluster.ChiefRole;
import org.flinkextended.flink.ml.tensorflow.cluster.TFAMStateMachineImpl;
import org.flinkextended.flink.ml.tensorflow.cluster.TensorBoardRole;
import org.flinkextended.flink.ml.tensorflow.cluster.node.runner.TFMLRunner;
import org.flinkextended.flink.ml.tensorflow.cluster.node.runner.TensorBoardPythonRunner;
import org.flinkextended.flink.ml.tensorflow.data.TFRecordReaderImpl;
import org.flinkextended.flink.ml.tensorflow.data.TFRecordWriterImpl;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.api.Schema;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableDescriptor;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.apache.flink.table.api.internal.TableEnvironmentInternal;
import org.apache.flink.table.catalog.ResolvedSchema;
import org.apache.flink.types.Row;

import com.google.common.base.Preconditions;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.concurrent.atomic.AtomicInteger;

/** Tensorflow on Flink API to run Tensorflow training and inference in Flink. */
@Deprecated
public class TFUtilsLegacy {
    private static final Logger LOG = LoggerFactory.getLogger(TFUtilsLegacy.class);
    static final Schema DUMMY_SCHEMA = Schema.newBuilder().column("a", DataTypes.STRING()).build();
    private static AtomicInteger count = new AtomicInteger(0);

    /* ***********************************************
     ******  API for Streaming Environment   **********
     ************************************************* */

    /**
     * Run TF train for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param tfConfig Configurations for the TF program.
     * @return the returned DataStream. Otherwise, caller is responsible to add sink to the output
     *     DataStream before executing the graph.
     */
    public static <OUT> DataStream<OUT> train(
            StreamExecutionEnvironment streamEnv, TFConfigBase tfConfig) throws IOException {
        return train(streamEnv, tfConfig, (TypeInformation<OUT>) null);
    }

    /**
     * Run TF train for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param tfConfig Configurations for the TF program.
     * @param outClazz output stream data class.
     * @return the returned DataStream. Otherwise, caller is responsible to add sink to the output
     *     DataStream before executing the graph.
     */
    public static <OUT> DataStream<OUT> train(
            StreamExecutionEnvironment streamEnv, TFConfigBase tfConfig, Class<OUT> outClazz)
            throws IOException {
        return train(streamEnv, tfConfig, getTypeInfo(outClazz));
    }

    /**
     * Run TF train for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param tfConfig Configurations for the TF program.
     * @param outTI output stream data TypeInformation.
     * @return the returned DataStream. Otherwise, caller is responsible to add sink to the output
     *     DataStream before executing the graph.
     */
    public static <OUT> DataStream<OUT> train(
            StreamExecutionEnvironment streamEnv, TFConfigBase tfConfig, TypeInformation<OUT> outTI)
            throws IOException {
        return run(streamEnv, ExecutionMode.TRAIN, null, tfConfig, outTI);
    }

    /**
     * Run TF train for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param tfConfig Configurations for the TF program.
     * @param input tensorflow job input stream.
     * @return the returned DataStream. Otherwise, caller is responsible to add sink to the output
     *     DataStream before executing the graph.
     */
    public static <IN, OUT> DataStream<OUT> train(
            StreamExecutionEnvironment streamEnv, DataStream<IN> input, TFConfigBase tfConfig)
            throws IOException {
        return train(streamEnv, input, tfConfig, (TypeInformation<OUT>) null);
    }

    /**
     * Run TF train for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param tfConfig Configurations for the TF program.
     * @param input tensorflow job input stream.
     * @param outClazz output stream data class.
     * @return the returned DataStream. Otherwise, caller is responsible to add sink to the output
     *     DataStream before executing the graph.
     */
    public static <IN, OUT> DataStream<OUT> train(
            StreamExecutionEnvironment streamEnv,
            DataStream<IN> input,
            TFConfigBase tfConfig,
            Class<OUT> outClazz)
            throws IOException {
        return train(streamEnv, input, tfConfig, getTypeInfo(outClazz));
    }

    /**
     * Run TF train for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param tfConfig Configurations for the TF program.
     * @param input tensorflow job input stream.
     * @param outTI output stream data TypeInformation.
     * @return the returned DataStream. Otherwise, caller is responsible to add sink to the output
     *     DataStream before executing the graph.
     */
    public static <IN, OUT> DataStream<OUT> train(
            StreamExecutionEnvironment streamEnv,
            DataStream<IN> input,
            TFConfigBase tfConfig,
            TypeInformation<OUT> outTI)
            throws IOException {
        return run(streamEnv, ExecutionMode.TRAIN, input, tfConfig, outTI);
    }

    /**
     * Run TF inference for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param tfConfig Configurations for the TF program.
     * @param input tensorflow job input stream.
     * @param outClazz output stream data class.
     * @return the returned DataStream. Otherwise, caller is responsible to add sink to the output
     *     DataStream before executing the graph.
     */
    public static <IN, OUT> DataStream<OUT> inference(
            StreamExecutionEnvironment streamEnv,
            DataStream<IN> input,
            TFConfigBase tfConfig,
            Class<OUT> outClazz)
            throws IOException {
        return inference(streamEnv, input, tfConfig, getTypeInfo(outClazz));
    }

    /**
     * Run TF inference for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param tfConfig Configurations for the TF program.
     * @param input tensorflow job input stream.
     * @param outTI output stream data TypeInformation.
     * @return the returned DataStream. Otherwise, caller is responsible to add sink to the output
     *     DataStream before executing the graph.
     */
    public static <IN, OUT> DataStream<OUT> inference(
            StreamExecutionEnvironment streamEnv,
            DataStream<IN> input,
            TFConfigBase tfConfig,
            TypeInformation<OUT> outTI)
            throws IOException {
        return run(streamEnv, ExecutionMode.INFERENCE, input, tfConfig, outTI);
    }

    /**
     * Run TF for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param mode The mode of the TF program - can be either TRAIN or INFERENCE.
     * @param input The input DataStream.
     * @param tfConfig Configurations for the TF program.
     * @param outClazz The class for the output DataStream. If it's null, a dummy sink will be
     *     connected.
     * @return the returned DataStream. Otherwise, caller is responsible to add sink to the output
     *     DataStream before executing the graph.
     */
    public static <IN, OUT> DataStream<OUT> run(
            StreamExecutionEnvironment streamEnv,
            ExecutionMode mode,
            DataStream<IN> input,
            TFConfigBase tfConfig,
            Class<OUT> outClazz)
            throws IOException {
        return run(streamEnv, mode, input, tfConfig, getTypeInfo(outClazz));
    }

    /**
     * Run TF for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param mode The mode of the TF program - can be either TRAIN or INFERENCE.
     * @param input The input DataStream.
     * @param tfConfig Configurations for the TF program.
     * @return the returned DataStream. Otherwise, caller is responsible to add sink to the output
     *     DataStream before executing the graph.
     */
    public static <IN, OUT> DataStream<OUT> run(
            StreamExecutionEnvironment streamEnv,
            ExecutionMode mode,
            DataStream<IN> input,
            TFConfigBase tfConfig)
            throws IOException {
        return run(streamEnv, mode, input, tfConfig, (TypeInformation<OUT>) null);
    }

    private static void setTFDefaultConfig(TFConfigBase tfConfig) {
        tfConfig.getProperties()
                .put(MLConstants.ML_RUNNER_CLASS, TFMLRunner.class.getCanonicalName());
        tfConfig.getProperties()
                .put(
                        MLConstants.AM_STATE_MACHINE_CLASS,
                        TFAMStateMachineImpl.class.getCanonicalName());
        tfConfig.getProperties()
                .put(MLConstants.RECORD_READER_CLASS, TFRecordReaderImpl.class.getCanonicalName());
        tfConfig.getProperties()
                .put(MLConstants.RECORD_WRITER_CLASS, TFRecordWriterImpl.class.getCanonicalName());
    }

    /**
     * start a tensorboard service.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param tfConfig Configurations for the TF program.
     * @throws IOException
     */
    public static void startTensorBoard(StreamExecutionEnvironment streamEnv, TFConfigBase tfConfig)
            throws IOException {
        TFConfigBase tbConfig = buildTensorBoardConfig(streamEnv, tfConfig);
        RoleUtils.addRole(
                streamEnv,
                ExecutionMode.OTHER,
                null,
                tbConfig.getMlConfig(),
                null,
                new TensorBoardRole());
    }

    private static TFConfigBase buildTensorBoardConfig(
            StreamExecutionEnvironment streamEnv, TFConfigBase tfConfig) throws IOException {
        TFConfigBase tbConfig = tfConfig.deepCopy();
        tbConfig.getProperties()
                .put(
                        MLConstants.SCRIPT_RUNNER_CLASS,
                        TensorBoardPythonRunner.class.getCanonicalName());
        tbConfig.getMlConfig().getRoleParallelismMap().put(new TensorBoardRole().name(), 1);
        PythonFileUtil.registerPythonFiles(streamEnv, tbConfig.getMlConfig());
        return tbConfig;
    }

    /**
     * start a tensorboard service.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment.
     * @param tableEnv The Flink TableEnvironment.
     * @param statementSet The StatementSet created by the given TableEnvironment
     * @param tfConfig Configurations for the TF program.
     * @throws IOException
     */
    public static void startTensorBoard(
            StreamExecutionEnvironment streamEnv,
            TableEnvironment tableEnv,
            StatementSet statementSet,
            TFConfigBase tfConfig)
            throws IOException {
        TFConfigBase tbConfig = buildTensorBoardConfig(streamEnv, tfConfig);
        RoleUtils.addRole(
                tableEnv,
                statementSet,
                ExecutionMode.OTHER,
                null,
                tbConfig.getMlConfig(),
                null,
                new TensorBoardRole());
    }

    /**
     * Run TF for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment
     * @param mode The mode of the TF program - can be either TRAIN or INFERENCE
     * @param input The input DataStream
     * @param tfConfig Configurations for the TF program
     * @param outTI The TypeInformation for the output DataStream. If it's null, a dummy sink will
     *     be connected to the returned DataStream. Otherwise, caller is responsible to add sink to
     *     the output DataStream before executing the graph.
     */
    public static <IN, OUT> DataStream<OUT> run(
            StreamExecutionEnvironment streamEnv,
            ExecutionMode mode,
            DataStream<IN> input,
            TFConfigBase tfConfig,
            TypeInformation<OUT> outTI)
            throws IOException {
        if (null != input) {
            tfConfig.addProperty(MLConstants.CONFIG_JOB_HAS_INPUT, "true");
        }
        setTFDefaultConfig(tfConfig);
        PythonFileUtil.registerPythonFiles(streamEnv, tfConfig.getMlConfig());
        TFConfigBase nodeConfig = toChiefTypeConfig(tfConfig);
        RoleUtils.addAMRole(streamEnv, tfConfig.getMlConfig());
        if (tfConfig.getPsNum() > 0) {
            RoleUtils.addRole(streamEnv, mode, null, nodeConfig.getMlConfig(), null, new PsRole());
        }
        return getWorkerDataStream(streamEnv, mode, input, nodeConfig, outTI).getLeft();
    }

    private static <IN, OUT> Pair<DataStream<OUT>, DataStream<OUT>> getWorkerDataStream(
            StreamExecutionEnvironment streamEnv,
            ExecutionMode mode,
            DataStream<IN> input,
            TFConfigBase tfConfig,
            final TypeInformation<OUT> outTI)
            throws IOException {
        DataStream worker = null;
        DataStream chief = null;
        boolean isWorkerZeroAlone = tfConfig.isWorkerZeroAlone();
        if (input == null) {
            if (isWorkerZeroAlone) {
                chief =
                        RoleUtils.addRole(
                                streamEnv,
                                mode,
                                null,
                                tfConfig.getMlConfig(),
                                outTI,
                                new ChiefRole());
                if (tfConfig.getWorkerNum() > 0) {
                    worker =
                            RoleUtils.addRole(
                                    streamEnv,
                                    mode,
                                    null,
                                    tfConfig.getMlConfig(),
                                    outTI,
                                    new WorkerRole());
                }
            } else {
                worker =
                        RoleUtils.addRole(
                                streamEnv,
                                mode,
                                null,
                                tfConfig.getMlConfig(),
                                outTI,
                                new WorkerRole());
            }
        } else {
            final boolean hasScript = hasScript(tfConfig);
            if (hasScript) {
                worker =
                        RoleUtils.addRole(
                                streamEnv,
                                mode,
                                input,
                                tfConfig.getMlConfig(),
                                outTI,
                                new WorkerRole());

            } else {
                FlatMapFunction flatMapper =
                        tfConfig.getInferenceFlatMapFunction(
                                new WorkerRole(), tfConfig.getMlConfig(), input.getType(), outTI);
                worker =
                        input.flatMap(flatMapper)
                                .setParallelism(tfConfig.getWorkerNum())
                                .name(new WorkerRole().name());
            }
        }
        return Pair.of(worker, chief);
    }

    /* **************************************************
     ******************  API for Table ****************
     ************************************************** */

    /**
     * Run TF train for flink table api.
     *
     * @param streamEnv
     * @param tableEnv The Flink TableEnvironment.
     * @param statementSet The StatementSet created by the given TableEnvironment
     * @param input The input Table.
     * @param tfConfig Configurations for the TF program.
     * @param outSchema The TableSchema for the output Table. If it's null, a dummy sink will be
     *     connected.
     * @return output Table. Otherwise, caller is responsible to add sink to the output Table before
     *     executing the graph.
     */
    public static Table train(
            StreamExecutionEnvironment streamEnv,
            TableEnvironment tableEnv,
            StatementSet statementSet,
            Table input,
            TFConfigBase tfConfig,
            Schema outSchema)
            throws IOException {
        return run(
                streamEnv, tableEnv, statementSet, ExecutionMode.TRAIN, input, tfConfig, outSchema);
    }

    /**
     * Run TF inference for flink table api.
     *
     * @param streamEnv
     * @param tableEnv The Flink TableEnvironment.
     * @param statementSet The StatementSet created by the given TableEnvironment
     * @param input The input Table.
     * @param tfConfig Configurations for the TF program.
     * @param outSchema The TableSchema for the output Table. If it's null, a dummy sink will be
     *     connected.
     * @return output Table. Otherwise, caller is responsible to add sink to the output Table before
     *     executing the graph.
     */
    public static Table inference(
            StreamExecutionEnvironment streamEnv,
            TableEnvironment tableEnv,
            StatementSet statementSet,
            Table input,
            TFConfigBase tfConfig,
            Schema outSchema)
            throws IOException {
        return run(
                streamEnv,
                tableEnv,
                statementSet,
                ExecutionMode.INFERENCE,
                input,
                tfConfig,
                outSchema);
    }

    /**
     * Run TF for Table.
     *
     * @param streamEnv
     * @param tableEnv The Flink TableEnvironment.
     * @param statementSet The StatementSet created by the given TableEnvironment
     * @param mode The mode of the TF program - can be either TRAIN or INFERENCE.
     * @param input The input Table.
     * @param tfConfig Configurations for the TF program.
     * @param outSchema The TableSchema for the output Table. If it's null, a dummy sink will be
     *     connected.
     * @return output Table. Otherwise, caller is responsible to add sink to the output Table before
     *     executing the graph.
     */
    public static Table run(
            StreamExecutionEnvironment streamEnv,
            TableEnvironment tableEnv,
            StatementSet statementSet,
            ExecutionMode mode,
            Table input,
            TFConfigBase tfConfig,
            Schema outSchema)
            throws IOException {
        final boolean hasScript = hasScript(tfConfig);
        Preconditions.checkArgument(
                hasScript || mode == ExecutionMode.INFERENCE,
                "Python script can be omitted only for inference");
        Preconditions.checkArgument(
                hasScript || input != null, "Input table and python script can't both be null");
        if (null != input) {
            tfConfig.addProperty(MLConstants.CONFIG_JOB_HAS_INPUT, "true");
        }
        setTFDefaultConfig(tfConfig);
        Table worker = null;
        Table chief = null;
        TFConfigBase nodeConfig = toChiefTypeConfig(tfConfig);
        DataStream<Row> toDataStream = tableToDS(input, tableEnv);

        if (hasScript) {
            PythonFileUtil.registerPythonFiles(streamEnv, nodeConfig.getMlConfig());
            RoleUtils.addAMRole(tableEnv, statementSet, tfConfig.getMlConfig());
            if (nodeConfig.getPsNum() > 0) {
                RoleUtils.addRole(
                        tableEnv,
                        statementSet,
                        mode,
                        null,
                        nodeConfig.getMlConfig(),
                        null,
                        new PsRole());
            }
        }
        Schema workerSchema = outSchema != null ? outSchema : DUMMY_SCHEMA;
        final ResolvedSchema resolvedSchema =
                workerSchema.resolve(
                        ((TableEnvironmentInternal) tableEnv)
                                .getCatalogManager()
                                .getSchemaResolver());
        Pair<DataStream<Row>, DataStream<Row>> workerAndChief =
                getWorkerDataStream(
                        streamEnv,
                        mode,
                        toDataStream,
                        nodeConfig,
                        TypeUtil.schemaToRowTypeInfo(resolvedSchema));
        if (workerAndChief.getLeft() != null) {
            worker = dsToTable(workerAndChief.getLeft(), tableEnv);
        }
        if (workerAndChief.getRight() != null) {
            chief = dsToTable(workerAndChief.getRight(), tableEnv);
        }
        if (outSchema == null) {
            if (worker != null) {
                writeToDummySink(worker, tableEnv, statementSet);
            }
            if (chief != null) {
                writeToDummySink(chief, tableEnv, statementSet);
            }
        }
        return worker;
    }

    private static TFConfigBase toChiefTypeConfig(TFConfigBase tfConfig) {
        boolean isWorkerZeroAlone = tfConfig.isWorkerZeroAlone();
        TFConfigBase realConfig;
        if (isWorkerZeroAlone) {
            TFConfigBase chiefConfig = tfConfig.deepCopy();
            chiefConfig.getMlConfig().getRoleParallelismMap().put(new ChiefRole().name(), 1);
            if (tfConfig.getWorkerNum() > 1) {
                chiefConfig
                        .getMlConfig()
                        .getRoleParallelismMap()
                        .put(new WorkerRole().name(), tfConfig.getWorkerNum() - 1);
            } else {
                chiefConfig.getMlConfig().getRoleParallelismMap().remove(new WorkerRole().name());
            }
            realConfig = chiefConfig;
        } else {
            realConfig = tfConfig;
        }
        return realConfig;
    }

    private static Table dsToTable(DataStream<Row> dataStream, TableEnvironment tableEnv) {
        return ((StreamTableEnvironment) tableEnv).fromDataStream(dataStream);
    }

    private static DataStream<Row> tableToDS(Table table, TableEnvironment tableEnv) {
        if (table == null) {
            return null;
        }
        return ((StreamTableEnvironment) tableEnv)
                .toAppendStream(table, TypeUtil.schemaToRowTypeInfo(table.getSchema()));
    }

    private static <OUT> TypeInformation<OUT> getTypeInfo(Class<OUT> clazz) {
        return clazz == null ? null : TypeInformation.of(clazz);
    }

    private static void writeToDummySink(
            Table tbl, TableEnvironment tableEnvironment, StatementSet statementSet) {
        String sinkName = String.format("dummy_sink_%s", count.getAndIncrement());
        tableEnvironment.createTemporaryTable(
                sinkName, TableDescriptor.forConnector("DummyTable").schema(DUMMY_SCHEMA).build());
        //		tableEnvironment.connect(new DummyTable())
        //				.withSchema(new Schema().schema(DUMMY_SCHEMA))
        //				.createTemporaryTable(sinkName);
        statementSet.addInsert(sinkName, tbl);
    }

    private static boolean hasScript(TFConfigBase tfConfig) {
        return tfConfig.getPythonFiles() != null && tfConfig.getPythonFiles().length > 0;
    }
}
