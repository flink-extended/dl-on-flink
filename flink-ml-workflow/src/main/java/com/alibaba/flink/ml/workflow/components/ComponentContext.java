package com.alibaba.flink.ml.workflow.components;

import org.apache.flink.api.java.ExecutionEnvironment;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.TableSchema;

import com.alibaba.flink.ml.workflow.RunModeProto;
import com.alibaba.flink.ml.workflow.SchemaProto;

import java.util.HashMap;
import java.util.Map;

public class ComponentContext {
	private StreamExecutionEnvironment streamEnv;
	private ExecutionEnvironment batchEnv;
	private TableEnvironment tableEnv;
	private Map<String, Table> tableMap = new HashMap<>();
	private Map<String, Table> sinkTableMap = new HashMap<>();
	private Map<String, SchemaProto.Builder> schemaMap = new HashMap<>();

	private RunModeProto runMode;

	public ComponentContext(StreamExecutionEnvironment streamEnv, TableEnvironment tableEnv, RunModeProto runModeProto) {
		this.streamEnv = streamEnv;
		this.tableEnv = tableEnv;
		this.runMode = runModeProto;
	}
	public ComponentContext(ExecutionEnvironment batchEnv, TableEnvironment tableEnv, RunModeProto runModeProto) {
		this.batchEnv = batchEnv;
		this.tableEnv = tableEnv;
		this.runMode = runModeProto;
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

	public void registerTable(String name, Table table){
		tableMap.put(name, table);
	}

	public Table getTable(String name){
		return tableMap.get(name);
	}

	public ExecutionEnvironment getBatchEnv() {
		return batchEnv;
	}

	public void setBatchEnv(ExecutionEnvironment batchEnv) {
		this.batchEnv = batchEnv;
	}

	public boolean isBatch(){
		return RunModeProto.BATCH == runMode;
	}

	public boolean isStream(){
		return !isBatch();
	}

	public void registerSinkTable(String name, Table table){
		sinkTableMap.put(name, table);
	}

	public void writeDataToSink(){
		for(Map.Entry<String, Table>entry: sinkTableMap.entrySet()){
			entry.getValue().insertInto(entry.getKey());
		}
	}
	public void registerSchema(String name, SchemaProto.Builder tableSchema){
		schemaMap.put(name, tableSchema);
	}

	public SchemaProto.Builder getSchema(String name){
		return schemaMap.get(name);
	}
}
