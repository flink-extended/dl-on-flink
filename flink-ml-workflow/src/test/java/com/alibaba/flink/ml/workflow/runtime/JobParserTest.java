package com.alibaba.flink.ml.workflow.runtime;

import org.apache.flink.api.java.ExecutionEnvironment;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.java.BatchTableEnvironment;
import org.apache.flink.table.api.java.StreamTableEnvironment;

import com.alibaba.flink.ml.workflow.ExecutionProto;
import com.alibaba.flink.ml.workflow.RunModeProto;
import com.alibaba.flink.ml.workflow.common.FileUtils;
import com.alibaba.flink.ml.workflow.common.ProtoUtil;
import com.alibaba.flink.ml.workflow.components.ComponentContext;
import org.apache.curator.test.TestingServer;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.io.File;

public class JobParserTest {
	private static TestingServer server;

	@Before
	public void setUp() throws Exception {
		server = new TestingServer(2181, true);
	}

	@After
	public void tearDown() throws Exception {
		server.stop();
	}


	@Test
	public void parseTransformerJob() throws Exception {
		String currentPath = JobParserTest.class.getClassLoader().getResource("").getPath();
		String inputFile = currentPath + "test.csv";
		String outputDir = currentPath + "../output";
		File output = new File(outputDir);
		FileUtils.deleteDir(output);
		String source = FileUtils.readResourceFile("execution.json");
		ExecutionProto.Builder executionBuilder = ExecutionProto.newBuilder();
		ProtoUtil.jsonToProto(source, executionBuilder);
		executionBuilder.getTransformersBuilder(0).getInputExampleListBuilder(0).setStreamUri(inputFile);
		executionBuilder.getTransformersBuilder(1).getOutputExampleListBuilder(0).setStreamUri(outputDir);

		System.out.println(executionBuilder);
		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		env.setParallelism(1);
		TableEnvironment tableEnv = StreamTableEnvironment.create(env);
		ComponentContext componentContext = new ComponentContext(env, tableEnv, RunModeProto.STREAM);
		StreamJobParser parser = new StreamJobParser();
		parser.parseJob(executionBuilder, componentContext);
		env.execute("job");

	}

	@Test
	public void parseTransformerBatchJob() throws Exception {
		String currentPath = JobParserTest.class.getClassLoader().getResource("").getPath();
		String inputFile = currentPath + "test.csv";
		String outputDir = currentPath + "../output_batch";
		File output = new File(outputDir);
		FileUtils.deleteDir(output);
		String source = FileUtils.readResourceFile("execution.json");
		ExecutionProto.Builder executionBuilder = ExecutionProto.newBuilder();
		ProtoUtil.jsonToProto(source, executionBuilder);
		executionBuilder.getTransformersBuilder(0).getInputExampleListBuilder(0).setBatchUri(inputFile);
		executionBuilder.getTransformersBuilder(1).getOutputExampleListBuilder(0).setBatchUri(outputDir);

		System.out.println(executionBuilder);
		ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();
		env.setParallelism(1);
		TableEnvironment tableEnv = BatchTableEnvironment.create(env);
		ComponentContext componentContext = new ComponentContext(env, tableEnv, RunModeProto.BATCH);
		StreamJobParser parser = new StreamJobParser();
		parser.parseJob(executionBuilder, componentContext);
		env.execute("job");

	}

	@Test
	public void parseTrainingJob() throws Exception {

		String currentPath = JobParserTest.class.getClassLoader().getResource("").getPath();
		String inputFile = currentPath + "test.csv";
		String outputDir = currentPath + "../output";
		File output = new File(outputDir);
		FileUtils.deleteDir(output);
		String source = FileUtils.readResourceFile("trainer.json");
		ExecutionProto.Builder executionBuilder = ExecutionProto.newBuilder();
		ProtoUtil.jsonToProto(source, executionBuilder);
		executionBuilder.getTransformersBuilder(0).getInputExampleListBuilder(0).setStreamUri(inputFile);
		executionBuilder.getTrainersBuilderList().get(0).setPyMainScript(currentPath+"/../../src/test/python/train_stream.py");

		System.out.println(executionBuilder);
		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		env.setParallelism(1);
		TableEnvironment tableEnv = StreamTableEnvironment.create(env);
		ComponentContext componentContext = new ComponentContext(env, tableEnv, RunModeProto.STREAM);
		StreamJobParser parser = new StreamJobParser();
		parser.parseJob(executionBuilder, componentContext);
		env.execute("job");

	}
}