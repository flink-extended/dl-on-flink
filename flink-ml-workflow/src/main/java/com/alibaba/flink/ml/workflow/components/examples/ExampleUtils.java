package com.alibaba.flink.ml.workflow.components.examples;

import com.alibaba.flink.ml.workflow.ExampleProto;

public class ExampleUtils {

	public static boolean isTempTable(ExampleProto exampleProto){
		if(exampleProto.getExampleFormat().equalsIgnoreCase("Row")){
			return true;
		}else {
			return false;
		}
	}
	public static boolean isTempTable(ExampleProto.Builder exampleProto){
		if(exampleProto.getExampleFormat().equalsIgnoreCase("Row")){
			return true;
		}else {
			return false;
		}
	}
}
