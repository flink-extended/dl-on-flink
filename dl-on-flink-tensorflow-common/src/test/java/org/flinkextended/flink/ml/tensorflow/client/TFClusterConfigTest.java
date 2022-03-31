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

package org.flinkextended.flink.ml.tensorflow.client;

import org.flinkextended.flink.ml.tensorflow.cluster.TFAMStateMachineImpl;
import org.flinkextended.flink.ml.tensorflow.cluster.node.runner.TFMLRunner;
import org.flinkextended.flink.ml.tensorflow.data.TFRecordReaderImpl;
import org.flinkextended.flink.ml.tensorflow.data.TFRecordWriterImpl;
import org.flinkextended.flink.ml.tensorflow.util.TFConstants;
import org.flinkextended.flink.ml.util.MLConstants;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

/** Unit test for {@link TFClusterConfig}. */
public class TFClusterConfigTest {

    @Test
    public void testTFClusterConfigConfigWorkerPs() {
        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setNodeEntry("entry.py", "main")
                        .setWorkerCount(3)
                        .setPsCount(2)
                        .build();
        assertEquals(Integer.valueOf(3), config.getNodeCount("worker"));
        assertEquals(Integer.valueOf(2), config.getNodeCount("ps"));

        // check default properties
        assertEquals(TFMLRunner.class.getName(), config.getProperty(MLConstants.ML_RUNNER_CLASS));
        assertEquals(
                TFAMStateMachineImpl.class.getName(),
                config.getProperty(MLConstants.AM_STATE_MACHINE_CLASS));
        assertEquals(
                TFRecordReaderImpl.class.getName(),
                config.getProperty(MLConstants.RECORD_READER_CLASS));
        assertEquals(
                TFRecordWriterImpl.class.getName(),
                config.getProperty(MLConstants.RECORD_WRITER_CLASS));
    }

    @Test
    public void testTFClusterConfigSetWorkerZeroChief() {
        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setNodeEntry("entry.py", "main")
                        .setWorkerCount(2)
                        .setIsWorkerZeroChief(true)
                        .build();
        assertEquals("true", config.getProperty(TFConstants.TF_IS_WORKER_ZERO_CHIEF));
    }

    @Test
    public void testTFClusterConfigToBuilder() {
        final TFClusterConfig config =
                TFClusterConfig.newBuilder()
                        .setNodeEntry("entry.py", "main")
                        .setWorkerCount(3)
                        .setPsCount(2)
                        .build();

        final TFClusterConfig config2 =
                config.toBuilder()
                        .setWorkerCount(4)
                        .setPsCount(3)
                        .setIsWorkerZeroChief(true)
                        .build();

        assertEquals(Integer.valueOf(4), config2.getNodeCount("worker"));
        assertEquals(Integer.valueOf(3), config2.getNodeCount("ps"));
        assertEquals("true", config2.getProperty(TFConstants.TF_IS_WORKER_ZERO_CHIEF));
    }

    @Test(expected = IllegalStateException.class)
    public void testTFClusterConfigBuildWithoutWorkerNodeTypeThrowException() {
        TFClusterConfig.newBuilder().setNodeEntry("entry.py", "main").build();
    }
}
