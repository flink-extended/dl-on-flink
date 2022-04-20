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

package org.flinkextended.flink.ml.tensorflow.cluster.node.runner;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.cluster.node.runner.python.ProcessPythonRunner;
import org.flinkextended.flink.ml.tensorflow.util.TFConstants;
import org.flinkextended.flink.ml.util.IpHostUtil;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.annotation.VisibleForTesting;

import com.google.common.base.Joiner;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/** a subclass of ScriptRunner, this runner start a tensorboard service. */
public class TensorBoardPythonRunner extends ProcessPythonRunner {
    private static final Logger LOG = LoggerFactory.getLogger(TensorBoardPythonRunner.class);

    public TensorBoardPythonRunner(MLContext mlContext) {
        super(mlContext);
    }

    @Override
    public void runScript() throws IOException {
        List<String> args = new ArrayList<>();
        // check if tensorboard is in the environment
        if (checkPythonEnvironment("which tensorboard") != 0) {
            throw new RuntimeException("tensorboard doesn't exist");
        }
        args.add("tensorboard");
        args.add(
                "--logdir="
                        + mlContext
                                .getProperties()
                                .getOrDefault(
                                        MLConstants.CHECKPOINT_DIR,
                                        mlContext.getWorkDir().getAbsolutePath()));
        String port =
                mlContext
                        .getProperties()
                        .getOrDefault(
                                TFConstants.TENSORBOARD_PORT,
                                String.valueOf(IpHostUtil.getFreePort()));
        args.add("--port=" + port);
        args.add("--host=" + mlContext.getNodeServerIP());
        ProcessBuilder builder = new ProcessBuilder(args);
        String classPath = getClassPath();
        if (classPath == null) {
            // can happen in UT
            LOG.warn("Cannot find proper classpath for the Python process.");
        } else {
            mlContext.putEnvProperty(MLConstants.CLASSPATH, classPath);
        }
        buildProcessBuilder(builder);
        LOG.info("{} Python cmd: {}", mlContext.getIdentity(), Joiner.on(" ").join(args));
        runProcess(builder);
    }

    @VisibleForTesting
    public void runProcess(ProcessBuilder builder) throws IOException {
        super.runProcess(builder);
    }
}
