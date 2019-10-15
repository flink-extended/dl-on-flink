package com.alibaba.flink.ml.workflow.components.transformers;

import org.apache.flink.ml.api.core.Transformer;
import org.apache.flink.ml.api.misc.param.Params;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;

import com.alibaba.flink.ml.workflow.TransformerProto;
import com.alibaba.flink.ml.workflow.components.ComponentContext;
import com.alibaba.flink.ml.workflow.components.ContextHandler;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public abstract class BaseTransformer implements Transformer<BaseTransformer>{
	protected Params params = new Params();
	protected TransformerProto.Builder transformerProto;

	public BaseTransformer(TransformerProto.Builder transformerProto) {
		this.transformerProto = transformerProto;
	}

	@Override
	public Params getParams() {
		return params;
	}

	private boolean inTableEnv(String name, TableEnvironment tableEnv){
		String[] tables = tableEnv.listTables();
		Set<String> tableSet = new HashSet<>(Arrays.asList(tables));
		return tableSet.contains(name);
	}
}
