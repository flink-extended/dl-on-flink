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
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;


public class StreamJob {

	public static void main(String[] args) throws Exception {
		ArgumentParser parser = ArgumentParsers.newFor("TransformJob").build();
		parser.addArgument("--execution-config").metavar("EXECUTION_CONFIG").dest("EXECUTION_CONFIG")
				.help("a execution configuration file define flink job.").required(true);

		Namespace res = null;
		try {
			res = parser.parseArgs(args);
			System.out.println(res);
		} catch (ArgumentParserException e) {
			parser.handleError(e);
			System.exit(1);
		}

		String executionConfig = res.getString("EXECUTION_CONFIG");

		String source = FileUtils.readFile(executionConfig);
		System.out.println(source);
		ExecutionProto.Builder executionBuilder = ExecutionProto.newBuilder();
		ProtoUtil.jsonToProto(source, executionBuilder);
		ComponentContext componentContext;
		TableEnvironment tableEnv;
		if(executionBuilder.getRunMode() == RunModeProto.BATCH){
			if(0 == executionBuilder.getTransformersBuilderList().size()){
				StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
				tableEnv = StreamTableEnvironment.create(env);
				componentContext = new ComponentContext(env, tableEnv, RunModeProto.BATCH);
				StreamJobParser streamParser = new StreamJobParser();
				streamParser.parseJob(executionBuilder, componentContext);
				env.execute("job");
			}else {
				ExecutionEnvironment env = ExecutionEnvironment.getExecutionEnvironment();
				tableEnv = BatchTableEnvironment.create(env);
				componentContext = new ComponentContext(env, tableEnv, RunModeProto.BATCH);
				StreamJobParser streamParser = new StreamJobParser();
				streamParser.parseJob(executionBuilder, componentContext);
				env.execute("job");
			}
		}else {
			StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
			tableEnv = StreamTableEnvironment.create(env);
			componentContext = new ComponentContext(env, tableEnv, RunModeProto.STREAM);
			StreamJobParser streamParser = new StreamJobParser();
			streamParser.parseJob(executionBuilder, componentContext);
			env.execute("job");
		}

	}
}
