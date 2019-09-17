from flink_ml_workflow.proto.meta_data_pb2 import *
from flink_ml_workflow.vertex.base_vertex import BaseVertex
from enum import Enum


class Schema(object):
    def __init__(self, name_list, type_list):
        self.name_list = name_list
        self.type_list = type_list

    def to_proto(self):
        schema_proto = SchemaProto()
        for i in self.name_list:
            schema_proto.nameList.append(i)
        for i in self.type_list:
            schema_proto.typeList.append(i)
        return schema_proto


class ExampleType(str, Enum):
    EXAMPLE_STREAM = 'EXAMPLE_STREAM'
    EXAMPLE_BATCH = 'EXAMPLE_BATCH'
    EXAMPLE_BOTH = 'EXAMPLE_BOTH'


class Example(BaseVertex):

    def __init__(self,
                 name,
                 example_type: ExampleType,
                 data_schema: Schema,
                 example_format,
                 batch_uri,
                 stream_uri,
                 properties=None):
        super(Example, self).__init__(name, properties)
        self.example_type = example_type
        self.schema = data_schema
        self.example_format = example_format
        self.batch_uri = batch_uri
        self.stream_uri = stream_uri

    def to_proto(self):
        example_proto = ExampleProto()
        example_proto.meta.name = self.name
        for i in self.properties:
            example_proto.meta.properties[i] = self.properties[i]
        if ExampleType.EXAMPLE_STREAM == self.example_type:
            example_proto.supportType = ExampleSupportTypeProto.EXAMPLE_STREAM
        elif ExampleType.EXAMPLE_BATCH == self.example_type:
            example_proto.supportType = ExampleSupportTypeProto.EXAMPLE_BATCH
        else:
            example_proto.supportType = ExampleSupportTypeProto.EXAMPLE_BOTH

        for i in self.schema.name_list:
            example_proto.schema.nameList.append(i)
        for i in self.schema.type_list:
            example_proto.schema.typeList.append(i)
        example_proto.exampleFormat = self.example_format
        example_proto.batchUri = self.batch_uri
        example_proto.streamUri = self.stream_uri
        return example_proto


class TempExample(Example):

    def __init__(self, name, data_schema: Schema):
        super().__init__(name, ExampleType.EXAMPLE_BOTH, data_schema, "ROW", "", "", None)


if __name__ == "__main__":
    schema = Schema(name_list=['a', 'b'], type_list=[DataTypeProto.String, DataTypeProto.String])

    example = Example(name="example",
                      example_type=ExampleType.EXAMPLE_BOTH,
                      data_schema=schema,
                      example_format="CSV",
                      batch_uri="aa",
                      stream_uri="bb",
                      properties={'a': 'a'})

    print(example.to_json())
