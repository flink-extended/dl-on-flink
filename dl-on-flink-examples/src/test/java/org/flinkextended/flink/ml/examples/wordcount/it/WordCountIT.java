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

package org.flinkextended.flink.ml.examples.wordcount.it;

import org.flinkextended.flink.ml.examples.wordcount.WordCount;
import org.flinkextended.flink.ml.util.MiniCluster;
import org.flinkextended.flink.ml.util.SysUtil;

import com.google.common.io.Files;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import java.io.File;

/** WordCount integration test. */
public class WordCountIT {
    private static MiniCluster miniCluster;
    private static final int numTMs = 3;

    @Before
    public void setUp() throws Exception {
        miniCluster = MiniCluster.start(numTMs, false);
        miniCluster.setExecJar(
                "/dl-on-flink-examples/target/dl-on-flink-examples-"
                        + SysUtil.getProjectVersion()
                        + ".jar");
    }

    @After
    public void tearDown() throws Exception {
        if (miniCluster != null) {
            miniCluster.stop();
        }
    }

    @Test
    public void trainStream() throws Exception {
        runAndVerify(miniCluster);
    }

    private static String run(MiniCluster miniCluster) {
        String output = miniCluster.flinkRun(WordCount.class.getCanonicalName());
        return output;
    }

    static boolean runAndVerify(MiniCluster miniCluster) {
        String output = run(miniCluster);
        System.out.println(output);
        if (!output.contains("Program execution finished")) {
            File tmp = Files.createTempDir();
            miniCluster.dumpFlinkLogs(tmp);
            Assert.fail("run failed in mode, check logs in " + tmp.getAbsolutePath());
            return false;
        } else {
            File tmp = Files.createTempDir();
            miniCluster.dumpFlinkLogs(tmp);
            System.out.println("logs in " + tmp.getAbsolutePath());
        }
        return true;
    }
}
