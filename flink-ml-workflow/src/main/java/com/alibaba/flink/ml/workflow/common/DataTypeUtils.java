package com.alibaba.flink.ml.workflow.common;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.common.typeinfo.Types;

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
}
