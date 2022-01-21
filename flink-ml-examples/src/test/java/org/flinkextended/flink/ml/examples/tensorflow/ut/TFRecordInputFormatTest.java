/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.flinkextended.flink.ml.examples.tensorflow.ut;


import org.apache.flink.core.fs.FileSystem;
import org.apache.flink.core.fs.Path;
import org.apache.flink.runtime.fs.hdfs.HadoopFileSystem;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hdfs.MiniDFSCluster;
import org.flinkextended.flink.ml.examples.tensorflow.mnist.MnistDataUtil;
import org.flinkextended.flink.ml.tensorflow.io.TFRecordInputFormat;
import org.flinkextended.flink.ml.tensorflow.io.TFRecordInputSplit;
import org.flinkextended.flink.ml.tensorflow.io.TFRecordSource;
import org.flinkextended.flink.ml.tensorflow.io.TraceTFRecordOutputFormat;
import org.flinkextended.flink.ml.util.SysUtil;

import org.apache.flink.api.common.io.InputFormat;
import org.apache.flink.api.java.ExecutionEnvironment;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import org.junit.BeforeClass;
import org.junit.ClassRule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;

import java.io.File;


public class TFRecordInputFormatTest {

	@ClassRule public static final TemporaryFolder TEMP_FOLDER = new TemporaryFolder();


	@BeforeClass
	public static void setUp() throws Exception {
		MnistDataUtil.prepareData();
	}

	@Test
	public void testReadTFRecord() throws Exception {
		System.out.println("Run Test: " + SysUtil._FUNC_());
		ExecutionEnvironment flinkEnv = ExecutionEnvironment.getExecutionEnvironment();
		String rootPath = new File("").getAbsolutePath();
		String[] paths = new String[2];
		paths[0] = rootPath + "/target/data/test/0.tfrecords";
		paths[1] = rootPath + "/target/data/test/1.tfrecords";
		InputFormat<byte[], TFRecordInputSplit> inputFormat = new TFRecordInputFormat(paths, 1);
		flinkEnv.createInput(inputFormat).setParallelism(2).output(new TraceTFRecordOutputFormat());
		flinkEnv.execute();
	}

	@Test
	public void testReadTFRecordStream() throws Exception {
		System.out.println("Run Test: " + SysUtil._FUNC_());
		StreamExecutionEnvironment flinkEnv = StreamExecutionEnvironment.getExecutionEnvironment();
		String rootPath = new File("").getAbsolutePath();
		String[] paths = new String[2];
		paths[0] = rootPath + "/target/data/test/0.tfrecords";
		paths[1] = rootPath + "/target/data/test/1.tfrecords";
		TFRecordSource source = TFRecordSource.createSource(paths, 3);
		DataStream<byte[]> input = flinkEnv.addSource(source).setParallelism(2);
		input.writeUsingOutputFormat(new TraceTFRecordOutputFormat());
		flinkEnv.execute();
	}


	@Test
	public void testReadTFRecordStreamHadoopConfiguration() throws Exception {
		System.out.println("Run Test: " + SysUtil._FUNC_());

		//create temp hdfs
		final File baseDir = TEMP_FOLDER.newFolder();
		final Configuration hdConf = new Configuration();
		hdConf.set(MiniDFSCluster.HDFS_MINIDFS_BASEDIR, baseDir.getAbsolutePath());
		final MiniDFSCluster.Builder builder = new MiniDFSCluster.Builder(hdConf);
		MiniDFSCluster hdfsCluster = builder.build();
		final org.apache.hadoop.fs.FileSystem hdfs = hdfsCluster.getFileSystem();

		//copy the tfrecord file to hdfs
		Path basePath = new Path(hdfs.getUri() + "/tests");
		String rootPath = new File("").getAbsolutePath();
		String[] paths = new String[2];
		paths[0] = rootPath + "/target/data/test/0.tfrecords";
		paths[1] = rootPath + "/target/data/test/1.tfrecords";
		hdfs.copyFromLocalFile(new org.apache.hadoop.fs.Path(rootPath + "/target/data/test/0.tfrecords"), new org.apache.hadoop.fs.Path(hdfs.getUri() + "/tests/0.tfrecords"));;
		hdfs.copyFromLocalFile(new org.apache.hadoop.fs.Path(rootPath + "/target/data/test/1.tfrecords"), new org.apache.hadoop.fs.Path(hdfs.getUri() + "/tests/1.tfrecords"));

		//submit flink job local
		StreamExecutionEnvironment flinkEnv = StreamExecutionEnvironment.getExecutionEnvironment();
		TFRecordSource source = TFRecordSource.createSource(new String[]{hdfs.getUri() + "/tests/0.tfrecords", hdfs.getUri() + "/tests/1.tfrecords"}, 3, hdfsCluster.getConfiguration(0));
		DataStream<byte[]> input = flinkEnv.addSource(source).setParallelism(2);
		input.writeUsingOutputFormat(new TraceTFRecordOutputFormat());
		flinkEnv.execute();

		//destroy mini dfs cluster
		if (hdfsCluster != null) {
			hdfsCluster
					.getFileSystem()
					.delete(new org.apache.hadoop.fs.Path(basePath.toUri()), true);
			hdfsCluster.shutdown();
		}
	}
}