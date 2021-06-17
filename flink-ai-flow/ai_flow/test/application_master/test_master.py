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
import unittest

from ai_flow.endpoint.server.server_runner import AIFlowServerRunner
from ai_flow.endpoint.server.server_config import AIFlowServerConfig, DBType
from ai_flow.test import test_util


class TestMaster(unittest.TestCase):

    def test_master_start_stop(self):
        config = AIFlowServerConfig()
        config.set_db_uri(db_type=DBType.SQLITE, uri="sqlite:///sql.db")
        server_runner = AIFlowServerRunner(config_file=test_util.get_master_config_file())
        server_runner.start(is_block=False)
        server_runner.stop()


if __name__ == '__main__':
    unittest.main()
