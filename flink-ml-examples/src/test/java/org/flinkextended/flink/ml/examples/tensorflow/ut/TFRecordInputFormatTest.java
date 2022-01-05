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
import org.junit.Test;

import java.io.File;


public class TFRecordInputFormatTest {
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

}