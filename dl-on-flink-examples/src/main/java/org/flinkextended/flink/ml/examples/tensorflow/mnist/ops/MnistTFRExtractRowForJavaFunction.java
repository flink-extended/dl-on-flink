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

package org.flinkextended.flink.ml.examples.tensorflow.mnist.ops;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.table.api.Types;
import org.apache.flink.table.functions.TableFunction;
import org.apache.flink.types.Row;

import com.google.common.primitives.UnsignedBytes;

import java.nio.charset.StandardCharsets;

/** Read MNIST TFR rows and convert data so that it can be used for Java inference. */
public class MnistTFRExtractRowForJavaFunction extends TableFunction<Row> {

    public void eval(String image, int label) throws Exception {
        byte[] imageBytes = image.getBytes(StandardCharsets.ISO_8859_1);
        float[] imageFloats = new float[imageBytes.length];
        for (int i = 0; i < imageFloats.length; i++) {
            int uByte = UnsignedBytes.toInt(imageBytes[i]);
            imageFloats[i] = (float) (uByte / 255.0);
        }
        Row res = new Row(2);
        res.setField(0, imageFloats);
        res.setField(1, (long) label);
        collect(res);
    }

    @Override
    public TypeInformation<Row> getResultType() {
        return Types.ROW(Types.PRIMITIVE_ARRAY(Types.FLOAT()), Types.LONG());
    }
}
