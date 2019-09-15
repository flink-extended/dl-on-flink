package com.alibaba.flink.ml.workflow.runtime;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.java.StreamTableEnvironment;
import org.apache.flink.table.sinks.CsvTableSink;
import org.apache.flink.table.sources.CsvTableSource;

import com.alibaba.flink.ml.workflow.ExampleProto;
import com.alibaba.flink.ml.workflow.ExampleProtoOrBuilder;
import com.alibaba.flink.ml.workflow.ExampleRunMode;
import com.alibaba.flink.ml.workflow.TransformerProto;
import com.alibaba.flink.ml.workflow.TransformerProtoOrBuilder;
import com.alibaba.flink.ml.workflow.common.ProtoUtil;
import com.alibaba.flink.ml.workflow.components.ComponentContext;
import com.alibaba.flink.ml.workflow.components.examples.ExampleComponent;
import com.alibaba.flink.ml.workflow.components.transformers.TransformerComponent;

import java.io.File;
import java.io.FileInputStream;

public class TransformJob {


	public static void main(String[] args) throws Exception {
		String fileName = TransformJob.class.getClassLoader().getResource("transform.json").getPath();
		System.out.println(fileName);
		File f = new File(fileName);
		FileInputStream in = new FileInputStream(f);
		int size = in.available();
		byte[] buffer = new byte[size];
		in.read(buffer);
		in.close();
		String source = new String(buffer, "utf-8");
		System.out.println(source);
		TransformerProto.Builder transformerProtoBuilder = TransformerProto.newBuilder();
		ProtoUtil.jsonToProto(source, transformerProtoBuilder);
		System.out.println(transformerProtoBuilder);

		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

		TableEnvironment tableEnv = StreamTableEnvironment.create(env);
		ComponentContext componentContext = new ComponentContext(env, tableEnv);
		for(ExampleProto.Builder builder: transformerProtoBuilder.getInputExampleListBuilderList()){
			builder.setRunMod(ExampleRunMode.SOURCE);
			ExampleComponent exampleComponent = new ExampleComponent();
			exampleComponent.translate(builder.build(), componentContext);
		}
		ComponentContext componentContext2 = new ComponentContext(env, tableEnv);
		for(ExampleProto.Builder builder: transformerProtoBuilder.getOutputExampleListBuilderList()){
			builder.setRunMod(ExampleRunMode.SINK);
			ExampleComponent exampleComponent = new ExampleComponent();
			exampleComponent.translate(builder.build(), componentContext2);
		}

		TransformerComponent transformerComponent = new TransformerComponent();
		transformerComponent.translate(transformerProtoBuilder.build(), componentContext);
		tableEnv.execute("job");
//
//		CsvTableSource csvtable = CsvTableSource
//				.builder()
//				.path("/Users/chenwuchao/code/ali/flink_ai_platform/python/flink_ai_platform/data/test/test.csv")
//				.ignoreFirstLine()
//				.fieldDelimiter(",")
//				.field("a", Types.STRING)
//				.field("b", Types.STRING)
//				.field("c", Types.STRING)
//				.field("d", Types.STRING)
//				.build();
//
//		tableEnv.registerTableSource("test", csvtable);
//
//		CsvTableSink csvTableSink = new CsvTableSink("./res.csv");
//		String[] names = {"a", "b"};
//		TypeInformation[] types = {Types.STRING, Types.STRING};
//		csvTableSink = (CsvTableSink)csvTableSink.configure(names, types);
//		tableEnv.registerTableSink("res", csvTableSink);
//
//		Table tableTest = tableEnv.scan("test").select("a, b");
//
//		tableTest.insertInto("res");
//		tableEnv.execute("aa");

	}
}
