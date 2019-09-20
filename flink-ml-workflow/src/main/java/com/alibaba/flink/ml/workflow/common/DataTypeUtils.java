package com.alibaba.flink.ml.workflow.common;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.common.typeinfo.Types;

import com.alibaba.flink.ml.operator.util.DataTypes;
import com.alibaba.flink.ml.workflow.DataTypeProto;

public class DataTypeUtils {

	public static TypeInformation toTypeInformation(DataTypeProto dataTypeProto){
		switch (dataTypeProto){
			case Bytes:
				return TypeInformation.of(byte[].class);
			case Int32:
				return Types.INT;
			case Int64:
				return Types.LONG;
			case String:
				return Types.STRING;
			case Float32:
				return Types.FLOAT;
			case Float64:
				return Types.DOUBLE;
			case BytesArray:
				return Types.OBJECT_ARRAY(TypeInformation.of(byte[].class));
			case Int32Array:
				return Types.OBJECT_ARRAY(Types.INT);
			case Int64Array:
				return Types.OBJECT_ARRAY(Types.LONG);
			case Float32Array:
				return Types.OBJECT_ARRAY(Types.FLOAT);
			case Float64Array:
				return Types.OBJECT_ARRAY(Types.DOUBLE);
			case StringArray:
				return Types.OBJECT_ARRAY(Types.STRING);
			case UNRECOGNIZED:
				throw new RuntimeException("not support UNRECOGNIZED");
		}
		throw new RuntimeException("not support:" + dataTypeProto.toString());
	}

	public static DataTypes toDataTypes(DataTypeProto dataTypeProto){
		switch (dataTypeProto){
			case Bytes:
				return DataTypes.STRING;
			case Int32:
				return DataTypes.INT_32;
			case Int64:
				return DataTypes.INT_64;
			case String:
				return DataTypes.STRING;
			case Float32:
				return DataTypes.FLOAT_32;
			case Float64:
				return DataTypes.FLOAT_64;
			case BytesArray:
				return DataTypes.STRING;
			case Int32Array:
				return DataTypes.INT_32;
			case Int64Array:
				return DataTypes.INT_64_ARRAY;
			case Float32Array:
				return DataTypes.FLOAT_32_ARRAY;
			case Float64Array:
				throw new RuntimeException("not support UNRECOGNIZED");
			case StringArray:
				throw new RuntimeException("not support UNRECOGNIZED");
			case UNRECOGNIZED:
				throw new RuntimeException("not support UNRECOGNIZED");
		}
		throw new RuntimeException("not support:" + dataTypeProto.toString());
	}
}
