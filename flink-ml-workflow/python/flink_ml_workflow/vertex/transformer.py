from flink_ml_workflow.proto.meta_data_pb2 import *
from flink_ml_workflow.vertex.base_vertex import BaseVertex
from enum import Enum
from flink_ml_workflow.vertex.example import *


class TransformerType(str, Enum):
    JAVA = 'JAVA'
    PYTHON = 'PYTHON'


class Transformer(BaseVertex):
    def __init__(self,
                 name,
                 transformer_type: TransformerType,
                 input_example_list: list,
                 output_example_list: list,
                 jar_location='',
                 transformer_class_name='',
                 py_script='',
                 py_func='',
                 properties: dict = None):
        super(Transformer, self).__init__(name, properties)
        self.transformer_type = transformer_type
        self.input_example_list = input_example_list
        self.output_example_list = output_example_list
        self.jar_location = jar_location
        self.transformer_class_name = transformer_class_name
        self.py_script = py_script
        self.py_func = py_func

    def to_proto(self):
        transformer_proto = TransformerProto()
        transformer_proto.meta.name = self.name
        for i in self.properties:
            transformer_proto.meta.properties[i] = self.properties[i]

        if self.transformer_type == TransformerType.JAVA:
            transformer_proto.type = TransformerTypeProto.JAVA
        else:
            transformer_proto.type = TransformerTypeProto.PYTHON

        for i in self.input_example_list:
            transformer_proto.inputExampleList.append(i.to_proto())
        for i in self.output_example_list:
            transformer_proto.outputExampleList.append(i.to_proto())
        transformer_proto.jarLocation = self.jar_location
        transformer_proto.transformerClassName = self.transformer_class_name
        transformer_proto.pyScript = self.py_script
        transformer_proto.pyFunc = self.py_func
        return transformer_proto


if __name__ == "__main__":
    input_schema = Schema(name_list=['a', 'b', 'c', 'd'], type_list=[DataTypeProto.String, DataTypeProto.String,
                                                                     DataTypeProto.String, DataTypeProto.String])

    input_example = Example(name="input_example",
                            example_type=ExampleSupportTypeProto.EXAMPLE_BATCH,
                            data_schema=input_schema,
                            example_format="CSV",
                            batch_uri="aa",
                            stream_uri="bb",
                            properties={'a': 'a'})

    output_schema = Schema(name_list=['a', 'b'], type_list=[DataTypeProto.String, DataTypeProto.String])

    output_example = Example(name="output_example",
                             example_type=ExampleSupportTypeProto.EXAMPLE_BATCH,
                             data_schema=output_schema,
                             example_format="CSV",
                             batch_uri="aa",
                             stream_uri="bb",
                             properties={'a': 'a'})

    transformer = Transformer(name='transformer',
                              transformer_type=TransformerType.JAVA,
                              input_example_list=[input_example],
                              output_example_list=[output_example],
                              jar_location="",
                              transformer_class_name="aaa")

    print(transformer.to_json())
