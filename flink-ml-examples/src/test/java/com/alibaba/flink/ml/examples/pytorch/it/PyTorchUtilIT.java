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

package com.alibaba.flink.ml.examples.pytorch.it;

import com.alibaba.flink.ml.examples.pytorch.PyTorchRunDist;
import com.alibaba.flink.ml.util.MiniCluster;
import com.google.common.io.Files;
import org.junit.*;
import com.alibaba.flink.ml.examples.util.CodeUtil;

import java.io.File;
import java.io.IOException;

public class PyTorchUtilIT {
	private static MiniCluster miniCluster;
	private static final int numTMs = 3;

	@Before
	public void setUp() throws Exception {
		miniCluster = MiniCluster.start(numTMs);
		miniCluster.setExecJar("/flink-ml-examples/target/flink-ml-examples-1.0-SNAPSHOT.jar");
	}

	@After
	public void tearDown() throws Exception {
		if (miniCluster != null) {
			miniCluster.stop();
		}
	}

	@Test
	public void trainStream() throws Exception {
		runAndVerify(miniCluster, PyTorchRunDist.EnvMode.Stream, "greeter.py");
	}

	@Test
	public void trainTable() throws Exception {
		runAndVerify(miniCluster, PyTorchRunDist.EnvMode.Table, "greeter.py");
	}

	@Test
	public void allReduceStream() throws Exception {
		runAndVerify(miniCluster, PyTorchRunDist.EnvMode.Stream, "all_reduce_test.py");
	}

	@Test
	public void allReduceTable() throws Exception {
		runAndVerify(miniCluster, PyTorchRunDist.EnvMode.Table, "all_reduce_test.py");
	}

	private static String run(MiniCluster miniCluster, PyTorchRunDist.EnvMode mode, String script) throws IOException {
		String codeRemotePath = null;
		try {
			codeRemotePath = CodeUtil.copyCodeToHdfs(miniCluster);
		} catch (IOException e) {
			e.printStackTrace();
			throw e;
		}
		String output = miniCluster.flinkRun(PyTorchRunDist.class.getCanonicalName(),
				"--zk-conn-str",
				miniCluster.getZKContainer(),
				"--mode",
				mode.toString(),
				"--script",
				script,
				"--envpath",
				miniCluster.getVenvHdfsPath(),
				"--code-path",
				codeRemotePath
		);
		return output;
	}

	static boolean runAndVerify(MiniCluster miniCluster, PyTorchRunDist.EnvMode mode, String script)
			throws IOException {
		String output = run(miniCluster, mode, script);
		System.out.println(output);
		if (!output.contains("Program execution finished")) {
			File tmp = Files.createTempDir();
			miniCluster.dumpFlinkLogs(tmp);
			Assert.fail("run failed in mode " + mode + ", check logs in " + tmp.getAbsolutePath());
			return false;
		} else {
			File tmp = Files.createTempDir();
			miniCluster.dumpFlinkLogs(tmp);
			System.out.println("logs in " + tmp.getAbsolutePath());
		}
		return true;
	}
}