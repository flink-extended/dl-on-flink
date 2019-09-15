package com.alibaba.flink.ml.workflow.components.examples;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.sinks.CsvTableSink;
import org.apache.flink.table.sources.CsvTableSource;

import com.alibaba.flink.ml.workflow.ExampleProto;
import com.alibaba.flink.ml.workflow.ExampleRunMode;
import com.alibaba.flink.ml.workflow.components.Component;
import com.alibaba.flink.ml.workflow.components.ComponentContext;
import com.google.protobuf.Message;

public class ExampleComponent implements Component {
	@Override
	public void translate(Message message, ComponentContext context) throws Exception {
		TableEnvironment tableEnv = context.getTableEnv();
		ExampleProto exampleProto = (ExampleProto) message;
		if(ExampleRunMode.SOURCE == exampleProto.getRunMod()) {
			CsvTableSource csvTable = CsvTableSource
					.builder()
					.path(exampleProto.getBatchUri())
					.ignoreFirstLine()
					.fieldDelimiter(",")
					.field("a", Types.STRING)
					.field("b", Types.STRING)
					.field("c", Types.STRING)
					.field("d", Types.STRING)
					.build();

			tableEnv.registerTableSource(exampleProto.getMeta().getName(), csvTable);
			System.out.println("source:" + exampleProto.getMeta().getName());
		}else {
			CsvTableSink csvTableSink = new CsvTableSink(exampleProto.getBatchUri());
			int count = exampleProto.getSchema().getNameListCount();
			String[] names = new String[count];
			TypeInformation[] types = new TypeInformation[count];
			for(int i = 0; i < count; i++){
				names[i] = exampleProto.getSchema().getNameList(i);
				types[i] = Types.STRING;
			}
			csvTableSink = (CsvTableSink)csvTableSink.configure(names, types);
			tableEnv.registerTableSink(exampleProto.getMeta().getName(), csvTableSink);
			System.out.println("sink:" + exampleProto.getMeta().getName());

		}
	}
}
