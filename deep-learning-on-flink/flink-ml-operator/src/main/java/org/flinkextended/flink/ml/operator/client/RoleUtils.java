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

import org.flinkextended.flink.ml.cluster.ExecutionMode;
import org.flinkextended.flink.ml.cluster.MLConfig;
import org.flinkextended.flink.ml.cluster.role.AMRole;
import org.flinkextended.flink.ml.cluster.role.BaseRole;
import org.flinkextended.flink.ml.operator.ops.MLFlatMapOp;
import org.flinkextended.flink.ml.operator.ops.sink.DummySink;
import org.flinkextended.flink.ml.operator.ops.source.NodeSource;
import org.flinkextended.flink.ml.operator.util.TypeUtil;
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
import org.apache.flink.table.api.bridge.java.internal.StreamTableEnvironmentImpl;
import org.apache.flink.table.api.internal.TableEnvironmentInternal;
import org.apache.flink.table.catalog.ResolvedSchema;
import org.apache.flink.types.Row;


/**
 * a helper function to create machine learning cluster.
 * 1. create application master.
 * 2. create a group of machine learning nodes as a named role.
 */
public class RoleUtils {
    private static final TypeInformation<String> DUMMY_TI = getTypeInfo(String.class);

    static final Schema DUMMY_SCHEMA = Schema.newBuilder()
            .column("a", DataTypes.STRING()).build();

    /**
     * Run ML program for DataStream.
     *
     * @param streamEnv The Flink StreamExecutionEnvironment
     * @param mode      The mode of the program - can be either TRAIN or INFERENCE
     * @param input     The input DataStream
     * @param mlConfig  Configurations for the  program
     * @param outTI     The TypeInformation for the output DataStream. If it's null, a dummy sink will be connected
     *                  to the returned DataStream. Otherwise, caller is responsible to add sink to the output
     *                  DataStream before executing the graph.
     */
    public static <IN, OUT> DataStream<OUT> addRole(StreamExecutionEnvironment streamEnv, ExecutionMode mode,
                                                    DataStream<IN> input, MLConfig mlConfig,
                                                    TypeInformation<OUT> outTI, BaseRole role) {
        if (null != input) {
            mlConfig.addProperty(MLConstants.CONFIG_JOB_HAS_INPUT, "true");
        }
        TypeInformation workerTI = outTI == null ? DUMMY_TI : outTI;
        DataStream worker = null;
        int workerParallelism = mlConfig.getRoleParallelismMap().get(role.name());
        if (input == null) {
            worker = streamEnv.addSource(NodeSource.createSource(mode, role, mlConfig, workerTI))
                    .setParallelism(workerParallelism).name(role.name());
        } else {
            FlatMapFunction flatMapper = new MLFlatMapOp<>(mode, role, mlConfig, input.getType(), workerTI);

            worker = input.flatMap(flatMapper)
                    .setParallelism(workerParallelism).name(role.name());
        }

        if (outTI == null) {
            if (worker != null) {
                worker.addSink(new DummySink<>()).setParallelism(workerParallelism)
                        .name(MLConstants.DISPLAY_NAME_DUMMY_SINK);
            }
        }
        return worker;
    }

    /**
     * add application master role to machine learning cluster.
     *
     * @param streamEnv flink stream environment
     * @param mlConfig  machine learning configuration
     */
    public static void addAMRole(StreamExecutionEnvironment streamEnv, MLConfig mlConfig) {
        streamEnv.addSource(NodeSource.createSource(ExecutionMode.OTHER, new AMRole(), mlConfig, DUMMY_TI))
                .setParallelism(1).name(new AMRole().name())
                .addSink(new DummySink<>()).setParallelism(1);

    }

