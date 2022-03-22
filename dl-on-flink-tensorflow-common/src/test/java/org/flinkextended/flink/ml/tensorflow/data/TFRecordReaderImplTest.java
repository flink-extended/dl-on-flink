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

package org.flinkextended.flink.ml.tensorflow.data;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.util.DummyContext;
import org.flinkextended.flink.ml.util.SpscOffHeapQueue;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.io.DataOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

import static org.junit.Assert.*;

public class TFRecordReaderImplTest {

    private TFRecordReaderImpl tfRecordReader;
    private MLContext mlContext;

    @Before
    public void setUp() throws Exception {
        mlContext = DummyContext.createDummyMLContext();
        tfRecordReader = new TFRecordReaderImpl(mlContext);
    }

    @After
    public void tearDown() throws Exception {
        tfRecordReader.close();
    }

    @Test
    public void testTryRead() throws IOException {
        final SpscOffHeapQueue inputQueue = mlContext.getInputQueue();
        final SpscOffHeapQueue.QueueOutputStream output =
                new SpscOffHeapQueue.QueueOutputStream(inputQueue);
        final DataOutputStream dataOutputStream = new DataOutputStream(output);
        final TFRecordWriter tfRecordWriter = new TFRecordWriter(dataOutputStream);
        tfRecordWriter.write("Hello".getBytes(StandardCharsets.UTF_8));
        assertEquals("Hello", new String(tfRecordReader.tryRead()));
        assertNull(tfRecordReader.tryRead());

        dataOutputStream.close();
        assertNull(tfRecordReader.read());
        assertTrue(tfRecordReader.isReachEOF());
    }
}
