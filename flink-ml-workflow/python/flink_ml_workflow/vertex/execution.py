from enum import Enum
from flink_ml_workflow.vertex.example import *
from flink_ml_workflow.vertex.transformer import *


class RunMode(str, Enum):
    STREAM = 'STREAM'
    BATCH = 'BATCH'


class Execution(BaseVertex):
    def __init__(self,
                 name,
                 run_mode: RunMode,
                 transformer_list: list,
                 trainer_list: list,
                 properties: dict = None):
        super(Execution, self).__init__(name, properties)
        self.run_mode = run_mode
        self.transformer_list = transformer_list
        self.trainer_list = trainer_list

    def to_proto(self):
        execution_proto = ExecutionProto()
        execution_proto.meta.name = self.name
        for i in self.properties:
            execution_proto.meta.properties[i] = self.properties[i]

        if self.run_mode == RunMode.STREAM:
            execution_proto.runMode = RunModeProto.STREAM
        else:
            execution_proto.runMode = RunModeProto.BATCH

        for i in self.transformer_list:
            execution_proto.transformers.append(i.to_proto())
        for i in self.trainer_list:
            execution_proto.trains.append(i.to_proto())
        return execution_proto


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

    execution = Execution(name="execution",
                          run_mode=RunMode.STREAM,
                          transformer_list=[transformer1, transformer2],
                          trainer_list=[])

    print(execution.to_json())
