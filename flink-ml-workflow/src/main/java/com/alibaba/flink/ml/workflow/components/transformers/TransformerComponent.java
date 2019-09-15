package com.alibaba.flink.ml.workflow.components.transformers;

import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;

import com.alibaba.flink.ml.workflow.TransformerProto;
import com.alibaba.flink.ml.workflow.components.Component;
import com.alibaba.flink.ml.workflow.components.ComponentContext;
import com.google.protobuf.Message;

public class TransformerComponent implements Component {
	@Override
	public void translate(Message message, ComponentContext context) throws Exception {
		TransformerProto transformerProto = (TransformerProto)message;
		TableEnvironment tableEnv = context.getTableEnv();
		Table inputTable = tableEnv.scan(transformerProto.getInputExampleList(0).getMeta().getName());
		TestTransformer testTransformer = new TestTransformer();
		Table outputTable = testTransformer.transform(tableEnv, inputTable);
		outputTable.insertInto(transformerProto.getOutputExampleList(0).getMeta().getName());
	}
}
