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
import unittest
from subprocess import Popen, PIPE

from ai_flow.util.process_utils import get_all_children_pids


class TestProcessUtil(unittest.TestCase):

    def test_get_children(self):
        hh = []
        for i in range(5):
            submitted_process = Popen(
                args="sleep 5",
                shell=True,
                stdout=PIPE,
                stderr=PIPE
            )
            hh.append(submitted_process)
        res = get_all_children_pids(os.getpid())
        print(res)
        # self.assertEqual(5, len(res))
        for h in hh:
            h.wait()


if __name__ == '__main__':
    unittest.main()
