from flink_ml_workflow.vertex.execution import *
from flink_ml_workflow.runtime.job import *
from flink_ml_workflow.vertex.model import *
from flink_ml_workflow.vertex.trainer import *



def transform_job_test():
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


def train_job_test():
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

    transformer1 = Transformer(name='transformer',
                               transformer_type=TransformerType.JAVA,
                               input_example_list=[input_example],
                               output_example_list=[output_example1],
                               jar_location="",
                               transformer_class_name="com.alibaba.flink.ml.workflow.runtime.TestTransformer1")

    output_m = Model(name="outputModel",
                     model_type=ModelType.CHECKPOINT,
                     uri="./target/model/")
    version = ModelVersion(version='version',
                           model_uri='./target/model/v1',
                           log_uri='./target/model/v1')
    trainer = Trainer(name="trainer",
                      run_mode=RunMode.STREAM,
                      input_example=output_example1,
                      output_model=output_m,
                      output_model_version=version,
                      py_main_script="train_stream.py",
                      py_main_func_name="map_func")

    execution = Execution(name="execution",
                          run_mode=RunMode.STREAM,
                          transformer_list=[transformer1],
                          trainer_list=[trainer])

    print(execution.to_json())


if __name__ == "__main__":
    # transform_job_test()
    train_job_test()
