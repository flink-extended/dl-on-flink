package com.alibaba.flink.ml.workflow.components.transformers;

import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.TableSchema;

import com.alibaba.flink.ml.workflow.ExampleProto;
import com.alibaba.flink.ml.workflow.SchemaProto;
import com.alibaba.flink.ml.workflow.TransformerProto;
import com.alibaba.flink.ml.workflow.common.DataTypeUtils;
import com.alibaba.flink.ml.workflow.common.ReflectUtil;
import com.alibaba.flink.ml.workflow.components.Component;
import com.alibaba.flink.ml.workflow.components.ComponentContext;
import com.alibaba.flink.ml.workflow.components.examples.ExampleUtils;
import com.google.protobuf.MessageOrBuilder;

public class TransformerComponent implements Component {

	@Override
	public void translate(MessageOrBuilder message, ComponentContext context) throws Exception {
		TransformerProto.Builder transformerProto = (TransformerProto.Builder)message;
		TableEnvironment tableEnv = context.getTableEnv();
		String className = transformerProto.getTransformerClassName();
		Class[] classes = new Class[1];
		Object[] objects = new Object[1];
		classes[0] = TransformerProto.Builder.class;
		objects[0] = transformerProto;
		BaseTransformer transformer = ReflectUtil.createInstance(className, classes, objects);
		Table outputTable = transformer.transform(tableEnv, null);
		TableSchema tableSchema = outputTable.getSchema();
		ExampleProto.Builder exampleProto = transformerProto.getOutputExampleListBuilder(0);
		SchemaProto.Builder schemaBuilder = SchemaProto.newBuilder();
		DataTypeUtils.tableSchemaToSchemaProto(tableSchema, schemaBuilder);
		exampleProto.setSchema(schemaBuilder);
		if(ExampleUtils.isTempTable(exampleProto)){
			tableEnv.registerTable(exampleProto.getMeta().getName(), outputTable);
			context.registerTable(exampleProto.getMeta().getName(), outputTable);
		}else {
			context.registerSinkTable(exampleProto.getMeta().getName(), outputTable);
		}
		context.registerSchema(exampleProto.getMeta().getName(), schemaBuilder);
	}
}
