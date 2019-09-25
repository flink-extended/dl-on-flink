package com.alibaba.flink.ml.workflow.runtime;

import com.alibaba.flink.ml.workflow.ExampleProto;
import com.alibaba.flink.ml.workflow.ExampleRunMode;
import com.alibaba.flink.ml.workflow.ExecutionProto;
import com.alibaba.flink.ml.workflow.TrainerProto;
import com.alibaba.flink.ml.workflow.TransformerProto;
import com.alibaba.flink.ml.workflow.components.ComponentContext;
import com.alibaba.flink.ml.workflow.components.examples.ExampleComponent;
import com.alibaba.flink.ml.workflow.components.examples.ExampleUtils;
import com.alibaba.flink.ml.workflow.components.trainers.TrainerComponent;
import com.alibaba.flink.ml.workflow.components.transformers.TransformerComponent;

import java.util.ArrayList;
import java.util.List;


public class StreamJobParser implements JobParser{
	private List<TransformerProto.Builder> transformerProtoList = new ArrayList<>();

	public boolean canTranslate(TransformerProto.Builder transformerBuilder, ComponentContext context){
		for(ExampleProto.Builder builder: transformerBuilder.getInputExampleListBuilderList()) {
			if(ExampleUtils.isTempTable(builder) && null == context.getTable(builder.getMeta().getName())){
				return false;
			}
		}
		return true;
	}

	@Override
	public void parseJob(ExecutionProto.Builder executionProtoBuilder, ComponentContext context) throws Exception{
		for(TransformerProto.Builder transformerBuilder: executionProtoBuilder.getTransformersBuilderList()){
			for(ExampleProto.Builder builder: transformerBuilder.getInputExampleListBuilderList()) {
				builder.setRunMod(ExampleRunMode.SOURCE);
				ExampleComponent exampleComponent = new ExampleComponent();
				exampleComponent.translate(builder.build(), context);
			}
			for(ExampleProto.Builder builder: transformerBuilder.getOutputExampleListBuilderList()){
				builder.setRunMod(ExampleRunMode.SINK);
				ExampleComponent exampleComponent = new ExampleComponent();
				exampleComponent.translate(builder.build(), context);
			}
		}
		for(TransformerProto.Builder transformerBuilder: executionProtoBuilder.getTransformersBuilderList()){
			transformerProtoList.add(transformerBuilder);
		}
		int size = transformerProtoList.size();
		while (!transformerProtoList.isEmpty()){
			ArrayList<TransformerProto.Builder> temp = new ArrayList<>();

			for(TransformerProto.Builder transformerBuilder: transformerProtoList){
				if(canTranslate(transformerBuilder, context)) {
					TransformerComponent transformerComponent = new TransformerComponent();
					transformerComponent.translate(transformerBuilder.build(), context);
					temp.add(transformerBuilder);
				}
			}
			transformerProtoList.removeAll(temp);
			if(size == transformerProtoList.size()){
				throw new RuntimeException("can not parse to job");
			}
		}
		for(TrainerProto.Builder trainerBuilder : executionProtoBuilder.getTrainersBuilderList()){
			TrainerComponent trainerComponent = new TrainerComponent();
			trainerComponent.translate(trainerBuilder.build(), context);
		}
	}
}
