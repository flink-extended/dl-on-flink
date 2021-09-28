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
from mnist_data_util import KafkaUtil

DATASET_URI = os.path.abspath(os.path.join(__file__, "../../../..")) + '/dataset_data/mnist_{}.npz'
bootstrap_servers = 'localhost:9092'
mnist_stream_data_topic = 'mnist_stream_data'
mnist_stream_data = 'kafka://{}/{}'.format(bootstrap_servers, mnist_stream_data_topic)


def init():
    af.register_dataset(name='mnist_train', uri=DATASET_URI.format('train'))
    af.register_dataset(name='mnist_evaluate', uri=DATASET_URI.format('evaluate'))
    af.register_dataset(name='mnist_predict', uri=DATASET_URI.format('predict'))
    kafka_util = KafkaUtil(bootstrap_servers=bootstrap_servers)
    kafka_util.create_topic(mnist_stream_data_topic)
    af.register_dataset(name='mnist_stream_data', uri=mnist_stream_data)


if __name__ == '__main__':
    af.init_ai_flow_context()
    init()
