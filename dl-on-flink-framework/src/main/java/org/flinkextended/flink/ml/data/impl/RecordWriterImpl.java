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

package org.flinkextended.flink.ml.data.impl;

import org.flinkextended.flink.ml.cluster.node.MLContext;
import org.flinkextended.flink.ml.data.RecordWriter;
import org.flinkextended.flink.ml.util.SpscOffHeapQueue;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

/** a simple RecordWriter implementation. */
public class RecordWriterImpl implements RecordWriter {
    private final SpscOffHeapQueue.QueueOutputStream output;
    byte[] buff = new byte[4];
    ByteBuffer bb = ByteBuffer.wrap(buff);

    public RecordWriterImpl(MLContext mlContext) {
        bb.order(ByteOrder.LITTLE_ENDIAN);
        this.output = mlContext.getOutWriter();
    }

    public boolean write(byte[] record, int offset, int length) throws IOException {
        int totalSize = 4 + (length - offset);
        if (!output.tryReserve((totalSize))) {
            return false;
        }

        /** TFRecord format: uint32 length byte data[length] */
        byte[] len = toInt32LE(length);
        output.write(len, 0, 4);
        output.write(record, offset, length);
        return true;
    }

    public boolean write(byte[] record) throws IOException {
        return write(record, 0, record.length);
    }

    private byte[] toInt32LE(int data) {
        bb.clear();
        bb.putInt(data);
        return buff;
    }

    @Override
    public void close() throws IOException {}
}
