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

package org.flinkextended.flink.ml.operator.ops;

import org.flinkextended.flink.ml.cluster.ClusterConfig;
import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.data.RecordWriter;
import org.flinkextended.flink.ml.operator.coding.RowCSVCoding;
import org.flinkextended.flink.ml.util.MLConstants;

import org.apache.flink.api.common.JobID;
import org.apache.flink.runtime.taskmanager.TaskManagerRuntimeInfo;
import org.apache.flink.streaming.api.operators.StreamingRuntimeContext;
import org.apache.flink.streaming.runtime.streamrecord.StreamRecord;
import org.apache.flink.types.Row;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;

import java.io.IOException;
import java.util.concurrent.atomic.AtomicBoolean;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

/** Unit test for {@link NodeOperator}. */
public class NodeOperatorTest {

    private TestNodeOperator nodeOperator;
    static StringBuilder writtenSb;

    @Before
    public void setUp() throws Exception {
        final ClusterConfig config =
                ClusterConfig.newBuilder()
                        .addNodeType("worker", 2)
                        .setNodeEntry("entry.py", "main")
                        .setProperty(MLConstants.ENCODING_CLASS, RowCSVCoding.class.getName())
                        .setProperty(RowCSVCoding.ENCODE_TYPES, "INT_32")
                        .setProperty(
                                MLConstants.RECORD_WRITER_CLASS, TestRecordWriter.class.getName())
                        .build();

        StreamingRuntimeContext mockRuntimeContext = Mockito.mock(StreamingRuntimeContext.class);
        final TaskManagerRuntimeInfo taskManagerRuntimeInfo = mock(TaskManagerRuntimeInfo.class);
        when(taskManagerRuntimeInfo.getTmpDirectories()).thenReturn(new String[] {"/tmp"});
        when(mockRuntimeContext.getTaskManagerRuntimeInfo()).thenReturn(taskManagerRuntimeInfo);
        when(mockRuntimeContext.getJobId()).thenReturn(new JobID());

        nodeOperator = new TestNodeOperator("worker", config, mockRuntimeContext);
        writtenSb = new StringBuilder();
    }

    @Test
    public void testOpen() throws Exception {
        assertNull(nodeOperator.getMlContext());
        assertNull(nodeOperator.getServerFuture());
        assertNull(nodeOperator.getDataExchange());
        nodeOperator.open();
        assertEquals("", nodeOperator.getMlContext().getEnvProperty(MLConstants.GPU_INFO));
        assertNotNull(nodeOperator.getServerFuture());
        assertNotNull(nodeOperator.getDataExchange());
    }

    @Test
    public void testProcessElement() throws Exception {
        nodeOperator.open();
        final Row row = new Row(1);
        row.setField(0, 0);
        nodeOperator.processElement(new StreamRecord<>(row));
        row.setField(0, 1);
        nodeOperator.processElement(new StreamRecord<>(row));
        assertEquals("0\n1\n", writtenSb.toString());
    }

    @Test
    public void testClose() throws Exception {
        nodeOperator.open();
        nodeOperator.markFinish();
        nodeOperator.getServerFuture().get();
        nodeOperator.getMlContext().getInputQueue().markFinished();
        nodeOperator.close();
        assertNull(nodeOperator.getServerFuture());
        assertNull(nodeOperator.getDataExchangeConsumerFuture());
    }

    @Test
    public void testCloseWithTimeout() throws Exception {
        nodeOperator.open();
        nodeOperator.close();
        assertNull(nodeOperator.getServerFuture());
        assertNull(nodeOperator.getDataExchangeConsumerFuture());
    }

    private static class TestNodeOperator extends NodeOperator<Integer> {
        private final AtomicBoolean finished = new AtomicBoolean(false);
        private final StreamingRuntimeContext runtimeContext;

        public TestNodeOperator(
                String nodeType,
                ClusterConfig clusterConfig,
                StreamingRuntimeContext runtimeContext) {
            super(nodeType, clusterConfig);
            this.runtimeContext = runtimeContext;
            closeTimeoutMs = 1_000;
        }

        @Override
        Runnable createNodeServerRunnable() {
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

        public void markFinish() {
            synchronized (finished) {
                finished.set(true);
                finished.notify();
            }
        }

        @Override
        public StreamingRuntimeContext getRuntimeContext() {
            return runtimeContext;
        }
    }

    /** RecordWriter for testing. */
    public static class TestRecordWriter implements RecordWriter {

        private final MLContext mlContext;

        public TestRecordWriter(MLContext mlContext) {
            this.mlContext = mlContext;
        }

        @Override
        public boolean write(byte[] record, int offset, int length) throws IOException {
            throw new UnsupportedOperationException();
        }

        @Override
        public boolean write(byte[] record) throws IOException {
            writtenSb.append(new String(record)).append("\n");
            return true;
        }

        @Override
        public void close() throws IOException {}

        public MLContext getMlContext() {
            return mlContext;
        }
    }
}
