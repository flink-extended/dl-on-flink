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

package org.flinkextended.flink.ml.examples.tensorflow.ops;

import org.flinkextended.flink.ml.examples.tensorflow.mnist.ops.MnistTFRPojo;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.table.api.Types;
import org.apache.flink.table.functions.TableFunction;
import org.apache.flink.types.Row;

public class MnistTFRExtractRowFunction extends TableFunction<Row> {

    public void eval(byte[] record) throws Exception {
        if (record == null) {
            // TODO: how to avoid this
            return;
        }
        MnistTFRPojo pojo = MnistTFRPojo.from(record);
        Row res = new Row(2);
        res.setField(0, pojo.getImage_raw());
        res.setField(1, pojo.getLabel());
        collect(res);
    }

    @Override
    public TypeInformation<Row> getResultType() {
        return Types.ROW(Types.STRING(), Types.INT());
    }
}
