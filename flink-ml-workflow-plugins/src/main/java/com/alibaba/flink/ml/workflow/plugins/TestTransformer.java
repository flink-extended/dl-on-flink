package com.alibaba.flink.ml.workflow.plugins;

import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;

import com.alibaba.flink.ml.workflow.SchemaProto;
import com.alibaba.flink.ml.workflow.TransformerProto;
import com.alibaba.flink.ml.workflow.components.examples.ExampleUtils;
import com.alibaba.flink.ml.workflow.components.transformers.BaseTransformer;

public class TestTransformer extends BaseTransformer {
	public TestTransformer(TransformerProto.Builder transformerProto) {
		super(transformerProto);
	}

	@Override
	public Table transform(TableEnvironment tableEnvironment, Table table) {
		Table inputTable = tableEnvironment.scan(transformerProto.getInputExampleList(0).getMeta().getName());
		Table  outputTable = inputTable.select("a, b");
		return outputTable;
	}
}
