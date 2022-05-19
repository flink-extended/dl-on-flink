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

package org.flinkextended.flink.ml.tensorflow.io;

import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.table.connector.ChangelogMode;
import org.apache.flink.table.connector.source.DynamicTableSource;
import org.apache.flink.table.connector.source.InputFormatProvider;
import org.apache.flink.table.connector.source.ScanTableSource;

import com.google.common.base.Preconditions;

import java.io.File;
import java.util.Arrays;

/** TFRToRowInputFormat corresponds to flink table source function. */
public class TFRToRowTableSource implements ScanTableSource {

    private final String[] paths;
    private final int epochs;
    private final RowTypeInfo outRowType;
    private final String[] outColAliases;
    private final TFRExtractRowHelper.ScalarConverter[] converters;

    public TFRToRowTableSource(
            String[] paths,
            int epochs,
            RowTypeInfo outRowType,
            String[] outColAliases,
            TFRExtractRowHelper.ScalarConverter[] converters) {
        Preconditions.checkArgument(outRowType.getArity() == outColAliases.length);
        this.paths = paths;
        this.epochs = epochs;
        this.outRowType = outRowType;
        this.outColAliases = outColAliases;
        this.converters = converters;
    }

    public TFRToRowTableSource(
            String[] paths,
            int epochs,
            RowTypeInfo outRowType,
            TFRExtractRowHelper.ScalarConverter[] converters) {
        this(paths, epochs, outRowType, outRowType.getFieldNames(), converters);
    }

    public TFRToRowTableSource(
            File[] files,
            int epochs,
            RowTypeInfo outRowType,
            TFRExtractRowHelper.ScalarConverter[] converters) {
        this(files, epochs, outRowType, outRowType.getFieldNames(), converters);
    }

    public TFRToRowTableSource(
            File[] files,
            int epochs,
            RowTypeInfo outRowType,
            String[] outColAliases,
            TFRExtractRowHelper.ScalarConverter[] converters) {
        this(
                Arrays.stream(files).map(f -> f.getAbsolutePath()).toArray(String[]::new),
                epochs,
                outRowType,
                outColAliases,
                converters);
    }

    @Override
    public ChangelogMode getChangelogMode() {
        return ChangelogMode.insertOnly();
    }

    @Override
    public ScanRuntimeProvider getScanRuntimeProvider(ScanContext runtimeProviderContext) {
        final TFRToRowInputFormat tfrToRowInputFormat =
                new TFRToRowInputFormat(paths, epochs, outRowType, outColAliases, converters);
        return InputFormatProvider.of(new TFRToRowDataInputFormat(tfrToRowInputFormat));
    }

    @Override
    public DynamicTableSource copy() {
        return new TFRToRowTableSource(
                this.paths, this.epochs, this.outRowType, this.outColAliases, this.converters);
    }

    @Override
    public String asSummaryString() {
        return String.format(
                "TFRecord source %s to %s", Arrays.toString(paths), outRowType.toString());
    }
}
