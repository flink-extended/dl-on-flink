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
import os

import ai_flow as af
from ai_flow.application_master.master import AIFlowMaster
from ai_flow.common.properties import ExecuteProperties, Properties
from ai_flow.util import json_utils
import flink_ai_flow as faf
import test_util


def run_flink_job():
    input_file = "/test1.csv"
    output_file ="/output_test1.csv"
    if os.path.exists(output_file):
        os.remove(output_file)

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
    flink_config.flink_home = "/Users/chenwuchao/soft/apache/flink-1.10.0"
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

        batch_args_2: Properties = {}
        ddl = """CREATE TABLE output_table (aa STRING, bb STRING) WITH ('connector' = 'filesystem',
                'path' = 'OUTPUT',
                'format' = 'csv'
                )"""
        table_name = "output_table"
        batch_args_2['ddl'] = ddl
        batch_args_2['table_name'] = table_name
        stream_args_2 = batch_args_2

        input_example = af.read_example(example_info=example_1,
                                        exec_args=ExecuteProperties(
                                            batch_properties=batch_args_1,
                                            stream_properties=stream_args_1)
                                        )
        processed = af.transform(input_data_list=[input_example],
                                 executor=faf.FlinkJavaExecutor(
                                     java_class="com.apache.flink.ai.flow.TestTransformer"))

        af.write_example(input_data=processed,
                         example_info=example_2,
                         exec_args=ExecuteProperties(
                             batch_properties=batch_args_2,
                             stream_properties=stream_args_2)
                         )

    workflow = af.compile_workflow(test_util.get_project_path())
    print(json_utils.dumps(list(workflow.jobs.values())[0]))


if __name__ == '__main__':
    config_file = test_util.get_master_config_file()
    master = AIFlowMaster(
        config_file=config_file)
    master.start()
    test_util.set_project_config(__file__)
    run_flink_job()
    master.stop()
