# Copyright 2019 The flink-ai-extended Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

import os
from pyflink.datastream.stream_execution_environment import StreamExecutionEnvironment
from tensorflow_on_flink_datastream import train, inference
from tensorflow_on_flink_tfconf import TFCONSTANS


class datastreamTest(object):

    @staticmethod
    def addTrainStream():
        stream_env = StreamExecutionEnvironment.get_execution_environment()
        work_num = 2
        ps_num = 1
        python_file = os.getcwd() + "/../../src/test/python/add.py"
        func = "map_func"
        property = None
        env_path = None
        zk_conn = None
        zk_base_path = None
        input_ds = None
        output_row_type = None

        train(work_num, ps_num, python_file, func, property, env_path, zk_conn, zk_base_path, stream_env, input_ds, output_row_type)
        # inference(work_num, ps_num, python_file, func, property, env_path, zk_conn, zk_base_path, stream_env, input_ds, output_row_type)

    @staticmethod
    def addTrainChiefAloneStream():
        stream_env = StreamExecutionEnvironment.get_execution_environment()
        work_num = 2
        ps_num = 1
        python_file = os.getcwd() + "/../../src/test/python/add.py"
        func = "map_func"
        property = {}
        property[TFCONSTANS.TF_IS_CHIEF_ALONE] = "true"
        env_path = None
        zk_conn = None
        zk_base_path = None
        input_ds = None
        output_row_type = None

        train(work_num, ps_num, python_file, func, property, env_path, zk_conn, zk_base_path, stream_env, input_ds, output_row_type)
        # inference(work_num, ps_num, python_file, func, property, env_path, zk_conn, zk_base_path, stream_env, input_ds, output_row_type)



if __name__ == '__main__':
    datastreamTest.addTrainStream()
    datastreamTest.addTrainChiefAloneStream()
