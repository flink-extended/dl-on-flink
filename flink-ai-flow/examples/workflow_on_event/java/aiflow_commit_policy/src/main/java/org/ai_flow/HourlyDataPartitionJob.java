package org.ai_flow;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HourlyDataPartitionJob {
	private static final Logger LOG = LoggerFactory.getLogger(HourlyDataPartitionJob.class);


	public static void main(String[] args) throws Exception {
		if (args.length != 3) {
			throw new IllegalArgumentException("missing arguments: [brokers] [input_topic] [output_file_path]");
		}

		String brokers = args[0];
		String input_topic = args[1];
		String output_file_path = args[2];
		LOG.info("brokers: {}, input topic: {},  file_path: {}", brokers, input_topic, output_file_path);

		StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		env.setParallelism(1);
		long checkpointInterval = env.getCheckpointInterval();
		if (checkpointInterval == -1) {
			LOG.info("Enabling checkpoint with interval 10 sec");
			checkpointInterval = 10 * 1000;
			env.enableCheckpointing(checkpointInterval);
		}
		LOG.info("Effective checkpoint interval: {}", checkpointInterval);
		StreamTableEnvironment tEnv = StreamTableEnvironment.create(env);

		tEnv.executeSql(String.format("create table hourly_data_source (\n" +
				"                sample varchar,\n" +
				"                ts TIMESTAMP(3),\n" +
				"				 WATERMARK FOR ts AS ts - INTERVAL '60' SECOND\n" +
				"            ) with (\n" +
				"                'connector' = 'kafka',\n" +
				"                'topic' = '%s',\n" +
				"                'properties.bootstrap.servers' = '%s',\n" +
				"                'properties.group.id' = 'hourly_data_partition',\n" +
				"                'format' = 'csv',\n" +
				"                'scan.startup.mode' = 'latest-offset'\n" +
				"            )", input_topic, brokers));

		tEnv.executeSql(String.format("create table hourly_data_sink (\n" +
				"                sample varchar,\n" +
				"				 dt STRING,\n" +
				"				 hr STRING\n" +
				"            ) PARTITIONED BY (dt, hr) with (\n" +
				"                'connector' = 'filesystem',\n" +
				"                'path' = '%s',\n" +
				"                'format' = 'csv',\n" +
				"				 'partition.time-extractor.timestamp-pattern'='$dt $hr:00:00',\n" +
				"				 'sink.rolling-policy.rollover-interval'='%d MS',\n" +
				"				 'sink.rolling-policy.check-interval'='%d MS',\n" +
				"				 'sink.partition-commit.trigger'='partition-time',\n" +
				"				 'sink.partition-commit.delay'='1 h',\n" +
				"				 'sink.partition-commit.policy.kind'='success-file,custom',\n" +
				"				 'sink.partition-commit.policy.class'='org.ai_flow.flink.AIFlowEventCommitPolicy'\n" +
				"            )", output_file_path, checkpointInterval, checkpointInterval / 100));


		final Table table =
				tEnv.sqlQuery("SELECT sample, DATE_FORMAT(ts, 'yyyy-MM-dd'), DATE_FORMAT(ts, 'HH') " +
						"FROM hourly_data_source");

		tEnv.createStatementSet()
				.addInsert("hourly_data_sink", table)
				.execute().getJobClient().get()
				.getJobExecutionResult(Thread.currentThread().getContextClassLoader()).get();
	}
}
