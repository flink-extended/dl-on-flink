package com.alibaba.flink.ml.workflow.components;

public interface ContextHandler {
	void setContext(ComponentContext context);
	ComponentContext getContext();
}
