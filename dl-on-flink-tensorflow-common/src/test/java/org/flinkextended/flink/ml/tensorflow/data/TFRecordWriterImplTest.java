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

import java.io.IOException;

import static org.junit.Assert.*;

public class TFRecordWriterImplTest {

    private MLContext mlContext;
    private TFRecordWriterImpl tfRecordWriter;

    @Before
    public void setUp() throws Exception {
        mlContext = DummyContext.createDummyMLContext();
        tfRecordWriter = new TFRecordWriterImpl(mlContext);
    }

    @After
    public void tearDown() throws Exception {
        tfRecordWriter.close();
    }

    @Test
    public void testWrite() throws IOException {
        final SpscOffHeapQueue outputQueue = mlContext.getOutputQueue();
        final SpscOffHeapQueue.QueueInputStream inputStream =
                new SpscOffHeapQueue.QueueInputStream(outputQueue);
        final TFRecordReader tfRecordReader = new TFRecordReader(inputStream, true);

        byte[] bytes = new byte[] {1, 3, 4};
        tfRecordWriter.write(bytes);

        byte[] read = tfRecordReader.read();
        assertArrayEquals(bytes, read);

        tfRecordWriter.write(bytes, 1, 2);
        read = tfRecordReader.read();
        assertArrayEquals(new byte[] {3, 4}, read);
    }
}
