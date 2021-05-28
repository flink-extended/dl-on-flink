package com.alibaba.flink.ml.tensorflow.client;

import com.alibaba.flink.ml.cluster.MLConfig;
import com.alibaba.flink.ml.cluster.role.BaseRole;
import com.alibaba.flink.ml.tensorflow.ops.TFJavaInferenceFlatMap;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.common.typeinfo.TypeInformation;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

public class TFConfig extends TFConfigBase {
	public TFConfig(int workerNum, int psNum, Map<String, String> properties, String pythonFile, String funName, String envPath) {
		super(workerNum, psNum, properties, pythonFile, funName, envPath);
	}

	public TFConfig(int workerNum, int psNum, Map<String, String> properties, String[] pythonFiles, String funName, String envPath) {
		super(workerNum, psNum, properties, pythonFiles, funName, envPath);
	}

	@Override
	public FlatMapFunction getInferenceFlatMapFunction(BaseRole role, MLConfig mlConfig, TypeInformation inTypeInfo, TypeInformation outTypeInfo) {
		return new TFJavaInferenceFlatMap(role, mlConfig, inTypeInfo, outTypeInfo);
	}

	@Override
	public TFConfig deepCopy() {
		String[] pyFiles = Arrays.copyOf(this.mlConfig.getPythonFiles(), this.mlConfig.getPythonFiles().length);
		HashMap<String, String> destProperties = new HashMap<>();
		destProperties.putAll(this.getMlConfig().getProperties());
		TFConfig config = new TFConfig(getWorkerNum(), getPsNum(), destProperties, pyFiles,
				String.copyValueOf(getFuncName().toCharArray()),
				this.mlConfig.getEnvPath());
		return config;
	}
}
