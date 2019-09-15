package com.alibaba.flink.ml.workflow.components;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.TableEnvironment;

import java.util.HashSet;
import java.util.Set;

public class ComponentContext {
	private StreamExecutionEnvironment streamEnv;
	private TableEnvironment tableEnv;
	private Set<String> sourceTables = new HashSet<>();

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
}
