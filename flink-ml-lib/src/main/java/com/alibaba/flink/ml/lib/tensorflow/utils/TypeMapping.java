package com.alibaba.flink.ml.lib.tensorflow.utils;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.scala.typeutils.Types;

import org.tensorflow.framework.DataType;

/**
 * helper function to convert TypeDef to TypeInformation, DataType etc.
 */
public class TypeMapping {

	/**
	 * extract TypeInformation by type names.
	 * @param typeNames TypeDef object String value
	 * @return mapping TypeInformation[]
	 */
	public static TypeInformation[] convertToTypeInformation(String[] typeNames){
		TypeInformation[] typeInformations = new TypeInformation[typeNames.length];
		for(int i = 0; i < typeNames.length; i++){
			TypeDef typeDef = TypeDef.valueOf(typeNames[i]);
			switch (typeDef){
				case INT:{
					typeInformations[i] = Types.INT();
					break;
				}
				case LONG:{
					typeInformations[i] = Types.LONG();
					break;
				}
				case FLOAT:{
					typeInformations[i] = Types.FLOAT();
					break;
				}
				case DOUBLE:{
					typeInformations[i] = Types.DOUBLE();
					break;
				}
				case STRING:{
					typeInformations[i] = Types.STRING();
					break;
				}
				case INT_2:{
					typeInformations[i] = TypeInformation.of(int[].class);
					break;
				}
				case LONG_2:{
					typeInformations[i] = TypeInformation.of(long[].class);
					break;
				}
				case FLOAT_2:{
					typeInformations[i] = TypeInformation.of(float[].class);
					break;
				}
				case DOUBLE_2:{
					typeInformations[i] = TypeInformation.of(double[].class);
					break;
				}
				case STRING_2:{
					typeInformations[i] = TypeInformation.of(String[].class);
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
			if(typeNames[i].startsWith("INT")) {
				dataTypes[i] = DataType.DT_INT32;
			}else if(typeNames[i].startsWith("LONG")){
				dataTypes[i] = DataType.DT_INT64;
			}else if(typeNames[i].startsWith("FLOAT")){
				dataTypes[i] = DataType.DT_FLOAT;
			}else if(typeNames[i].startsWith("DOUBLE")){
				dataTypes[i] = DataType.DT_DOUBLE;
			}else if(typeNames[i].startsWith("STRING")){
				dataTypes[i] = DataType.DT_STRING;
			}else{
				throw new RuntimeException(typeNames[i] + " not support for output type!");
			}
		}
		return dataTypes;
	}

	/**
	 * calculate TypeDef object mapping Tensor dimension
	 * @param typeNames TypeDef object String value
	 * @return dimensions
	 */
	public static int[] getDimsByDataTypes(String[] typeNames){
		int[] dims = new int[typeNames.length];
		for(int i = 0; i < typeNames.length; i++){
			if(typeNames[i].endsWith("_2")) {
				dims[i] = 2;
			} else{
				dims[i] = 1;
			}
		}
		return dims;
	}
}
