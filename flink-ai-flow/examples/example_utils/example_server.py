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
import os
from ai_flow.endpoint.server.server_runner import AIFlowServerRunner
from ai_flow_plugins.tests import airflow_db_utils
from ai_flow_plugins.tests import airflow_scheduler_utils


class ExampleServer(object):
    def __init__(self):
        self.master = None

    def run(self):
        airflow_db_utils.clear_all()
        config_file = os.path.dirname(__file__) + '/master.yaml'
        aiflow_db_file = os.path.dirname(__file__) + '/aiflow.db'
        if os.path.exists(aiflow_db_file):
            os.remove(aiflow_db_file)
        self.master = AIFlowServerRunner(config_file=config_file)
        self.master.start(is_block=False)
        airflow_scheduler_utils.start_scheduler(file_path='/tmp/airflow/')


if __name__ == '__main__':
    server = ExampleServer()
    server.run()
