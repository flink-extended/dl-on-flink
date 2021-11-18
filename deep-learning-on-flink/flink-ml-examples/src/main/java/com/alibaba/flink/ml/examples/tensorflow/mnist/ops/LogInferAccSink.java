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

package com.alibaba.flink.ml.examples.tensorflow.mnist.ops;

import com.google.common.base.Preconditions;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.flink.streaming.api.checkpoint.ListCheckpointed;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.apache.flink.table.data.RowData;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.text.DecimalFormat;
import java.util.Collections;
import java.util.List;

public class LogInferAccSink extends RichSinkFunction<RowData> implements ListCheckpointed<ImmutablePair<Long, Long>> {

    private static final Logger LOG = LoggerFactory.getLogger(LogInferAccSink.class);

    private transient long total = 0;
    private transient long correct = 0;
    // Hadoop path is not serializable
    private final String pathStr;

    public LogInferAccSink() {
        this(null);
    }

    public LogInferAccSink(String pathStr) {
        this.pathStr = pathStr;
    }

    @Override
    public void open(org.apache.flink.configuration.Configuration parameters) throws Exception {
        super.open(parameters);
        if (total != 0 || correct != 0) {
            LOG.info("Restored state: total={}, correct={}", total, correct);
        }
    }

    @Override
    public void invoke(RowData value, Context context) throws Exception {
        total++;
        if (value.getLong(0) == value.getLong(1)) {
            correct++;
        }
        if (total % 100 == 0) {
            System.out.println("Processed value:" + value.toString());
        }
    }

    @Override
    public void close() throws Exception {
        DecimalFormat df = new DecimalFormat("#.##");
        LOG.info(String.format("Records processed: %d, Accuracy: %s%%",
                total, total > 0 ? df.format(100.0 * correct / total) : "0"));
        if (pathStr != null) {
            Path outDir = new Path(pathStr);
            FileSystem fs = FileSystem.get(outDir.toUri(), new Configuration());
            fs.mkdirs(outDir);
            Path outFile = new Path(outDir, String.valueOf(getRuntimeContext().getIndexOfThisSubtask()));
            if (fs.exists(outFile)) {
                LOG.info("{} already exists. Tying to delete it", outFile.toString());
                Preconditions.checkState(fs.delete(outFile, false), "Cannot delete previous output file " + outFile);
            }
            LOG.info("Writing result to " + outFile.toString());
            try (FSDataOutputStream out = fs.create(outFile)) {
                out.writeUTF(String.valueOf(total));
            }
        }
    }

    @Override
    public List<ImmutablePair<Long, Long>> snapshotState(long l, long l1) throws Exception {
        return Collections.singletonList(ImmutablePair.of(total, correct));
    }

    @Override
    public void restoreState(List<ImmutablePair<Long, Long>> list) throws Exception {
        ImmutablePair<Long, Long> pair = list.get(0);
        total = pair.getLeft();
        correct = pair.getRight();
    }
}
