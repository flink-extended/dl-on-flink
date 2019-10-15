package com.alibaba.flink.ml.workflow.components;

import com.google.protobuf.MessageOrBuilder;

public interface Component {

	void translate(MessageOrBuilder messageOrBuilder, ComponentContext context) throws Exception;
}
