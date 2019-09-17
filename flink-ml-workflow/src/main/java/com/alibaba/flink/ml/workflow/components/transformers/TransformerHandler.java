package com.alibaba.flink.ml.workflow.components.transformers;

import com.alibaba.flink.ml.workflow.TransformerProto;

public interface TransformerHandler {
	void setTransformerProto(TransformerProto transformerProto);
}
