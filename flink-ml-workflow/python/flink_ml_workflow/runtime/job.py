from flink_ml_workflow.vertex.execution import *
from flink_ml_workflow.runtime.job_config import *
import logging
import uuid


def create_execution_config(execution_stage: Execution, output_file=None):
    if output_file is None:
        uuid_str = uuid.uuid4().hex
        output_file = "/tmp/" + uuid_str + ".json"
    config_str = execution_stage.to_json()
    with open(output_file, 'w') as f:
        f.write(config_str)
    return output_file


def start_job(execution_stage: Execution):
    import subprocess
    output_file = create_execution_config(execution_stage)
    jar_set = set()
    PLUGIN_JAR = ""
    for i in execution_stage.transformer_list:
        jar_set.add(i.jar_location)

    for j in jar_set:
        PLUGIN_JAR = PLUGIN_JAR + "-C " + j + " "
    to_flink_home = 'cd %s' % FLINK_HOME
    flink_run = 'bin/flink run %s -c %s %s --execution-config %s' \
                % (PLUGIN_JAR, JOB_MAIN_CLASS, JOB_MAIN_JAR, output_file)
    final_command = ' && '.join(
        (to_flink_home, flink_run))
    logging.info(final_command)
    status = subprocess.getstatusoutput(final_command)
    logging.info(str(status))
    return status


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename="./log",
                        filemode='a')
    input_schema = Schema(name_list=['a', 'b', 'c', 'd'], type_list=[DataTypeProto.String, DataTypeProto.String,
                                                                     DataTypeProto.String, DataTypeProto.String])

    input_example = Example(name="input_example",
                            example_type=ExampleType.EXAMPLE_BATCH,
                            data_schema=input_schema,
                            example_format="CSV",
                            batch_uri="/Users/chenwuchao/code/github/flink-ai-extended/flink-ml-workflow/src/test/resources/test.csv",
                            stream_uri="bb",
                            properties={'a': 'a'})

    output_schema1 = Schema(name_list=['a', 'b', 'c'], type_list=[DataTypeProto.String, DataTypeProto.String,
                                                                  DataTypeProto.String])

    output_example1 = TempExample(name="output1", data_schema=output_schema1)

    output_schema2 = Schema(name_list=['a', 'b'], type_list=[DataTypeProto.String, DataTypeProto.String])

    transformer1 = Transformer(name='transformer1',
                               transformer_type=TransformerType.JAVA,
                               input_example_list=[input_example],
                               output_example_list=[output_example1],
                               jar_location="file:///Users/chenwuchao/code/github/flink-ai-extended/flink-ml-workflow-plugins/target/flink-ml-workflow-plugins-0.1.0.jar",
                               transformer_class_name="com.alibaba.flink.ml.workflow.plugins.TestTransformer")

    output_example2 = Example(name="output_example",
                              example_type=ExampleType.EXAMPLE_BATCH,
                              data_schema=output_schema2,
                              example_format="CSV",
                              batch_uri="/tmp/output1.csv",
                              stream_uri="bb",
                              properties={'a': 'a'})

    transformer2 = Transformer(name='transformer2',
                               transformer_type=TransformerType.JAVA,
                               input_example_list=[output_example1],
                               output_example_list=[output_example2],
                               jar_location="file:///Users/chenwuchao/code/github/flink-ai-extended/flink-ml-workflow-plugins/target/flink-ml-workflow-plugins-0.1.0.jar",
                               transformer_class_name="com.alibaba.flink.ml.workflow.plugins.TestTransformer")

    execution = Execution(name="execution",
                          run_mode=RunMode.STREAM,
                          transformer_list=[transformer1, transformer2],
                          trainer_list=[])

    start_job(execution)
