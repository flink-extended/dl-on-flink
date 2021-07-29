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
from ai_flow.context.project_context import init_project_config
from ai_flow.api.ai_flow_context import __ensure_project_registered


def get_project_path():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def init():
    af.register_dataset(
        name='batch_train_input',
        data_format='csv',
        uri='/tmp/census_data/adult.data')
    af.register_dataset(
        name='stream_preprocess_input',
        data_format='csv',
        uri='/tmp/census_data/adult.data')
    af.register_dataset(
        name='stream_train_input',
        data_format='csv',
        uri='localhost:9092')
    af.register_dataset(
        name='stream_predict_input',
        data_format='csv',
        uri='localhost:9092')
    af.register_dataset(
        name='stream_predict_output',
        data_format='csv',
        uri='localhost:9092')
    af.register_model(
        model_name='wide_and_deep',
        model_desc='')
    af.register_model(
        model_name='wide_and_deep_base',
        model_desc='')


if __name__ == '__main__':
    init_project_config(get_project_path() + '/project.yaml')
    __ensure_project_registered()
    init()
