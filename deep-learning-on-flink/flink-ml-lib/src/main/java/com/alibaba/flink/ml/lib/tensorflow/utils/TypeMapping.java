package com.alibaba.flink.ml.lib.tensorflow.utils;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.scala.typeutils.Types;

import org.tensorflow.proto.framework.DataType;

/**
 * helper function to convert TypeDef to TypeInformation, DataType etc.
 */
public class TypeMapping {

	/**
	 * extract TypeInformation by type names.
	 * @param typeNames TypeDef object String value
	 * @return mapping TypeInformation[]
	 */
	public static TypeInformation[] convertToTypeInformation(String[] typeNames, int[] ranks){
		TypeInformation[] typeInformations = new TypeInformation[typeNames.length];
		for(int i = 0; i < typeNames.length; i++){
			DataType dataType = DataType.valueOf(typeNames[i]);
			switch (dataType){
				case DT_INT32:{
					switch (ranks[i]){
						case 0: {
							typeInformations[i] = Types.INT();
							break;
						}
						case 1: {
							typeInformations[i] = TypeInformation.of(int[].class);
							break;
						}
						case 2: {
							typeInformations[i] = TypeInformation.of(int[][].class);
							break;
						}
						case 3: {
							typeInformations[i] = TypeInformation.of(int[][][].class);
							break;
						}
						case 4: {
							typeInformations[i] = TypeInformation.of(int[][][][].class);
							break;
						}
						case 5: {
							typeInformations[i] = TypeInformation.of(int[][][][][].class);
							break;
						}
						case 6: {
							typeInformations[i] = TypeInformation.of(int[][][][][][].class);
							break;
						}
						default:
							throw new RuntimeException(String.valueOf(ranks[i]) + " not support for rank!");

					}
					break;
				}
				case DT_INT64:{
					switch (ranks[i]){
						case 0: {
							typeInformations[i] = Types.LONG();
							break;
						}
						case 1: {
							typeInformations[i] = TypeInformation.of(long[].class);
							break;
						}
						case 2: {
							typeInformations[i] = TypeInformation.of(long[][].class);
							break;
						}
						case 3: {
							typeInformations[i] = TypeInformation.of(long[][][].class);
							break;
						}
						case 4: {
							typeInformations[i] = TypeInformation.of(long[][][][].class);
							break;
						}
						case 5: {
							typeInformations[i] = TypeInformation.of(long[][][][][].class);
							break;
						}
						case 6: {
							typeInformations[i] = TypeInformation.of(long[][][][][][].class);
							break;
						}
						default:
							throw new RuntimeException(String.valueOf(ranks[i]) + " not support for rank!");

					}
					break;
				}
				case DT_FLOAT:{
					switch (ranks[i]){
						case 0: {
							typeInformations[i] = Types.FLOAT();
							break;
						}
						case 1: {
							typeInformations[i] = TypeInformation.of(float[].class);
							break;
						}
						case 2: {
							typeInformations[i] = TypeInformation.of(float[][].class);
							break;
						}
						case 3: {
							typeInformations[i] = TypeInformation.of(float[][][].class);
							break;
						}
						case 4: {
							typeInformations[i] = TypeInformation.of(float[][][][].class);
							break;
						}
						case 5: {
							typeInformations[i] = TypeInformation.of(float[][][][][].class);
							break;
						}
						case 6: {
							typeInformations[i] = TypeInformation.of(float[][][][][][].class);
							break;
						}
						default:
							throw new RuntimeException(String.valueOf(ranks[i]) + " not support for rank!");

					}
					break;
				}
				case DT_DOUBLE:{
					switch (ranks[i]){
						case 0: {
							typeInformations[i] = Types.DOUBLE();
							break;
						}
						case 1: {
							typeInformations[i] = TypeInformation.of(double[].class);
							break;
						}
						case 2: {
							typeInformations[i] = TypeInformation.of(double[][].class);
							break;
						}
						case 3: {
							typeInformations[i] = TypeInformation.of(double[][][].class);
							break;
						}
						case 4: {
							typeInformations[i] = TypeInformation.of(double[][][][].class);
							break;
						}
						case 5: {
							typeInformations[i] = TypeInformation.of(double[][][][][].class);
							break;
						}
						case 6: {
							typeInformations[i] = TypeInformation.of(double[][][][][][].class);
							break;
						}
						default:
							throw new RuntimeException(String.valueOf(ranks[i]) + " not support for rank!");
					}
					break;
				}
				case DT_STRING:{
					switch (ranks[i]){
						case 0: {
							typeInformations[i] = Types.STRING();
							break;
						}
						case 1: {
							typeInformations[i] = TypeInformation.of(String[].class);
							break;
						}
						case 2: {
							typeInformations[i] = TypeInformation.of(String[][].class);
							break;
						}
						case 3: {
							typeInformations[i] = TypeInformation.of(String[][][].class);
							break;
						}
						case 4: {
							typeInformations[i] = TypeInformation.of(String[][][][].class);
							break;
						}
						case 5: {
							typeInformations[i] = TypeInformation.of(String[][][][][].class);
							break;
						}
						default:
							throw new RuntimeException(String.valueOf(ranks[i]) + " not support for rank!");
					}
					break;
				}
				default:
					throw new RuntimeException(typeNames[i] + " not support for output type!");
			}
		}
		return typeInformations;
	}

	/**
	 * get tensorflow DataType by TypeDef object string
	 * @param typeNames TypeDef object String value
	 * @return DataType[]
	 */
	public static DataType[] convertToDataTypes(String[] typeNames){
		DataType[] dataTypes = new DataType[typeNames.length];
		for(int i = 0; i < typeNames.length; i++){
			DataType type = DataType.valueOf(typeNames[i]);
			switch (type){
				case DT_INT32:
				case DT_INT64:
				case DT_FLOAT:
				case DT_DOUBLE:
				case DT_STRING:
					dataTypes[i] = type;
					break;
				default:
					throw new RuntimeException(typeNames[i] + " not support for output type!");
			}
		}
		return dataTypes;
	}
}
