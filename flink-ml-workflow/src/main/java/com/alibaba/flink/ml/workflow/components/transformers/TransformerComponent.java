package com.alibaba.flink.ml.workflow.components.transformers;

import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;

import com.alibaba.flink.ml.workflow.ExampleProto;
import com.alibaba.flink.ml.workflow.TransformerProto;
import com.alibaba.flink.ml.workflow.common.ReflectUtil;
import com.alibaba.flink.ml.workflow.components.Component;
import com.alibaba.flink.ml.workflow.components.ComponentContext;
import com.alibaba.flink.ml.workflow.components.examples.ExampleUtils;
import com.google.protobuf.Message;

public class TransformerComponent implements Component {

	@Override
	public void translate(Message message, ComponentContext context) throws Exception {
		TransformerProto transformerProto = (TransformerProto)message;
		TableEnvironment tableEnv = context.getTableEnv();
		String className = transformerProto.getTransformerClassName();
		BaseTransformer transformer = ReflectUtil.createInstance(className, new Class[0], new Object[0]);
		transformer.setContext(context);
		transformer.setTransformerProto(transformerProto);
		Table outputTable = transformer.transform(tableEnv, null);
		ExampleProto exampleProto = transformerProto.getOutputExampleList(0);
		if(ExampleUtils.isTempTable(exampleProto)){
			context.registerTable(exampleProto.getMeta().getName(), outputTable);
		}
	}
}
