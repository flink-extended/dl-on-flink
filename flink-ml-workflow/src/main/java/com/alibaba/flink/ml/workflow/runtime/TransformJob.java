package com.alibaba.flink.ml.workflow.runtime;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.api.java.StreamTableEnvironment;
import com.alibaba.flink.ml.workflow.ExecutionProto;
import com.alibaba.flink.ml.workflow.common.FileUtils;
import com.alibaba.flink.ml.workflow.common.ProtoUtil;
import com.alibaba.flink.ml.workflow.components.ComponentContext;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;


public class TransformJob {

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
		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		TableEnvironment tableEnv = StreamTableEnvironment.create(env);
		ComponentContext componentContext = new ComponentContext(env, tableEnv);
		TransformParser transformParser = new TransformParser();
		transformParser.parseJob(executionBuilder, componentContext);
		tableEnv.execute("job");

	}
}
