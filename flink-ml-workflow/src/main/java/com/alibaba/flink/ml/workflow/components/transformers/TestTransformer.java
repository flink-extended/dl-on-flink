package com.alibaba.flink.ml.workflow.components.transformers;

import org.apache.flink.ml.api.core.Transformer;
import org.apache.flink.ml.api.misc.param.Params;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;

public class TestTransformer implements Transformer<TestTransformer> {
	@Override
	public Table transform(TableEnvironment tableEnvironment, Table table) {
		return table.select("a, b");
	}

	@Override
	public Params getParams() {
		return null;
	}
}
