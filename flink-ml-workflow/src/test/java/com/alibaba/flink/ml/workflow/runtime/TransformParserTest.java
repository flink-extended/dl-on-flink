package com.alibaba.flink.ml.workflow.runtime;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.java.StreamTableEnvironment;

import com.alibaba.flink.ml.workflow.ExecutionProto;
import com.alibaba.flink.ml.workflow.common.FileUtils;
import com.alibaba.flink.ml.workflow.common.ProtoUtil;
import com.alibaba.flink.ml.workflow.components.ComponentContext;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.io.File;

import static org.junit.Assert.*;

public class TransformParserTest {

	@Before
	public void setUp() throws Exception {
	}

	@After
	public void tearDown() throws Exception {
	}


	@Test
	public void parseTransformerJob() throws Exception {
		String currentPath = TransformParserTest.class.getClassLoader().getResource("").getPath();
		String inputFile = currentPath + "test.csv";
		String outputDir = currentPath + "../output";
		File output = new File(outputDir);
		FileUtils.deleteDir(output);
		String source = FileUtils.readResourceFile("execution.json");
		ExecutionProto.Builder executionBuilder = ExecutionProto.newBuilder();
		ProtoUtil.jsonToProto(source, executionBuilder);
		executionBuilder.getTransformersBuilder(0).getInputExampleListBuilder(0).setBatchUri(inputFile);
		executionBuilder.getTransformersBuilder(1).getOutputExampleListBuilder(0).setBatchUri(outputDir);

		System.out.println(executionBuilder);
		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		env.setParallelism(1);
		TableEnvironment tableEnv = StreamTableEnvironment.create(env);
		ComponentContext componentContext = new ComponentContext(env, tableEnv);
		TransformParser parser = new TransformParser();
		parser.parseJob(executionBuilder, componentContext);
		tableEnv.execute("job");

	}

	@Test
	public void parseTrainingJob() throws Exception {
		String currentPath = TransformParserTest.class.getClassLoader().getResource("").getPath();
		String inputFile = currentPath + "test.csv";
		String outputDir = currentPath + "../output";
		File output = new File(outputDir);
		FileUtils.deleteDir(output);
		String source = FileUtils.readResourceFile("trainer.json");
		ExecutionProto.Builder executionBuilder = ExecutionProto.newBuilder();
		ProtoUtil.jsonToProto(source, executionBuilder);
		executionBuilder.getTransformersBuilder(0).getInputExampleListBuilder(0).setBatchUri(inputFile);
		executionBuilder.getTrainersBuilderList().get(0).setPyMainScript(currentPath+"/../../src/test/python/train_stream.py");

		System.out.println(executionBuilder);
		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		env.setParallelism(1);
		TableEnvironment tableEnv = StreamTableEnvironment.create(env);
		ComponentContext componentContext = new ComponentContext(env, tableEnv);
		TransformParser parser = new TransformParser();
		parser.parseJob(executionBuilder, componentContext);
		tableEnv.execute("job");

	}
}