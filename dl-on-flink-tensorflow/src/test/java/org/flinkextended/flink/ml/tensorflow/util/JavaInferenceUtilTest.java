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

package org.flinkextended.flink.ml.tensorflow.util;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.util.DummyContext;
import io.grpc.Server;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.junit.Before;
import org.junit.Test;

import java.io.IOException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.FutureTask;

import static org.junit.Assert.assertFalse;

public class JavaInferenceUtilTest {

	private MLContext mlContext;

	@Before
	public void setUp() throws Exception {
		mlContext = DummyContext.createDummyMLContext();
	}

	@Test
	public void testStartTFContextService() throws Exception {
		final Server server = JavaInferenceUtil.startTFContextService(mlContext);
		assertFalse(server.isShutdown());
		assertFalse(server.isTerminated());
	}

	@Test
	public void testStartInferenceProcessWatcher() throws IOException, ExecutionException, InterruptedException {
		final Process process = new ProcessBuilder("echo", "hello").start();
		final FutureTask<Void> future = JavaInferenceUtil.startInferenceProcessWatcher(process, mlContext);
		future.get();
		assertFalse(process.isAlive());
	}

	@Test
	public void testLaunchInferenceProcess() throws IOException, InterruptedException {
		final Process process =
				JavaInferenceUtil.launchInferenceProcess(mlContext, new RowTypeInfo(Types.STRING), new RowTypeInfo(Types.STRING));
		final FutureTask<Void> future = JavaInferenceUtil.startInferenceProcessWatcher(process, mlContext);
		try {
			future.get();
		} catch (ExecutionException e) {
			// expected
		}
		assertFalse(process.isAlive());
	}
}