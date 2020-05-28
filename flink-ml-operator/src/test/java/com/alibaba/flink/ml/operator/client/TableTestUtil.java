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

package com.alibaba.flink.ml.operator.client;

import com.alibaba.flink.ml.cluster.MLConfig;
import com.alibaba.flink.ml.cluster.role.AMRole;
import com.alibaba.flink.ml.cluster.role.WorkerRole;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.graph.StreamGraph;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.types.Row;

public class TableTestUtil {

    public static void execTableJobCustom(MLConfig mlConfig, StreamExecutionEnvironment streamEnv, TableEnvironment tableEnv, Table table,
                                          String sinkTable) throws Exception {
        FlinkJobHelper helper = new FlinkJobHelper();
        helper.like(new WorkerRole().name(), mlConfig.getRoleParallelismMap().get(new WorkerRole().name()));
        helper.like(new AMRole().name(), 1);
        helper.like(MLTestConstants.SOURCE_CONVERSION, 1);
        helper.like(MLTestConstants.SINK_CONVERSION, 1);
        helper.like("debug_source", 1);
        helper.like(MLTestConstants.SINK, 1);
        DataStream<Row> rowDataStream = RoleUtils.tableToDS(table, tableEnv);
        StreamGraph streamGraph =  helper.matchStreamGraph(streamEnv.getStreamGraph(
                StreamExecutionEnvironment.DEFAULT_JOB_NAME,
                true));
        StatementSet statementSet = RoleUtils.getStatementSet(tableEnv);
        if (sinkTable != null) {
            Table table1 = RoleUtils.dsToTable(rowDataStream, tableEnv);
            statementSet.addInsert(sinkTable, table1);
        }
        statementSet.execute().getJobClient().get().getJobExecutionResult(Thread.currentThread().getContextClassLoader())
                .get();
//        String plan = FlinkJobHelper.streamPlan(streamGraph);
//        System.out.println(plan);
//        streamEnv.execute();
//        tableEnv.execute("hh");
    }
}
