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

package com.alibaba.flink.ml.tensorflow.util;

import com.google.common.base.Preconditions;
import org.tensorflow.Tensor;
import org.tensorflow.ndarray.Shape;
import org.tensorflow.ndarray.buffer.DataBuffers;
import org.tensorflow.proto.framework.TensorInfo;
import org.tensorflow.types.TFloat32;
import org.tensorflow.types.TFloat64;
import org.tensorflow.types.TInt32;
import org.tensorflow.types.TInt64;

import java.nio.DoubleBuffer;
import java.nio.FloatBuffer;
import java.nio.IntBuffer;
import java.nio.LongBuffer;
import java.util.Arrays;

// TODO: support more kinds of tensors

/**
 * a util function: transformation between tensorflow tensor and java object.
 */
public class TFTensorConversion {

	private TFTensorConversion() {
	}

	/**
	 * convert java objects to tensorflow tensor.
	 * @param objects given java objects.
	 * @param tensorInfo target tensor type information.
	 * @return result tensorflow tensor.
	 */
	public static Tensor<?> toTensor(Object[] objects, TensorInfo tensorInfo) {
		switch (tensorInfo.getDtype()) {
			case DT_INT8:
			case DT_INT16:
			case DT_INT32: {
				long[] shape = new long[] { objects.length, ((int[]) objects[0]).length };
				IntBuffer intBuffer = IntBuffer.allocate(getCapacity(shape));
				for (Object obj : objects) {
					intBuffer.put((int[]) obj);
				}
				intBuffer.flip();
				return TInt32.tensorOf(Shape.of(shape), DataBuffers.of(intBuffer));
			}
			case DT_INT64: {
				long[] shape = new long[] { objects.length, ((long[]) objects[0]).length };
				LongBuffer longBuffer = LongBuffer.allocate(getCapacity(shape));
				for (Object obj : objects) {
					longBuffer.put((long[]) obj);
				}
				longBuffer.flip();
				return TInt64.tensorOf(Shape.of(shape), DataBuffers.of(longBuffer));
			}
			case DT_FLOAT: {
				long[] shape = new long[] { objects.length, ((float[]) objects[0]).length };
				FloatBuffer floatBuffer = FloatBuffer.allocate(getCapacity(shape));
				for (Object obj : objects) {
					floatBuffer.put((float[]) obj);
				}
				floatBuffer.flip();
				return TFloat32.tensorOf(Shape.of(shape), DataBuffers.of(floatBuffer));
			}
			case DT_DOUBLE: {
				long[] shape = new long[] { objects.length, ((double[]) objects[0]).length };
				DoubleBuffer doubleBuffer = DoubleBuffer.allocate(getCapacity(shape));
				for (Object obj : objects) {
					doubleBuffer.put((double[]) obj);
				}
				doubleBuffer.flip();
				return TFloat64.tensorOf(Shape.of(shape), DataBuffers.of(doubleBuffer));
			}
			default:
				throw new UnsupportedOperationException(
						"Type can't be converted to tensor: " + tensorInfo.getDtype().name());
		}
	}

	/**
	 * convert tensorflow tensor to java objects.
	 * @param tensor given tensorflow tensor.
	 * @return java objects corresponded to given tensor.
	 */
	public static Object[] fromTensor(Tensor<?> tensor) {
		Preconditions.checkArgument(tensor.shape().numDimensions() == 1, "Can only convert tensors with shape long[]");
		final int size = (int) tensor.shape().size(0);
		Object[] res = new Object[size];
		if (TInt32.DTYPE.equals(tensor.dataType())) {
			int[] ints = new int[size];
			tensor.rawData().asInts().read(ints);
			for (int i = 0; i < size; i++) {
				res[i] = ints[i];
			}
		} else if (TFloat32.DTYPE.equals(tensor.dataType())) {
			float[] floats = new float[size];
			tensor.rawData().asFloats().read(floats);
			for (int i = 0; i < size; i++) {
				res[i] = floats[i];
			}
		} else if (TInt64.DTYPE.equals(tensor.dataType())) {
			long[] longs = new long[size];
			tensor.rawData().asLongs().read(longs);
			for (int i = 0; i < size; i++) {
				res[i] = longs[i];
			}
		} else if (TFloat64.DTYPE.equals(tensor.dataType())) {
			double[] doubles = new double[size];
			tensor.rawData().asDoubles().read(doubles);
			for (int i = 0; i < size; i++) {
				res[i] = doubles[i];
			}
		} else {
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
		Preconditions.checkArgument(res >= 0 && res <= Integer.MAX_VALUE, "Invalid shape: " + Arrays.toString(shape));
		return (int) res;
	}
}
