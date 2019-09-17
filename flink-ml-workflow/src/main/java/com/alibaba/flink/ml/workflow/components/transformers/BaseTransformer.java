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

public abstract class BaseTransformer implements Transformer<BaseTransformer>, ContextHandler, TransformerHandler{
	protected Params params = new Params();
	protected ComponentContext context;
	protected TransformerProto transformerProto;

	@Override
	public Params getParams() {
		return params;
	}

	@Override
	public void setContext(ComponentContext context) {
		this.context = context;
	}

	@Override
	public ComponentContext getContext() {
		return context;
	}

	@Override
	public void setTransformerProto(TransformerProto transformerProto) {
		this.transformerProto = transformerProto;
	}

	private boolean inTableEnv(String name, TableEnvironment tableEnv){
		String[] tables = tableEnv.listTables();
		Set<String> tableSet = new HashSet<>(Arrays.asList(tables));
		return tableSet.contains(name);
	}
	public Table getInputTable(int index){
		TableEnvironment tableEnv = context.getTableEnv();
		String tableName = transformerProto.getInputExampleList(index).getMeta().getName();
		Table input = context.getTable(tableName);
		if(null == input){
			if(inTableEnv(tableName, tableEnv)){
				return tableEnv.scan(tableName);
			}else {
				return null;
			}
		}else {
			return input;
		}
	}

	public void registerOutputTable(String name, Table table){
		context.registerTable(name, table);
	}
}