    /**
     * Run ML program for DataStream.
     *
     * @param tableEnv     The Flink TableEnvironment
     * @param statementSet The StatementSet created by the given TableEnvironment
     * @param mode         The mode of the program - can be either TRAIN or INFERENCE
     * @param input        The input DataStream
     * @param mlConfig     Configurations for the program
     * @param outputSchema The TableSchema for the output DataStream. If it's null, a dummy sink will be connected
     *                     to the returned DataStream. Otherwise, caller is responsible to add sink to the output
     *                     DataStream before executing the graph.
     * @param role         machine learning a group of nodes name.
     */
    public static Table addRole(TableEnvironment tableEnv, StatementSet statementSet, ExecutionMode mode,
                                Table input, MLConfig mlConfig,
                                Schema outputSchema, BaseRole role) {
        if (null != input) {
            mlConfig.addProperty(MLConstants.CONFIG_JOB_HAS_INPUT, "true");
        }
        Table worker;
        Schema workerSchema = outputSchema != null ? outputSchema : DUMMY_SCHEMA;
        final ResolvedSchema resolvedSchema =
                workerSchema.resolve(((TableEnvironmentInternal) tableEnv).getCatalogManager().getSchemaResolver());
        int workerParallelism = mlConfig.getRoleParallelismMap().get(role.name());
        if (input == null) {
            final DataStream<Row> source = ((StreamTableEnvironmentImpl) tableEnv).execEnv()
                    .addSource(NodeSource.createSource(mode, role, mlConfig,
                            TypeUtil.schemaToRowTypeInfo(resolvedSchema)))
                    .setParallelism(workerParallelism);

            worker = dsToTable(source, tableEnv);
        } else {
            DataStream<Row> toDataStream = tableToDS(input, tableEnv);
            FlatMapFunction<Row, Row> flatMapper = new MLFlatMapOp<>(mode, role, mlConfig, toDataStream.getType(),
                    TypeUtil.schemaToRowTypeInfo(resolvedSchema));

            DataStream<Row> workerStream = toDataStream.flatMap(flatMapper)
                    .setParallelism(workerParallelism).name(role.name());
            worker = dsToTable(workerStream, tableEnv);
        }
        if (outputSchema == null) {
            if (worker != null) {
                tableEnv.createTemporaryTable(role.name() + "_table_sink",
                        TableDescriptor
                                .forConnector("DummyTable")
                                .schema(DUMMY_SCHEMA)
                                .build());
                statementSet.addInsert(role.name() + "_table_sink", worker);
            }
        }
        return worker;
    }

    /**
     * add application master role to machine learning cluster.
     *
     * @param tableEnv     flink table environment
     * @param statementSet The StatementSet created by the given TableEnvironment
     * @param mlConfig     Configurations for the program
     */
    public static void addAMRole(TableEnvironment tableEnv, StatementSet statementSet, MLConfig mlConfig) {
        final ResolvedSchema resolvedSchema =
                DUMMY_SCHEMA.resolve(((TableEnvironmentInternal) tableEnv).getCatalogManager().getSchemaResolver());
        final DataStream<Row> source = ((StreamTableEnvironmentImpl) tableEnv).execEnv()
                .addSource(NodeSource.createSource(ExecutionMode.OTHER, new AMRole(), mlConfig,
                        TypeUtil.schemaToRowTypeInfo(resolvedSchema)))
                .setParallelism(1);

        Table am = dsToTable(source, tableEnv);

        tableEnv.createTemporaryTable("am_table_stream_sink",
                TableDescriptor
                        .forConnector("DummyTable")
                        .schema(DUMMY_SCHEMA)
                        .build());

        statementSet.addInsert("am_table_stream_sink", am);
    }

    private static <OUT> TypeInformation<OUT> getTypeInfo(Class<OUT> clazz) {
        return clazz == null ? null : TypeInformation.of(clazz);
    }

    public static Table dsToTable(DataStream<Row> dataStream, TableEnvironment tableEnv) {
        return ((StreamTableEnvironment) tableEnv).fromDataStream(dataStream);
    }

    public static DataStream<Row> tableToDS(Table table, TableEnvironment tableEnv) {
        if (table == null) {
            return null;
        }
        return ((StreamTableEnvironment) tableEnv).toAppendStream(table,
                TypeUtil.schemaToRowTypeInfo(table.getSchema()));

    }
}
