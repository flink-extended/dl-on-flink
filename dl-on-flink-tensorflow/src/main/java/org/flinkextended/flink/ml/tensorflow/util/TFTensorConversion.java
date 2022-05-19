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

package org.flinkextended.flink.ml.tensorflow.util;

import com.google.common.base.Preconditions;
import org.tensorflow.Tensor;
import org.tensorflow.framework.TensorInfo;

import java.nio.DoubleBuffer;
import java.nio.FloatBuffer;
import java.nio.IntBuffer;
import java.nio.LongBuffer;
import java.util.Arrays;

// TODO: support more kinds of tensors

/** a util function: transformation between tensorflow tensor and java object. */
public class TFTensorConversion {

    private TFTensorConversion() {}

    /**
     * convert java objects to tensorflow tensor.
     *
     * @param objects given java objects.
     * @param tensorInfo target tensor type information.
     * @return result tensorflow tensor.
     */
    public static Tensor<?> toTensor(Object[] objects, TensorInfo tensorInfo) {
        switch (tensorInfo.getDtype()) {
            case DT_INT8:
            case DT_INT16:
            case DT_INT32:
                {
                    long[] shape = new long[] {objects.length, ((int[]) objects[0]).length};
                    IntBuffer intBuffer = IntBuffer.allocate(getCapacity(shape));
                    for (Object obj : objects) {
                        intBuffer.put((int[]) obj);
                    }
                    intBuffer.flip();
                    return Tensor.create(shape, intBuffer);
                }
            case DT_INT64:
                {
                    long[] shape = new long[] {objects.length, ((long[]) objects[0]).length};
                    LongBuffer longBuffer = LongBuffer.allocate(getCapacity(shape));
                    for (Object obj : objects) {
                        longBuffer.put((long[]) obj);
                    }
                    longBuffer.flip();
                    return Tensor.create(shape, longBuffer);
                }
            case DT_FLOAT:
                {
                    long[] shape = new long[] {objects.length, ((float[]) objects[0]).length};
                    FloatBuffer floatBuffer = FloatBuffer.allocate(getCapacity(shape));
                    for (Object obj : objects) {
                        floatBuffer.put((float[]) obj);
                    }
                    floatBuffer.flip();
                    return Tensor.create(shape, floatBuffer);
                }
            case DT_DOUBLE:
                {
                    long[] shape = new long[] {objects.length, ((double[]) objects[0]).length};
                    DoubleBuffer doubleBuffer = DoubleBuffer.allocate(getCapacity(shape));
                    for (Object obj : objects) {
                        doubleBuffer.put((double[]) obj);
                    }
                    doubleBuffer.flip();
                    return Tensor.create(shape, doubleBuffer);
                }
            default:
                throw new UnsupportedOperationException(
                        "Type can't be converted to tensor: " + tensorInfo.getDtype().name());
        }
    }

    /**
     * convert tensorflow tensor to java objects.
     *
     * @param tensor given tensorflow tensor.
     * @return java objects corresponded to given tensor.
     */
    public static Object[] fromTensor(Tensor<?> tensor) {
        Preconditions.checkArgument(
                tensor.shape().length == 1, "Can only convert tensors with shape long[]");
        final int size = (int) tensor.shape()[0];
        Object[] res = new Object[size];
        switch (tensor.dataType()) {
            case INT32:
                int[] ints = tensor.copyTo(new int[size]);
                for (int i = 0; i < size; i++) {
                    res[i] = ints[i];
                }
                break;
            case FLOAT:
                float[] floats = tensor.copyTo(new float[size]);
                for (int i = 0; i < size; i++) {
                    res[i] = floats[i];
                }
                break;
            case INT64:
                long[] longs = tensor.copyTo(new long[size]);
                for (int i = 0; i < size; i++) {
                    res[i] = longs[i];
                }
                break;
            case DOUBLE:
                double[] doubles = tensor.copyTo(new double[size]);
                for (int i = 0; i < size; i++) {
                    res[i] = doubles[i];
                }
                break;
            default:
                throw new UnsupportedOperationException(
                        "Type can't be converted from tensor: " + tensor.dataType().name());
        }
        return res;
    }

    private static int getCapacity(long[] shape) {
        if (shape == null || shape.length == 0) {
            return 0;
        }
        long res = shape[0];
        for (int i = 1; i < shape.length; i++) {
            res *= shape[i];
        }
        Preconditions.checkArgument(
                res >= 0 && res <= Integer.MAX_VALUE, "Invalid shape: " + Arrays.toString(shape));
        return (int) res;
    }
}
