from enum import Enum
from flink_ml_workflow.vertex.base_vertex import *
from flink_ml_workflow.vertex.transformer import *
from flink_ml_workflow.vertex.execution import *


class WorkFlow(BaseVertex):
    def __init__(self,
                 name,
                 run_mode: RunMode,
                 execution_list: list,
                 dependencies: dict = None,
                 properties: dict = None):
        super(WorkFlow, self).__init__(name, properties)
        self.run_mode = run_mode
        self.execution_list = execution_list
        self.dependencies = dependencies
        if dependencies is None:
            self.dependencies = {}
        self.parse_dependencies()

    def parse_dependencies(self):
        input_map = {}
        output_map = {}
        for execution in self.execution_list:
            for transformer in execution.transformer_list:
                for example in transformer.input_example_list:
                    input_map[example.name] = execution.name
            for trainer in execution.trainer_list:
                input_map[trainer.input_example.name] = execution.name

        for execution in self.execution_list:
            for transformer in execution.transformer_list:
                for example in transformer.output_example_list:
                    output_map[example.name] = execution.name

        for input_i in input_map:
            if input_i in output_map:
                self.dependencies[input_map[input_i]] = output_map[input_i]

    def to_proto(self):
        workflow_proto = WorkFlowProto()
        return self.set_proto(workflow_proto)

    def set_proto(self, workflow_proto):
        workflow_proto.meta.name = self.name
        for i in self.properties:
            workflow_proto.meta.properties[i] = self.properties[i]

        if self.run_mode == RunMode.STREAM:
            workflow_proto.runMode = RunModeProto.STREAM
        else:
            workflow_proto.runMode = RunModeProto.BATCH

        for i in self.execution_list:
            workflow_proto.executions.append(i.to_proto())
        if self.dependencies is not None:
            for i in self.dependencies:
                workflow_proto.dependencies[i] = self.dependencies[i]

        return workflow_proto


if __name__ == "__main__":
    input_schema = Schema(name_list=['a', 'b', 'c', 'd'], type_list=[DataTypeProto.String, DataTypeProto.String,
                                                                     DataTypeProto.String, DataTypeProto.String])

    input_example = Example(name="input_example",
                            example_type=ExampleType.EXAMPLE_BATCH,
                            data_schema=input_schema,
                            example_format="CSV",
                            batch_uri="aa",
                            stream_uri="bb",
                            properties={'a': 'a'})

    output_schema1 = Schema(name_list=['a', 'b', 'c'], type_list=[DataTypeProto.String, DataTypeProto.String,
                                                                  DataTypeProto.String])

    output_example1 = TempExample(name="output1", data_schema=output_schema1)

    output_schema2 = Schema(name_list=['a', 'b'], type_list=[DataTypeProto.String, DataTypeProto.String])

    transformer1 = Transformer(name='transformer',
                               transformer_type=TransformerType.JAVA,
                               input_example_list=[input_example],
                               output_example_list=[output_example1],
                               jar_location="",
                               transformer_class_name="com.alibaba.flink.ml.workflow.runtime.TestTransformer1")

    output_example2 = Example(name="output_example",
                              example_type=ExampleType.EXAMPLE_BATCH,
                              data_schema=output_schema2,
                              example_format="CSV",
                              batch_uri="aa",
                              stream_uri="bb",
                              properties={'a': 'a'})

    transformer2 = Transformer(name='transformer',
                               transformer_type=TransformerType.JAVA,
                               input_example_list=[output_example1],
                               output_example_list=[output_example2],
                               jar_location="",
                               transformer_class_name="com.alibaba.flink.ml.workflow.runtime.TestTransformer1")

    execution1 = Execution(name="execution1",
                           run_mode=RunMode.STREAM,
                           transformer_list=[transformer1],
                           trainer_list=[])

    execution2 = Execution(name="execution2",
                           run_mode=RunMode.STREAM,
                           transformer_list=[transformer2],
                           trainer_list=[])

    workflow = WorkFlow(name="workflow",
                        run_mode=RunMode.BATCH,
                        execution_list=[execution1, execution2])

    print(workflow.to_json())
