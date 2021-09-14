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

DATASET_URI = os.path.abspath(os.path.join(__file__, "../../../..")) + '/dataset_data/mnist_{}.npz'
hourly_data_dir = '/tmp/hourly_data'
process_result_base_path = '/tmp/hourly_processed'
daily_data_base_path = '/tmp/daily_data'
daily_result = '/tmp/daily_result'


def init():
    af.register_dataset(name='mnist_train', uri=DATASET_URI.format('train'))
    af.register_dataset(name='mnist_evaluate', uri=DATASET_URI.format('evaluate'))
    af.register_dataset(name='mnist_predict', uri=DATASET_URI.format('predict'))
    af.register_dataset(name='hourly_data', uri=hourly_data_dir)
    af.register_dataset(name='hourly_data_processed', uri=process_result_base_path)
    af.register_dataset(name='daily_data', uri=daily_data_base_path)


if __name__ == '__main__':
    af.init_ai_flow_context()
    init()
