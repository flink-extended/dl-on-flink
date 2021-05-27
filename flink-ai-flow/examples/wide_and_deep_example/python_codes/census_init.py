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
from ai_flow import ExampleSupportType, ModelType


def get_project_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def init():
    af.register_example(
        name='batch_train_input',
        support_type=ExampleSupportType.EXAMPLE_BATCH,
        data_type='file',
        data_format='csv',
        batch_uri='/tmp/census_data/adult.data')
    af.register_example(
        name='stream_preprocess_input',
        support_type=ExampleSupportType.EXAMPLE_STREAM,
        data_type='file',
        data_format='csv',
        batch_uri='/tmp/census_data/adult.data')
    af.register_example(
        name='stream_train_input',
        support_type=ExampleSupportType.EXAMPLE_STREAM,
        data_type='kafka',
        data_format='csv',
        stream_uri='localhost:9092')
    af.register_example(
        name='stream_predict_input',
        support_type=ExampleSupportType.EXAMPLE_STREAM,
        data_type='kafka',
        data_format='csv',
        stream_uri='localhost:9092')
    af.register_example(
        name='stream_predict_output',
        support_type=ExampleSupportType.EXAMPLE_STREAM,
        data_type='kafka',
        data_format='csv',
        stream_uri='localhost:9092')
    af.register_model(
        model_name='wide_and_deep',
        model_type=ModelType.CHECKPOINT)
    af.register_model(
        model_name='wide_and_deep_base',
        model_type=ModelType.SAVED_MODEL)


if __name__ == '__main__':
    af.set_project_config_file(get_project_path() + '/project.yaml')
    init()
