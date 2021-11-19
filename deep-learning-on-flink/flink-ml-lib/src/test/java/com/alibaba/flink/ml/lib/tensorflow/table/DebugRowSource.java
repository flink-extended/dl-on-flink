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

package com.alibaba.flink.ml.lib.tensorflow.table;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.ResultTypeQueryable;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.streaming.api.functions.source.ParallelSourceFunction;
import org.apache.flink.table.data.GenericArrayData;
import org.apache.flink.table.data.GenericRowData;
import org.apache.flink.table.data.RowData;
import org.apache.flink.table.data.StringData;


public class DebugRowSource implements ParallelSourceFunction<RowData>, ResultTypeQueryable {
    public RowTypeInfo typeInfo;
    private int rank;
    private boolean hasString;

    public DebugRowSource(int rank, boolean hasString, RowTypeInfo typeInfo) {
        this.rank = rank;
        this.hasString = hasString;
        this.typeInfo = typeInfo;
    }

    @Override
    public void run(SourceContext<RowData> ctx) throws Exception {
        for (int i = 0; i < 20; i++) {
            if (hasString) {
                GenericRowData row = new GenericRowData(3);
                switch (rank) {
                    case 2: {
                        Float[] c1 = {1.0f * i, 1.0f * i};
                        GenericArrayData[] cc1 = {new GenericArrayData(c1), new GenericArrayData(c1)};

                        Float[] c2 = {2.0f * i, 2.0f * i};
                        GenericArrayData[] cc2 = {new GenericArrayData(c2), new GenericArrayData(c2)};

                        StringData[] c3 = {StringData.fromString(String.valueOf(1.0f * i)),
                                StringData.fromString(String.valueOf(1.0f * i))};
                        GenericArrayData[] cc3 = {new GenericArrayData(c3), new GenericArrayData(c3)};

                        row.setField(0, new GenericArrayData(cc1));
                        row.setField(1, new GenericArrayData(cc2));
                        row.setField(2, new GenericArrayData(cc3));
                        break;
                    }
                    case 1: {
                        Float[] c1 = {1.0f * i, 1.0f * i};
                        Float[] c2 = {2.0f * i, 2.0f * i};
                        StringData[] c3 = {StringData.fromString(String.valueOf(1.0f * i)),
                                StringData.fromString(String.valueOf(1.0f * i))};
                        row.setField(0, new GenericArrayData(c1));
                        row.setField(1, new GenericArrayData(c2));
                        row.setField(2, new GenericArrayData(c3));
                        break;
                    }
                    default: {
                        row.setField(0, 1.0f * i);
                        row.setField(1, 2.0f * i);
                        row.setField(2, StringData.fromString(String.valueOf(1.0f * i)));
                    }
                }
                ctx.collect(row);
            } else {
                GenericRowData row = new GenericRowData(2);
                switch (rank) {
                    case 2: {
                        Float[] c1 = {1.0f * i, 1.0f * i};
                        GenericArrayData[] cc1 = {new GenericArrayData(c1), new GenericArrayData(c1)};

                        Float[] c2 = {2.0f * i, 2.0f * i};
                        GenericArrayData[] cc2 = {new GenericArrayData(c2), new GenericArrayData(c2)};

                        row.setField(0, new GenericArrayData(cc1));
                        row.setField(1, new GenericArrayData(cc2));
                        break;
                    }
                    case 1: {
                        Float[] c1 = {1.0f * i, 1.0f * i};
                        Float[] c2 = {2.0f * i, 2.0f * i};
                        row.setField(0, new GenericArrayData(c1));
                        row.setField(1, new GenericArrayData(c2));
                        break;
                    }
                    default: {
                        row.setField(0, 1.0f * i);
                        row.setField(1, 2.0f * i);
                    }
                }
                ctx.collect(row);
            }
        }
    }

    @Override
    public void cancel() {

    }

    @Override
    public TypeInformation getProducedType() {
        return typeInfo;
    }
}
