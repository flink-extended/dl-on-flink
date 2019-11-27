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

import org.apache.flink.api.common.typeinfo.BasicTypeInfo;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.ResultTypeQueryable;
import org.apache.flink.api.java.typeutils.RowTypeInfo;
import org.apache.flink.streaming.api.functions.source.ParallelSourceFunction;
import org.apache.flink.types.Row;


public class DebugRowSource implements ParallelSourceFunction<Row>, ResultTypeQueryable {
    public RowTypeInfo getTypeInfo() {
        return typeInfo;
    }

    public RowTypeInfo typeInfo;
    private int rank;
    private boolean hasString;

    public DebugRowSource(int rank, boolean hasString) {
        this.rank = rank;
        this.hasString = hasString;
        if(hasString){
            TypeInformation[] types = new TypeInformation[3];
            switch (rank){
                case 1:{
                    types[0] = TypeInformation.of(float[].class);
                    types[1] = TypeInformation.of(float[].class);
                    types[2] = TypeInformation.of(String[].class);
                    break;
                }
                case 2:{
                    types[0] = TypeInformation.of(float[][].class);
                    types[1] = TypeInformation.of(float[][].class);
                    types[2] = TypeInformation.of(String[][].class);
                    break;
                }
                default:{
                    types[0] = BasicTypeInfo.FLOAT_TYPE_INFO;
                    types[1] = BasicTypeInfo.FLOAT_TYPE_INFO;
                    types[2] = BasicTypeInfo.STRING_TYPE_INFO;
                }
            }
            String[] names = { "a", "b", "c" };
            typeInfo = new RowTypeInfo(types, names);
        }else {
            TypeInformation[] types = new TypeInformation[2];
            switch (rank) {
                case 1: {
                    types[0] = TypeInformation.of(float[].class);
                    types[1] = TypeInformation.of(float[].class);
                    break;
                }
                case 2: {
                    types[0] = TypeInformation.of(float[][].class);
                    types[1] = TypeInformation.of(float[][].class);
                    break;
                }
                default: {
                    types[0] = BasicTypeInfo.FLOAT_TYPE_INFO;
                    types[1] = BasicTypeInfo.FLOAT_TYPE_INFO;
                }
            }
            String[] names = { "a", "b" };
            typeInfo = new RowTypeInfo(types, names);
        }
    }

    @Override
    public void run(SourceContext<Row> ctx) throws Exception {
        for(int i = 0; i < 20; i++){
            if(hasString){
                Row row = new Row(3);
                switch (rank){
                    case 2:{
                        float[] c1 = { 1.0f * i, 1.0f * i };
                        float[][] cc1 = {c1, c1};

                        float[] c2 = { 2.0f * i, 2.0f * i };
                        float[][] cc2 = {c2, c2};

                        String[] c3 = { String.valueOf(1.0f * i), String.valueOf(1.0f * i) };
                        String[][] cc3 = {c3, c3};

                        row.setField(0, cc1);
                        row.setField(1, cc2);
                        row.setField(2, cc3);
                        break;
                    }
                    case 1:{
                        float[] c1 = { 1.0f * i, 1.0f * i };
                        float[] c2 = { 2.0f * i, 2.0f * i };
                        String[] c3 = { String.valueOf(1.0f * i), String.valueOf(1.0f * i) };
                        row.setField(0, c1);
                        row.setField(1, c2);
                        row.setField(2, c3);
                        break;
                    }
                    default:{
                        row.setField(0, 1.0f * i);
                        row.setField(1, 2.0f * i);
                        row.setField(2, String.valueOf(1.0f * i));
                    }
                }
                ctx.collect(row);
            }else {
                Row row = new Row(2);
                switch (rank){
                    case 2:{
                        float[] c1 = { 1.0f * i, 1.0f * i };
                        float[][] cc1 = {c1, c1};

                        float[] c2 = { 2.0f * i, 2.0f * i };
                        float[][] cc2 = {c2, c2};

                        row.setField(0, cc1);
                        row.setField(1, cc2);
                        break;
                    }
                    case 1:{
                        float[] c1 = { 1.0f * i, 1.0f * i };
                        float[] c2 = { 2.0f * i, 2.0f * i };
                        row.setField(0, c1);
                        row.setField(1, c2);
                        break;
                    }
                    default:{
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
