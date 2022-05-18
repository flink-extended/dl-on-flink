/*
 * Copyright 2022 Deep Learning on Flink Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
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
import org.flinkextended.flink.ml.util.MiniCluster;
import org.flinkextended.flink.ml.util.SysUtil;

import com.google.common.base.Preconditions;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.Random;

/** Integration test for failover. */
public class FailoverIT {
    private static final Logger LOG = LoggerFactory.getLogger(FailoverIT.class);

    private MiniCluster miniCluster;
    private static final int numTMs = 3;
    private Random r = new Random();
    private volatile boolean success;

    @Before
    public void setUp() throws Exception {
        miniCluster = MiniCluster.start(numTMs);
        miniCluster.setExecJar(
                "/dl-on-flink-examples/target/dl-on-flink-examples-"
                        + SysUtil.getProjectVersion()
                        + ".jar");
        Preconditions.checkState(
                miniCluster.copyToJM(MnistDataUtil.downloadData(), MnistIT.MNIST_CONTAINER_PATH));
    }

    @After
    public void tearDown() throws Exception {
        if (miniCluster != null) {
            miniCluster.stop();
        }
    }

    public FailoverIT() {}

    @Test
    public void testKillOneTM() throws InterruptedException {
        Thread t =
                new Thread(
                        () -> {
                            try {
                                success =
                                        MnistIT.runAndVerify(
                                                miniCluster, MnistDist.EnvMode.StreamEnv, true);
                            } catch (IOException e) {
                                e.printStackTrace();
                            }
                        });
        t.start();

        int sleepTime = r.nextInt(20000) + 20000;
        Thread.sleep(sleepTime);
        miniCluster.killOneTMWithWorkload();

        t.join();
        Assert.assertTrue(success);
    }
}
