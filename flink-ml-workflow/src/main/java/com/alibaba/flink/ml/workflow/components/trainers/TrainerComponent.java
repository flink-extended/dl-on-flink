package com.alibaba.flink.ml.workflow.components.trainers;

import org.apache.flink.table.api.Table;
import org.apache.flink.types.Row;

import com.alibaba.flink.ml.operator.coding.RowCSVCoding;
import com.alibaba.flink.ml.operator.util.DataTypes;
import com.alibaba.flink.ml.tensorflow.client.TFConfig;
import com.alibaba.flink.ml.tensorflow.client.TFUtils;
import com.alibaba.flink.ml.tensorflow.coding.ExampleCoding;
import com.alibaba.flink.ml.tensorflow.coding.ExampleCodingConfig;
import com.alibaba.flink.ml.tensorflow.util.TFConstants;
import com.alibaba.flink.ml.util.MLConstants;
import com.alibaba.flink.ml.workflow.SchemaProto;
import com.alibaba.flink.ml.workflow.TrainerProto;
import com.alibaba.flink.ml.workflow.common.DataTypeUtils;
import com.alibaba.flink.ml.workflow.common.WorkflowConstants;
import com.alibaba.flink.ml.workflow.components.Component;
import com.alibaba.flink.ml.workflow.components.ComponentContext;
import com.google.protobuf.Message;

import java.util.HashMap;
import java.util.Map;

public class TrainerComponent implements Component {

	@Override
	public void translate(Message message, ComponentContext context) throws Exception {
		TrainerProto trainerProto = (TrainerProto)message;
		String tableName = trainerProto.getInputExample().getMeta().getName();
		String script = trainerProto.getPyMainScript();
		int scriptCount = trainerProto.getPyScriptsCount();
		String[] pyScripts = new String[scriptCount + 1];
		pyScripts[0] = script;
		for (int i = 1; i < scriptCount; i++) {
			pyScripts[i] = trainerProto.getPyScripts(i);
		}
		String entryFunc = trainerProto.getPyMainFuncName();
		int workerNum = Integer.valueOf(trainerProto.getMeta().getPropertiesOrDefault(WorkflowConstants.WORKER_NUM, "1"));
		int psNum = Integer.valueOf(trainerProto.getMeta().getPropertiesOrDefault(WorkflowConstants.PS_NUM, "1"));
		Map<String, String> properties = new HashMap<>(trainerProto.getMeta().getPropertiesMap());
		String envPath = null;
		if (properties.containsKey(WorkflowConstants.VIRTUAL_ENV)) {
			envPath = properties.get(WorkflowConstants.VIRTUAL_ENV);
		}
		String checkpointPath = trainerProto.getOutputModelVersion().getModelUri();
		properties.put(WorkflowConstants.CHECKPOINT_DIR, checkpointPath);
		TFConfig tfConfig = new TFConfig(workerNum, psNum, properties, pyScripts, entryFunc, envPath);
		if(context.isStream()) {
			Table inputTable = context.getTable(tableName);
			if (properties.containsKey(WorkflowConstants.CODE_TYPE) && "EXAMPLE"
					.equalsIgnoreCase(properties.get(WorkflowConstants.CODE_TYPE))) {
				setExampleCodingRowType(tfConfig, trainerProto);
			} else {
				setCSVCodingRowType(tfConfig, trainerProto);
			}
			TFUtils.train(context.getStreamEnv(), context.getTableEnv(), inputTable, tfConfig, null);
		}else {
			tfConfig.addProperty(WorkflowConstants.INPUT_DATA_URI, trainerProto.getInputExample().getBatchUri());
			TFUtils.train(context.getStreamEnv(), context.getTableEnv(), null, tfConfig, null);
		}
	}

	public static void setExampleCodingRowType(TFConfig config, TrainerProto trainerProto) {
		SchemaProto schemaProto = trainerProto.getInputExample().getSchema();
		int fieldCount = schemaProto.getNameListCount();
		String[] names = new String[fieldCount];
		DataTypes[] types = new DataTypes[fieldCount];
		for(int i = 0; i < fieldCount; i++){
			names[i] = schemaProto.getNameList(i);
			types[i] = DataTypeUtils.toDataTypes(schemaProto.getTypeList(i));
		}
		String str = ExampleCodingConfig.createExampleConfigStr(names, types,
				ExampleCodingConfig.ObjectType.ROW, Row.class);
		config.getProperties().put(TFConstants.INPUT_TF_EXAMPLE_CONFIG, str);
		config.getProperties().put(TFConstants.OUTPUT_TF_EXAMPLE_CONFIG, str);
		config.getProperties().put(MLConstants.ENCODING_CLASS, ExampleCoding.class.getCanonicalName());
		config.getProperties().put(MLConstants.DECODING_CLASS, ExampleCoding.class.getCanonicalName());
	}

	public static void setCSVCodingRowType(TFConfig config, TrainerProto trainerProto){
		config.getProperties().put(MLConstants.ENCODING_CLASS, RowCSVCoding.class.getCanonicalName());
		config.getProperties().put(MLConstants.DECODING_CLASS, RowCSVCoding.class.getCanonicalName());
		StringBuilder inputSb = new StringBuilder();
		SchemaProto schemaProto = trainerProto.getInputExample().getSchema();
		int fieldCount = schemaProto.getNameListCount();
		for(int i = 0; i < fieldCount; i++){
			DataTypes types = DataTypeUtils.toDataTypes(schemaProto.getTypeList(i));
			inputSb.append(types.name()).append(",");
		}
		inputSb.deleteCharAt(inputSb.length()-1);
		config.getProperties().put(RowCSVCoding.ENCODE_TYPES, inputSb.toString());
		config.getProperties().put(RowCSVCoding.DECODE_TYPES, inputSb.toString());
	}
}
