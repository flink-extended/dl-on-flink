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

package org.flinkextended.flink.ml.operator.ops.inputformat;

import org.flinkextended.flink.ml.cluster.ClusterConfig;
import org.flinkextended.flink.ml.cluster.ExecutionMode;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.coding.CodingException;
import org.flinkextended.flink.ml.coding.Decoding;
import org.flinkextended.flink.ml.data.RecordReader;
import org.flinkextended.flink.ml.operator.util.ColumnInfos;
import org.flinkextended.flink.ml.util.MLConstants;
import org.flinkextended.flink.ml.util.MLException;

import org.apache.flink.api.common.functions.RuntimeContext;
import org.apache.flink.api.common.io.DefaultInputSplitAssigner;
import org.apache.flink.configuration.Configuration;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.atomic.AtomicBoolean;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;
import static org.mockito.Matchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

/** Unit test for {@link AbstractNodeInputFormat}. */
public class AbstractNodeInputFormatTest {

    private DummyNodeInputFormat nodeInputFormat;

    @Before
    public void setUp() throws Exception {
        ClusterConfig config =
                ClusterConfig.newBuilder()
                        .setNodeEntry("entry.py", "main")
                        .setProperty(
                                MLConstants.RECORD_READER_CLASS, TestRecordReader.class.getName())
                        .setProperty(MLConstants.DECODING_CLASS, TestDecoding.class.getName())
                        .build();
        nodeInputFormat = new DummyNodeInputFormat(config);
        RuntimeContext mockRuntimeContext = mock(RuntimeContext.class);
        nodeInputFormat.setRuntimeContext(mockRuntimeContext);
    }

    @Test
    public void testGetInputSplitAssigner() {
        assertThat(
                nodeInputFormat.getInputSplitAssigner(new NodeInputSplit[0]),
                org.hamcrest.Matchers.instanceOf(DefaultInputSplitAssigner.class));
    }

    @Test
    public void testGetStatistics() throws IOException {
        assertNull(nodeInputFormat.getStatistics(null));
    }

    @Test
    public void testOpen() throws IOException {
        DummyNodeInputFormat nodeInputFormat = Mockito.spy(this.nodeInputFormat);
        nodeInputFormat.open(new NodeInputSplit(1, 0));
        verify(nodeInputFormat, times(1)).prepareMLContext(any());
        verify(nodeInputFormat, times(1)).getNodeServerRunnable(any());
        verify(nodeInputFormat, times(1)).preparePythonFiles();
    }

    @Test
    public void testReachedEnd() throws IOException, ExecutionException, InterruptedException {
        nodeInputFormat.open(new NodeInputSplit(1, 0));
        assertFalse(nodeInputFormat.reachedEnd());
        nodeInputFormat.markFinish();
        nodeInputFormat.waitServerFutureFinish();
        assertTrue(nodeInputFormat.reachedEnd());
    }

    @Test
    public void testNextRecord() throws IOException {
        nodeInputFormat.open(new NodeInputSplit(1, 0));
        assertFalse(nodeInputFormat.reachedEnd());
        assertEquals(Integer.valueOf(0), nodeInputFormat.nextRecord(null));
        assertEquals(Integer.valueOf(1), nodeInputFormat.nextRecord(null));
        assertTrue(nodeInputFormat.reachedEnd());
    }

    @Test
    public void testClose() throws IOException, InterruptedException, ExecutionException {
        DummyNodeInputFormat nodeInputFormat = Mockito.spy(this.nodeInputFormat);
        nodeInputFormat.open(new NodeInputSplit(1, 0));
        nodeInputFormat.markFinish();
        nodeInputFormat.waitServerFutureFinish();
        nodeInputFormat.close();
        assertTrue(nodeInputFormat.isClosed());
    }

    @Test
    public void testCloseTimeout() throws IOException {
        DummyNodeInputFormat nodeInputFormat = Mockito.spy(this.nodeInputFormat);
        nodeInputFormat.open(new NodeInputSplit(1, 0));
        nodeInputFormat.close();
        assertTrue(nodeInputFormat.isClosed());
    }

    private static class DummyNodeInputFormat extends AbstractNodeInputFormat<Integer> {
        private final AtomicBoolean finished = new AtomicBoolean(false);

        public DummyNodeInputFormat(ClusterConfig clusterConfig) {
            super(clusterConfig);
            closeTimeoutMs = 1_000;
        }

        @Override
        public void configure(Configuration parameters) {}

        @Override
        public NodeInputSplit[] createInputSplits(int minNumSplits) throws IOException {
            return new NodeInputSplit[0];
        }

        @Override
        protected MLContext prepareMLContext(Integer nodeIndex) throws MLException {
            return new MLContext(
                    ExecutionMode.OTHER,
                    "worker",
                    0,
                    clusterConfig.getNodeTypeCntMap(),
                    clusterConfig.getEntryFuncName(),
                    clusterConfig.getProperties(),
                    clusterConfig.getPythonVirtualEnvZipPath(),
                    ColumnInfos.dummy().getNameToTypeMap());
        }

        @Override
        protected Runnable getNodeServerRunnable(MLContext mlContext) {
            return () -> {
                while (!finished.get()) {
                    synchronized (finished) {
                        try {
                            if (finished.get()) {
                                return;
                            }
                            finished.wait();
                        } catch (InterruptedException e) {
                            // ignore
                        }
                    }
                }
            };
        }

        @Override
        void preparePythonFiles() {
            // do nothing
        }

        public void markFinish() {
            synchronized (finished) {
                finished.set(true);
                finished.notify();
            }
        }
    }

    /** Dummy RecordReader for testing. */
    public static class TestRecordReader implements RecordReader {

        private int count = 0;

        public TestRecordReader(MLContext mlContext) {}

        @Override
        public byte[] tryRead() throws IOException {
            return ByteBuffer.allocate(4).putInt(count++).array();
        }

        @Override
        public boolean isReachEOF() {
            return count > 1;
        }

        @Override
        public byte[] read() throws IOException {
            return tryRead();
        }

        @Override
        public void close() throws IOException {}
    }

    /** Dummy Decoding for testing. */
    public static class TestDecoding implements Decoding<Integer> {

        public TestDecoding(MLContext mlContext) {}

        @Override
        public Integer decode(byte[] bytes) throws CodingException {
            return ByteBuffer.wrap(bytes).getInt();
        }
    }
}
