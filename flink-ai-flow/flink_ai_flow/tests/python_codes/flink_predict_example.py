#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import ai_flow as af
from ai_flow import ExecuteArgs, Properties
from ai_flow.application_master.master import AIFlowMaster
from ai_flow.util.json_utils import dumps
import flink_ai_flow as faf
import test_util


def run_flink_predict_job():
    input_file = "/test1.csv"
    output_file = "/output_test2.csv"
    example_1 = af.create_example(name="example_1",
                                  support_type=af.ExampleSupportType.EXAMPLE_BOTH,
                                  batch_uri=input_file,
                                  stream_uri=input_file,
                                  data_format="csv")

    example_2 = af.create_example(name="example_2",
                                  support_type=af.ExampleSupportType.EXAMPLE_BOTH,
                                  batch_uri=output_file,
                                  stream_uri=output_file,
                                  data_format="csv")
    flink_config = faf.LocalFlinkJobConfig()
    flink_config.flink_home = ''
    with af.config(flink_config):
        batch_args_1: Properties = {}
        ddl = """CREATE TABLE input_table (a INT, b INT, c INT) WITH ('connector' = 'filesystem',
                        'path' = 'INPUT',
                        'format' = 'csv'
                        )"""
        table_name = "input_table"
        batch_args_1['ddl'] = ddl
        batch_args_1['table_name'] = table_name

        stream_args_1 = batch_args_1

        batch_args_2: Properties = {}
        ddl = """CREATE TABLE output_table (aa INT, cc INT) WITH ('connector' = 'filesystem',
                        'path' = 'OUTPUT',
                        'format' = 'csv'
                        )"""
        table_name = "output_table"
        batch_args_2['ddl'] = ddl
        batch_args_2['table_name'] = table_name
        stream_args_2 = batch_args_2

        input_example = af.read_example(example_info=example_1,
                                        exec_args=ExecuteArgs(
                                            batch_properties=batch_args_1,
                                            stream_properties=stream_args_1)
                                        )
        model_meta = af.ModelMeta(name="test", model_type="saved_model")
        model_version = af.ModelVersionMeta(version="11111",
                                            model_path="./tmp/saved_model/",
                                            model_metric="./tmp/saved_model/",
                                            model_id=0)
        processed = af.predict(input_data_list=[input_example],
                               model_info=model_meta,
                               model_version_info=model_version,
                               executor=faf.flink_executor.FlinkJavaExecutor(
                                   java_class="com.apache.flink.ai.flow.TestPredict"))

        af.write_example(input_data=processed,
                         example_info=example_2,
                         exec_args=ExecuteArgs(
                             batch_properties=batch_args_2,
                             stream_properties=stream_args_2)
                         )

    g = af.default_graph()
    workflow = af.compile_workflow(project_path=test_util.get_project_path())
    print(dumps(list(workflow.jobs.values())[0]))


if __name__ == '__main__':
    config_file = test_util.get_master_config_file()
    master = AIFlowMaster(
        config_file=config_file)
    master.start()
    test_util.set_project_config(__file__)
    run_flink_predict_job()
    master.stop()
