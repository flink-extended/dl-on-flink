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
from typing import List

from ai_flow_plugins.job_plugins import python
from ai_flow_plugins.job_plugins.python.python_processor import ExecutionContext
from mnist_data_util import KafkaUtil


class PreProcessor(python.PythonProcessor):
    def __init__(self, bootstrap_servers, topic, file_path, interval):
        super().__init__()
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.file_path = file_path
        self.interval = interval

    def process(self, execution_context: ExecutionContext, input_list: List) -> List:
        kafka_util = KafkaUtil(bootstrap_servers=self.bootstrap_servers)
        kafka_util.producer_loop(self.file_path, self.topic, None, self.interval)
        return []
