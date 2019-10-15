package com.alibaba.flink.ml.workflow.components.examples;

import org.apache.flink.table.sinks.TableSink;
import org.apache.flink.table.sources.TableSource;

import com.alibaba.flink.ml.workflow.ExampleProto;
import com.alibaba.flink.ml.workflow.RunModeProto;

public interface ExampleCreator {
	TableSource createSource(ExampleProto.Builder exampleProto, RunModeProto runMode) throws Exception;
	TableSink createSink(ExampleProto.Builder exampleProto, RunModeProto runMode) throws Exception;
}
