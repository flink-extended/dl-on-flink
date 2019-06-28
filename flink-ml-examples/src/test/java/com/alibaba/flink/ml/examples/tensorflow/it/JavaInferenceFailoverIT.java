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

package com.alibaba.flink.ml.examples.tensorflow.it;

import com.alibaba.flink.ml.examples.tensorflow.mnist.MnistDataUtil;
import com.alibaba.flink.ml.examples.tensorflow.mnist.MnistJavaInference;
import com.alibaba.flink.ml.examples.tensorflow.ut.TFMnistInferenceTest;
import com.alibaba.flink.ml.util.MiniCluster;
import com.google.common.io.Files;
import org.apache.hadoop.fs.Path;
import org.junit.*;

import java.io.File;
import java.util.concurrent.FutureTask;


public class JavaInferenceFailoverIT {

	private static final int NUM_TM = 3;
	private static final String HDFS_EXPORT_DIR = "/mnist/models/" + new Path(TFMnistInferenceTest.exportPath)
			.getName();
	private static final String HDFS_TEST_DATA_DIR = "/mnist/test";

	private MiniCluster miniCluster;

	@BeforeClass
	public static void prepData() throws Exception {
		MnistDataUtil.prepareData();
		TFMnistInferenceTest.generateModelIfNeeded();
	}

	@Before
	public void setUp() throws Exception {
		miniCluster = MiniCluster.start(NUM_TM);
		miniCluster.setExecJar("/flink-ml-examples/target/flink-ml-examples-1.0-SNAPSHOT.jar");
		miniCluster.copyFromHostToHDFS(TFMnistInferenceTest.exportPath, HDFS_EXPORT_DIR);
		miniCluster.copyFromHostToHDFS(TFMnistInferenceTest.testDataPath, HDFS_TEST_DATA_DIR);
	}

	@After
	public void tearDown() throws Exception {
		if (miniCluster != null) {
			miniCluster.stop();
		}
	}

	@Test
	public void testKillOneTM() throws Exception {
		FutureTask<Void> jobFuture = new FutureTask<>(this::runAndVerify, null);
		Thread thread = new Thread(jobFuture);
		thread.setDaemon(true);
		thread.setName(getClass().getSimpleName() + "-JobRunner");
		thread.start();

		long sleepTime = 30000;
		Thread.sleep(sleepTime);
		miniCluster.killOneTMWithWorkload();
		jobFuture.get();
	}

	private void runAndVerify() {
		String output = miniCluster.flinkRun(MnistJavaInference.class.getCanonicalName(),
				"--model-path",
				makeHDFSURI(HDFS_EXPORT_DIR),
				"--test-data",
				makeHDFSURI(HDFS_TEST_DATA_DIR),
				"--hadoop-fs",
				miniCluster.getHDFS(),
				"--num-records",
				"10000",
				"--batch-size",
				"200");
		System.out.println(output);
		if (!output.contains("Program execution finished")) {
			File tmp = Files.createTempDir();
			miniCluster.dumpFlinkLogs(tmp);
			Assert.fail("Job failed, check logs in " + tmp.getAbsolutePath());
		}
	}

	private String makeHDFSURI(String path) {
		return miniCluster.getHDFS() + path;
	}
}
