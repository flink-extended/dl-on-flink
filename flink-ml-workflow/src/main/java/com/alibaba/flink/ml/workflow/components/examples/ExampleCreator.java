package com.alibaba.flink.ml.workflow.components.examples;

import org.apache.flink.table.sinks.TableSink;
import org.apache.flink.table.sources.TableSource;

import com.alibaba.flink.ml.workflow.ExampleProto;

public interface ExampleCreator {
	TableSource createSource(ExampleProto exampleProto) throws Exception;
	TableSink createSink(ExampleProto exampleProto) throws Exception;
}
