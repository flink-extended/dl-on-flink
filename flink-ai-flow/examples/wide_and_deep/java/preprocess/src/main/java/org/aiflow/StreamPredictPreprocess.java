package org.aiflow;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.ExecutionException;

import static org.apache.flink.table.api.Expressions.$;

public class StreamPredictPreprocess {
	private static final Logger LOG = LoggerFactory.getLogger(StreamPredictPreprocess.class);

	public static void main(String[] args) throws ExecutionException, InterruptedException {
		if (args.length != 3) {
			throw new IllegalArgumentException("missing arguments: [brokers] [input_topic] [output_topic]");
		}

		String brokers = args[0];
		String input_topic = args[1];
		String output_topic = args[2];
		LOG.info("brokers: {}, input topic: {}, output topic: {}", brokers, input_topic, output_topic);

		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		StreamTableEnvironment tEnv = StreamTableEnvironment.create(env);

		tEnv.executeSql(String.format("create table stream_predict_preprocess_source (\n" +
				"                age varchar,\n" +
				"                workclass varchar,\n" +
				"                fnlwgt varchar,\n" +
				"                education varchar,\n" +
				"                education_num varchar,\n" +
				"                marital_status varchar,\n" +
				"                occupation varchar,\n" +
				"                relationship varchar,\n" +
				"                race varchar,\n" +
				"                gender varchar,\n" +
				"                capital_gain varchar,\n" +
				"                capital_loss varchar,\n" +
				"                hours_per_week varchar,\n" +
				"                native_country varchar,\n" +
				"                income_bracket varchar\n" +
				"            ) with (\n" +
				"                'connector' = 'kafka',\n" +
				"                'topic' = '%s',\n" +
				"                'properties.bootstrap.servers' = '%s',\n" +
				"                'properties.group.id' = 'stream_predict_preprocess_source',\n" +
				"                'format' = 'csv',\n" +
				"                'scan.startup.mode' = 'earliest-offset'\n" +
				"            )", input_topic, brokers));

		tEnv.executeSql(String.format("create table stream_predict_preprocess_sink (\n" +
				"                age varchar,\n" +
				"                workclass varchar,\n" +
				"                fnlwgt varchar,\n" +
				"                education varchar,\n" +
				"                education_num varchar,\n" +
				"                marital_status varchar,\n" +
				"                occupation varchar,\n" +
				"                relationship varchar,\n" +
				"                race varchar,\n" +
				"                gender varchar,\n" +
				"                capital_gain varchar,\n" +
				"                capital_loss varchar,\n" +
				"                hours_per_week varchar,\n" +
				"                native_country varchar\n" +
				"            ) with (\n" +
				"                'connector' = 'kafka',\n" +
				"                'topic' = '%s',\n" +
				"                'properties.bootstrap.servers' = '%s',\n" +
				"                'properties.group.id' = 'stream_predict_preprocess_sink',\n" +
				"                'format' = 'csv',\n" +
				"                'scan.startup.mode' = 'earliest-offset'\n" +
				"            )", output_topic, brokers));
		final Table sourceTable = tEnv.from("stream_predict_preprocess_source");
		tEnv.createStatementSet()
				.addInsert("stream_predict_preprocess_sink", sourceTable.dropColumns($("income_bracket")))
				.execute().getJobClient().get()
				.getJobExecutionResult(Thread.currentThread().getContextClassLoader()).get();
	}

}
