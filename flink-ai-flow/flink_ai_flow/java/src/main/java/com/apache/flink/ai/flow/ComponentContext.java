/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package com.apache.flink.ai.flow;

import org.apache.flink.api.java.ExecutionEnvironment;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.StatementSet;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;

import java.util.HashMap;
import java.util.Map;

public class ComponentContext {

    private StreamExecutionEnvironment streamEnv;
    private ExecutionEnvironment batchEnv;
    private TableEnvironment tableEnv;

    public StatementSet getStatementSet() {
        return statementSet;
    }

    public void setStatementSet(StatementSet statementSet) {
        this.statementSet = statementSet;
    }

    private StatementSet statementSet;
    private Map<String, Table> tableMap = new HashMap<>();
    private Map<String, Table> sinkTableMap = new HashMap<>();
    private boolean isStream;
    private Long workflowExecutionId;


    public ComponentContext(StreamExecutionEnvironment streamEnv, TableEnvironment tableEnv, StatementSet statementSet,
            Long workflowExecutionId) {
        this.streamEnv = streamEnv;
        this.tableEnv = tableEnv;
        this.statementSet = statementSet;
        this.isStream = true;
        this.workflowExecutionId = workflowExecutionId;
    }

    public ComponentContext(ExecutionEnvironment batchEnv, TableEnvironment tableEnv, StatementSet statementSet,
            Long workflowExecutionId) {
        this.batchEnv = batchEnv;
        this.tableEnv = tableEnv;
        this.statementSet = statementSet;
        this.isStream = false;
        this.workflowExecutionId = workflowExecutionId;
    }

    public StreamExecutionEnvironment getStreamEnv() {
        return streamEnv;
    }

    public void setStreamEnv(StreamExecutionEnvironment streamEnv) {
        this.streamEnv = streamEnv;
    }

    public TableEnvironment getTableEnv() {
        return tableEnv;
    }

    public void setTableEnv(TableEnvironment tableEnv) {
        this.tableEnv = tableEnv;
    }

    public void registerTable(String name, Table table) {
        tableMap.put(name, table);
    }

    public Table getTable(String name) {
        return tableMap.get(name);
    }

    public ExecutionEnvironment getBatchEnv() {
        return batchEnv;
    }

    public void setBatchEnv(ExecutionEnvironment batchEnv) {
        this.batchEnv = batchEnv;
    }


    public void registerSinkTable(String name, Table table) {
        sinkTableMap.put(name, table);
    }

    public void writeDataToSink() {
        for (Map.Entry<String, Table> entry : sinkTableMap.entrySet()) {
            entry.getValue().insertInto(entry.getKey());
        }
    }

    public boolean isStream() {
        return this.isStream;
    }

    public boolean isBatch() {
        return !this.isStream;
    }

    public Long getWorkflowExecutionId() {
        return workflowExecutionId;
    }

    public void setWorkflowExecutionId(Long workflowExecutionId) {
        this.workflowExecutionId = workflowExecutionId;
    }
}