package com.alibaba.flink.ml.workflow.components;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;

import java.util.HashMap;
import java.util.Map;

public class ComponentContext {
	private StreamExecutionEnvironment streamEnv;
	private TableEnvironment tableEnv;
	private Map<String, Table> tableMap = new HashMap<>();

	public ComponentContext(StreamExecutionEnvironment streamEnv, TableEnvironment tableEnv) {
		this.streamEnv = streamEnv;
		this.tableEnv = tableEnv;
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
}
