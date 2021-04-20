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

import com.alibaba.flink.ml.tensorflow.data.TFRecordReader;
import com.alibaba.flink.ml.tensorflow.io.TFRExtractRowHelper;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.ResultTypeQueryable;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.checkpoint.ListCheckpointed;
import org.apache.flink.streaming.api.functions.source.RichParallelSourceFunction;
import org.apache.flink.types.Row;

import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Collections;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

public class DelayedTFRSourceFunction extends RichParallelSourceFunction<Row>
		implements ListCheckpointed<Long>, ResultTypeQueryable<Row> {

	private static Logger LOG = LoggerFactory.getLogger(DelayedTFRSourceFunction.class);

	private final String[] paths;
	private final long delayBound;
	private final RowTypeInfo outRowType;
	private final TFRExtractRowHelper extractRowHelper;
	private long offset = 0;
	private long numRead = 0;
	private volatile boolean cancelled;

	DelayedTFRSourceFunction(String[] paths, long delayBound, RowTypeInfo outRowType,
			TFRExtractRowHelper.ScalarConverter[] converters) {
		this.paths = paths;
		this.delayBound = delayBound;
		this.outRowType = outRowType;
		extractRowHelper = new TFRExtractRowHelper(outRowType, converters);
	}

	@Override
	public void open(Configuration parameters) throws Exception {
		super.open(parameters);
		if (offset != 0) {
			LOG.info("Restored from offset {}", offset);
		}
		numRead = 0;
		cancelled = false;
	}

	@Override
	public List<Long> snapshotState(long l, long l1) throws Exception {
		return Collections.singletonList(offset);
	}

	@Override
	public void restoreState(List<Long> list) throws Exception {
		offset = list.get(0);
	}

	@Override
	public void run(SourceContext<Row> sourceContext) throws Exception {
		final Object lock = sourceContext.getCheckpointLock();
		org.apache.hadoop.conf.Configuration hadoopConf = new org.apache.hadoop.conf.Configuration();
		for (String p : paths) {
			Path path = new Path(p);
			FileSystem fs = path.getFileSystem(hadoopConf);
			try (FSDataInputStream inputStream = fs.open(path)) {
				TFRecordReader tfrReader = new TFRecordReader(inputStream, true);
				byte[] bytes = tfrReader.read();
				while (bytes != null) {
					if (cancelled) {
						return;
					}
					if (numRead == offset) {
						synchronized (lock) {
							sourceContext.collect(extractRowHelper.extract(bytes));
							offset++;
						}
						Thread.sleep(ThreadLocalRandom.current().nextLong(delayBound) + 1);
					}
					numRead++;
					bytes = tfrReader.read();
				}
			}
		}
	}

	@Override
	public void cancel() {
		cancelled = true;
	}

	@Override
	public TypeInformation<Row> getProducedType() {
		return outRowType;
	}
}
