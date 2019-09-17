package com.alibaba.flink.ml.workflow.components.examples;

import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.sinks.TableSink;
import org.apache.flink.table.sources.TableSource;

import com.alibaba.flink.ml.workflow.ExampleProto;
import com.alibaba.flink.ml.workflow.ExampleRunMode;
import com.alibaba.flink.ml.workflow.components.Component;
import com.alibaba.flink.ml.workflow.components.ComponentContext;
import com.alibaba.flink.ml.workflow.components.examples.csv.CSVExampleCreator;
import com.google.protobuf.Message;

public class ExampleComponent implements Component {

	public static ExampleCreator getExampleCreator(String exampleFormat){
		if(exampleFormat.equalsIgnoreCase("CSV")){
			return new CSVExampleCreator();
		}else {
			throw new RuntimeException("not support:" + exampleFormat);
		}
	}

	@Override
	public void translate(Message message, ComponentContext context) throws Exception {
		TableEnvironment tableEnv = context.getTableEnv();
		ExampleProto exampleProto = (ExampleProto) message;
		if(ExampleUtils.isTempTable(exampleProto)){
			return;
		}
		ExampleCreator creator = getExampleCreator(exampleProto.getExampleFormat());
		if(ExampleRunMode.SOURCE == exampleProto.getRunMod()) {
			TableSource tableSource = creator.createSource(exampleProto);
			tableEnv.registerTableSource(exampleProto.getMeta().getName(), tableSource);
		}else {
			TableSink tableSink = creator.createSink(exampleProto);
			tableEnv.registerTableSink(exampleProto.getMeta().getName(), tableSink);
		}
	}
}
