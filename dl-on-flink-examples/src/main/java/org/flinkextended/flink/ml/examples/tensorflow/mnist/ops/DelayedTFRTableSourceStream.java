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

package org.flinkextended.flink.ml.examples.tensorflow.mnist.ops;

import org.flinkextended.flink.ml.operator.util.TypeUtil;
import org.flinkextended.flink.ml.tensorflow.io.TFRExtractRowHelper;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.TableSchema;
import org.apache.flink.table.sources.StreamTableSource;
import org.apache.flink.types.Row;

import java.util.Arrays;

/** DelayedTFRTableSourceStream. */
public class DelayedTFRTableSourceStream implements StreamTableSource<Row> {

    private static final long DEFAULT_DELAY_BOUND = 20;

    private final String[] paths;
    private final Long delayBound;
    private final RowTypeInfo outRowType;
    private final TFRExtractRowHelper.ScalarConverter[] converters;

    private DelayedTFRTableSourceStream(
            String[] paths,
            int epochs,
            Long delayBound,
            RowTypeInfo outRowType,
            TFRExtractRowHelper.ScalarConverter[] converters) {
        this.paths = paths;
        this.delayBound = delayBound;
        this.outRowType = outRowType;
        this.converters = converters;
    }

    public DelayedTFRTableSourceStream(
            String[] paths,
            int epochs,
            RowTypeInfo outRowType,
            TFRExtractRowHelper.ScalarConverter[] converters) {
        this(paths, epochs, DEFAULT_DELAY_BOUND, outRowType, converters);
    }

    @Override
    public TypeInformation<Row> getReturnType() {
        return outRowType;
    }

    @Override
    public TableSchema getTableSchema() {
        return TypeUtil.rowTypeInfoToTableSchema(outRowType);
    }

    @Override
    public String explainSource() {
        return "Delayed TFRecord source " + Arrays.toString(paths);
    }

    @Override
    public DataStream<Row> getDataStream(StreamExecutionEnvironment execEnv) {
        return execEnv.addSource(
                        new DelayedTFRSourceFunction(paths, delayBound, outRowType, converters))
                .setParallelism(1)
                .name(explainSource());
    }
}
