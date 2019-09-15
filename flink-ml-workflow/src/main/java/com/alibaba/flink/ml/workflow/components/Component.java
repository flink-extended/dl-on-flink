package com.alibaba.flink.ml.workflow.components;

import com.google.protobuf.Message;

public interface Component {

	void translate(Message message, ComponentContext context) throws Exception;
}
