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

package org.flinkextended.flink.ml.examples.tensorflow.it;

import org.flinkextended.flink.ml.examples.tensorflow.mnist.MnistDataUtil;
import org.flinkextended.flink.ml.examples.tensorflow.mnist.MnistDist;
import org.flinkextended.flink.ml.examples.util.CodeUtil;
import org.flinkextended.flink.ml.util.MiniCluster;
import org.flinkextended.flink.ml.util.SysUtil;

import com.google.common.base.Preconditions;
import com.google.common.io.Files;
import org.junit.*;

import java.io.File;
import java.io.IOException;

public class MnistIT {

    private static final String MNIST_FOLDER = "mnist_input";
    public static final String MNIST_CONTAINER_PATH = "/tmp/" + MNIST_FOLDER;

    private static MiniCluster miniCluster;

    @BeforeClass
    public static void setUp() throws Exception {
        miniCluster = MiniCluster.start(3);
        miniCluster.setExecJar(
                "/dl-on-flink-examples/target/dl-on-flink-examples-"
                        + SysUtil.getProjectVersion()
                        + ".jar");
        Preconditions.checkState(
                miniCluster.copyToJM(MnistDataUtil.downloadData(), MNIST_CONTAINER_PATH));
    }

    @AfterClass
    public static void tearDown() throws Exception {
        if (miniCluster != null) {
            miniCluster.stop();
        }
    }

    public MnistIT() {}

    @After
    public void clearLogs() {
        miniCluster.emptyTMLogs();
    }

    @Test
    public void mnistDistStream() throws IOException {
        runAndVerify(miniCluster, MnistDist.EnvMode.StreamEnv);
    }

    @Test
    public void mnistDistStreamTable() throws IOException {
        runAndVerify(miniCluster, MnistDist.EnvMode.StreamTableEnv);
    }

    private void runAndVerify(MiniCluster miniCluster, MnistDist.EnvMode mode) throws IOException {
        runAndVerify(miniCluster, mode, false);
    }

    static boolean runAndVerify(
            MiniCluster miniCluster, MnistDist.EnvMode mode, boolean withRestart)
            throws IOException {
        String output = run(miniCluster, mode, withRestart);
        System.out.println(output);
        if (!output.contains("Program execution finished")) {
            File tmp = Files.createTempDir();
            miniCluster.dumpFlinkLogs(tmp);
            Assert.fail(
                    "MnistDist failed in mode "
                            + mode
                            + ", check logs in "
                            + tmp.getAbsolutePath());
            return false;
        } else {
            File tmp = Files.createTempDir();
            miniCluster.dumpFlinkLogs(tmp);
            System.out.println("logs in " + tmp.getAbsolutePath());
        }
        return true;
    }

    private static String run(MiniCluster miniCluster, MnistDist.EnvMode mode, boolean withRestart)
            throws IOException {
        String codeRemotePath = null;
        try {
            codeRemotePath = CodeUtil.copyCodeToHdfs(miniCluster);
        } catch (IOException e) {
            e.printStackTrace();
            throw e;
        }
        String output =
                miniCluster.flinkRun(
                        MnistDist.class.getCanonicalName(),
                        "--zk-conn-str",
                        miniCluster.getZKContainer(),
                        "--mode",
                        mode.toString(),
                        "--setup",
                        miniCluster.getLocalBuildDir()
                                + "/dl-on-flink-examples/src/test/python/mnist_data_setup.py",
                        "--train",
                        "mnist_dist.py",
                        "--envpath",
                        miniCluster.getVenvHdfsPath(),
                        "--mnist-files",
                        MNIST_CONTAINER_PATH,
                        "--with-restart",
                        String.valueOf(withRestart),
                        "--code-path",
                        codeRemotePath);
        return output;
    }
}
