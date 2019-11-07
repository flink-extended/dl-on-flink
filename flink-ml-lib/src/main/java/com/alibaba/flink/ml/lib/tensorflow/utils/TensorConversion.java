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

package com.alibaba.flink.ml.lib.tensorflow.utils;

import com.google.common.base.Preconditions;
import org.tensorflow.Tensor;
import org.tensorflow.Tensors;
import org.tensorflow.framework.TensorInfo;


// TODO: support more kinds of tensors

/**
 * a util function: transformation between tensorflow tensor and java object.
 */
public class TensorConversion {

	private TensorConversion() {
	}

	/**
	 * convert java objects to tensorflow tensor.
	 * @param object given java objects.
	 * @param tensorInfo target tensor type information.
	 * @return result tensorflow tensor.
	 */
	public static Tensor<?> toTensor(Object object, TensorInfo tensorInfo, int dimCount) {

		switch (tensorInfo.getDtype()) {
			case DT_INT32: {
				switch (dimCount){
					case 1:{
						return Tensors.create((int[])object);
					}
					case 2:{
						return Tensors.create((int[][])object);
					}
					case 3:{
						return Tensors.create((int[][][])object);
					}
					case 4:{
						return Tensors.create((int[][][][])object);
					}
					case 5:{
						return Tensors.create((int[][][][][])object);
					}
					case 6:{
						return Tensors.create((int[][][][][][])object);
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(dimCount));
				}
			}
			case DT_INT64: {
				switch (dimCount){
					case 1:{
						return Tensors.create((long[])object);
					}
					case 2:{
						return Tensors.create((long[][])object);
					}
					case 3:{
						return Tensors.create((long[][][])object);
					}
					case 4:{
						return Tensors.create((long[][][][])object);
					}
					case 5:{
						return Tensors.create((long[][][][][])object);
					}
					case 6:{
						return Tensors.create((long[][][][][][])object);
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(dimCount));
				}
			}
			case DT_FLOAT: {
				switch (dimCount){
					case 1:{
						return Tensors.create((float[])object);
					}
					case 2:{
						return Tensors.create((float[][])object);
					}
					case 3:{
						return Tensors.create((float[][][])object);
					}
					case 4:{
						return Tensors.create((float[][][][])object);
					}
					case 5:{
						return Tensors.create((float[][][][][])object);
					}
					case 6:{
						return Tensors.create((float[][][][][][])object);
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(dimCount));
				}
			}
			case DT_DOUBLE: {
				switch (dimCount){
					case 1:{
						return Tensors.create((double[])object);
					}
					case 2:{
						return Tensors.create((double[][])object);
					}
					case 3:{
						return Tensors.create((double[][][])object);
					}
					case 4:{
						return Tensors.create((double[][][][])object);
					}
					case 5:{
						return Tensors.create((double[][][][][])object);
					}
					case 6:{
						return Tensors.create((double[][][][][][])object);
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(dimCount));
				}
			}
			case DT_STRING: {
				switch (dimCount){
					case 1:{
						String[] stringArray = (String[])object;
						byte[][] temp = new byte[stringArray.length][];
						for(int i = 0; i < stringArray.length; i++){
							temp[i] = stringArray[i].getBytes();
						}
						return Tensors.create(temp);
					}
					case 2:{
						String[][] stringArray = (String[][])object;
						int len1 = stringArray.length;
						int len2 = stringArray[0].length;
						byte[][][] temp = new byte[len1][len2][];
						for(int i = 0; i < len1; i++){
							for(int j = 0; j < len2; j++) {
								temp[i][j] = stringArray[i][j].getBytes();
							}
						}
						return Tensors.create(temp);
					}
					case 3:{
						String[][][] stringArray = (String[][][])object;
						int len1 = stringArray.length;
						int len2 = stringArray[0].length;
						int len3 = stringArray[0][0].length;
						byte[][][][] temp = new byte[len1][len2][len3][];
						for(int i = 0; i < len1; i++){
							for(int j = 0; j < len2; j++) {
								for(int k = 0; k < len3; k++) {
									temp[i][j][k] = stringArray[i][j][k].getBytes();
								}
							}
						}
						return Tensors.create(temp);
					}
					case 4:{
						String[][][][] stringArray = (String[][][][])object;
						int len1 = stringArray.length;
						int len2 = stringArray[0].length;
						int len3 = stringArray[0][0].length;
						int len4 = stringArray[0][0][0].length;
						byte[][][][][] temp = new byte[len1][len2][len3][len4][];
						for(int i = 0; i < len1; i++){
							for(int j = 0; j < len2; j++) {
								for(int k = 0; k < len3; k++) {
									for(int m = 0; m < len4; m++) {
										temp[i][j][k][m] = stringArray[i][j][k][m].getBytes();
									}
								}
							}
						}
						return Tensors.create(temp);
					}
					case 5:{
						String[][][][][] stringArray = (String[][][][][])object;
						int len1 = stringArray.length;
						int len2 = stringArray[0].length;
						int len3 = stringArray[0][0].length;
						int len4 = stringArray[0][0][0].length;
						int len5 = stringArray[0][0][0][0].length;

						byte[][][][][][] temp = new byte[len1][len2][len3][len4][len5][];
						for(int i = 0; i < len1; i++){
							for(int j = 0; j < len2; j++) {
								for(int k = 0; k < len3; k++) {
									for(int m = 0; m < len4; m++) {
										for(int n = 0; n < len5; n++) {
											temp[i][j][k][m][n] = stringArray[i][j][k][m][n].getBytes();
										}
									}
								}
							}
						}
						return Tensors.create(temp);
					}
					default:
						throw new UnsupportedOperationException(
								"dim count can't supported: " + String.valueOf(dimCount));
				}
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
	public static Object fromTensor(Tensor<?> tensor) {
		Preconditions.checkArgument(tensor.numDimensions() <= 5,
				"Can only convert tensors with shape less than 2 current " + tensor.numDimensions());
		final int dimCount = tensor.numDimensions();
		final int num = tensor.numElements();
		switch (tensor.dataType()) {
			case INT32: {
				switch (dimCount){
					case 1:{
						final int len1 = (int) tensor.shape()[0];
						return tensor.copyTo(new int[len1]);
					}
					case 2:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						return tensor.copyTo(new int[len1][len2]);
					}
					case 3:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						return tensor.copyTo(new int[len1][len2][len3]);
					}
					case 4:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						final int len4 = (int) tensor.shape()[3];
						return tensor.copyTo(new int[len1][len2][len3][len4]);
					}
					case 5:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						final int len4 = (int) tensor.shape()[3];
						final int len5 = (int) tensor.shape()[4];
						return tensor.copyTo(new int[len1][len2][len3][len4][len5]);
					}
				}
			}
			case FLOAT: {
				switch (dimCount){
					case 1:{
						final int len1 = (int) tensor.shape()[0];
						return tensor.copyTo(new float[len1]);
					}
					case 2:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						return tensor.copyTo(new float[len1][len2]);
					}
					case 3:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						return tensor.copyTo(new float[len1][len2][len3]);
					}
					case 4:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						final int len4 = (int) tensor.shape()[3];
						return tensor.copyTo(new float[len1][len2][len3][len4]);
					}
					case 5:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						final int len4 = (int) tensor.shape()[3];
						final int len5 = (int) tensor.shape()[4];
						return tensor.copyTo(new float[len1][len2][len3][len4][len5]);
					}
				}
			}
			case INT64: {
				switch (dimCount){
					case 1:{
						final int len1 = (int) tensor.shape()[0];
						return tensor.copyTo(new long[len1]);
					}
					case 2:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						return tensor.copyTo(new long[len1][len2]);
					}
					case 3:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						return tensor.copyTo(new long[len1][len2][len3]);
					}
					case 4:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						final int len4 = (int) tensor.shape()[3];
						return tensor.copyTo(new long[len1][len2][len3][len4]);
					}
					case 5:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						final int len4 = (int) tensor.shape()[3];
						final int len5 = (int) tensor.shape()[4];
						return tensor.copyTo(new long[len1][len2][len3][len4][len5]);
					}
				}
			}
			case DOUBLE: {
				switch (dimCount){
					case 1:{
						final int len1 = (int) tensor.shape()[0];
						return tensor.copyTo(new double[len1]);
					}
					case 2:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						return tensor.copyTo(new double[len1][len2]);
					}
					case 3:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						return tensor.copyTo(new double[len1][len2][len3]);
					}
					case 4:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						final int len4 = (int) tensor.shape()[3];
						return tensor.copyTo(new double[len1][len2][len3][len4]);
					}
					case 5:{
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						final int len4 = (int) tensor.shape()[3];
						final int len5 = (int) tensor.shape()[4];
						return tensor.copyTo(new double[len1][len2][len3][len4][len5]);
					}
				}
			}
			case STRING:{
				switch (dimCount) {
					case 1: {
						final int len1 = (int) tensor.shape()[0];
						byte[][] resultBytes = tensor.copyTo(new byte[len1][]);
						String[] results = new String[len1];
						for (int i = 0; i < len1; i++){
							results[i] = new String(resultBytes[i]);
						}
						return results;
					}
					case 2: {
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						byte[][][] resultBytes = tensor.copyTo(new byte[len1][len2][]);
						String[][] results = new String[len1][len2];
						for (int i = 0; i < len1; i++) {
							for (int j = 0; j < len2; j++) {
								results[i][j] = new String(resultBytes[i][j]);
							}
						}
						return results;
					}
					case 3: {
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						byte[][][][] resultBytes = tensor.copyTo(new byte[len1][len2][len3][]);
						String[][][] results = new String[len1][len2][len3];
						for (int i = 0; i < len1; i++) {
							for (int j = 0; j < len2; j++) {
								for (int k = 0; k < len3; k++) {
									results[i][j][k] = new String(resultBytes[i][j][k]);
								}
							}
						}
						return results;
					}
					case 4: {
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						final int len4 = (int) tensor.shape()[3];
						byte[][][][][] resultBytes = tensor.copyTo(new byte[len1][len2][len3][len4][]);
						String[][][][] results = new String[len1][len2][len3][len4];
						for (int i = 0; i < len1; i++) {
							for (int j = 0; j < len2; j++) {
								for (int k = 0; k < len3; k++) {
									for (int m = 0; m < len4; m++) {
										results[i][j][k][m] = new String(resultBytes[i][j][k][m]);
									}
								}
							}
						}
						return results;
					}
					case 5: {
						final int len1 = (int) tensor.shape()[0];
						final int len2 = (int) tensor.shape()[1];
						final int len3 = (int) tensor.shape()[2];
						final int len4 = (int) tensor.shape()[3];
						final int len5 = (int) tensor.shape()[4];
						byte[][][][][][] resultBytes = tensor.copyTo(new byte[len1][len2][len3][len4][len5][]);
						String[][][][][] results = new String[len1][len2][len3][len4][len5];
						for (int i = 0; i < len1; i++) {
							for (int j = 0; j < len2; j++) {
								for (int k = 0; k < len3; k++) {
									for (int m = 0; m < len4; m++) {
										for (int n = 0; n < len5; n++) {
											results[i][j][k][m][n] = new String(resultBytes[i][j][k][m][n]);
										}
									}
								}
							}
						}
						return results;
					}
				}
			}

			default:
				throw new UnsupportedOperationException(
						"Type can't be converted from tensor : " + tensor.dataType().name());
		}
	}

}