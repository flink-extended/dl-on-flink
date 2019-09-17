package com.alibaba.flink.ml.workflow.runtime;

import com.alibaba.flink.ml.workflow.ExecutionProto;
import com.alibaba.flink.ml.workflow.components.ComponentContext;

public interface JobParser {
	void parseJob(ExecutionProto.Builder executionProtoBuilder, ComponentContext context) throws Exception;
}
