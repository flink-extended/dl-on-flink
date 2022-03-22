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

package org.flinkextended.flink.ml.tensorflow.io;

import org.apache.flink.api.common.io.RichInputFormat;
import org.apache.flink.api.common.io.statistics.BaseStatistics;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.ResultTypeQueryable;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.core.io.InputSplitAssigner;
import org.apache.flink.table.data.GenericRowData;
import org.apache.flink.table.data.RowData;
import org.apache.flink.table.data.StringData;
import org.apache.flink.types.Row;

import java.io.IOException;

public class TFRToRowDataInputFormat extends RichInputFormat<RowData, TFRecordInputSplit>
        implements ResultTypeQueryable<Row> {

    private final TFRToRowInputFormat tfrToRowInputFormat;

    public TFRToRowDataInputFormat(TFRToRowInputFormat tfrToRowInputFormat) {
        this.tfrToRowInputFormat = tfrToRowInputFormat;
    }

    @Override
    public void configure(Configuration parameters) {}

    @Override
    public BaseStatistics getStatistics(BaseStatistics cachedStatistics) throws IOException {
        return tfrToRowInputFormat.getStatistics(cachedStatistics);
    }

    @Override
    public TFRecordInputSplit[] createInputSplits(int minNumSplits) throws IOException {
        return tfrToRowInputFormat.createInputSplits(minNumSplits);
    }

    @Override
    public InputSplitAssigner getInputSplitAssigner(TFRecordInputSplit[] inputSplits) {
        return tfrToRowInputFormat.getInputSplitAssigner(inputSplits);
    }

    @Override
    public void open(TFRecordInputSplit split) throws IOException {
        tfrToRowInputFormat.open(split);
    }

    @Override
    public boolean reachedEnd() throws IOException {
        return tfrToRowInputFormat.reachedEnd();
    }

    @Override
    public void close() throws IOException {
        tfrToRowInputFormat.close();
    }

    @Override
    public TypeInformation<Row> getProducedType() {
        return tfrToRowInputFormat.getProducedType();
    }

    @Override
    public RowData nextRecord(RowData reuse) throws IOException {
        final Row row = tfrToRowInputFormat.nextRecord(null);
        if (row == null) {
            return null;
        }
        return rowToRowData(row);
    }

    private RowData rowToRowData(Row row) {
        GenericRowData rowData = new GenericRowData(row.getArity());
        for (int i = 0; i < row.getArity(); ++i) {
            Object field = row.getField(i);
            if (field instanceof String) {
                field = StringData.fromString((String) field);
            }
            rowData.setField(i, field);
        }
        return rowData;
    }
}
