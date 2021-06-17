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
from ai_flow.application_master.server_runner import AIFlowServerRunner
from ai_flow.util.json_utils import dumps
import flink_ai_flow as faf
import test_util


def run_flink_predict_job():
    example_1 = af.create_example(name="example_1",
                                  support_type=af.ExampleSupportType.EXAMPLE_BOTH,
                                  batch_uri="../../tmp/test1.csv",
                                  stream_uri="../../tmp/test1.csv",
                                  data_format="csv")

    example_2 = af.create_example(name="example_2",
                                  support_type=af.ExampleSupportType.EXAMPLE_BOTH,
                                  batch_uri="../../tmp/test2.csv",
                                  stream_uri="../../tmp/test2.csv",
                                  data_format="csv")
    flink_config = faf.LocalFlinkJobConfig()
    flink_config.flink_home = ''
    with af.config(flink_config):
        batch_args_1: Properties = {}
        ddl = """CREATE TABLE input_table (a STRING, b STRING, c STRING) WITH ('connector' = 'filesystem',
                        'path' = 'INPUT',
                        'format' = 'csv'
                        )"""
        table_name = "input_table"
        batch_args_1['ddl'] = ddl
        batch_args_1['table_name'] = table_name

        stream_args_1 = batch_args_1

        input_example = af.read_example(example_info=example_1,
                                        exec_args=ExecuteArgs(
                                            batch_properties=batch_args_1,
                                            stream_properties=stream_args_1)
                                        )
        model_meta = af.ModelMeta(name="test", model_type="saved_model")

        exec_args: ExecuteArgs = ExecuteArgs()
        exec_args.common_properties = {'a': 'a'}
        train = af.train(input_data_list=[input_example],
                         model_info=model_meta,
                         base_model_info=None,
                         exec_args=exec_args,
                         executor=faf.flink_executor.FlinkJavaExecutor(
                             java_class="com.apache.flink.ai.flow.TestTrain"),
                         name='aa')

    workflow = af.compile_workflow(project_path=test_util.get_project_path())
    print(dumps(list(workflow.jobs.values())[0]))


if __name__ == '__main__':
    config_file = test_util.get_master_config_file()
    server_runner = AIFlowServerRunner(
        config_file=config_file)
    server_runner.start()
    test_util.set_project_config(__file__)
    run_flink_predict_job()
    server_runner.stop()
