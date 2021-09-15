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
import json
import unittest
from unittest import mock

from ai_flow.workflow.job_config import JobConfig

from ai_flow_plugins.job_plugins.flink.read_only_flink.read_only_flink_job_plugin import ReadOnlyFlinkJobController
from ai_flow_plugins.job_plugins.read_only import ReadOnlyJob


class TestReadOnlyFlinkJobController(unittest.TestCase):
    def test_get_job_label(self):
        controller = ReadOnlyFlinkJobController()
        mock_response = """
Waiting for response...
------------------ Running/Restarting Jobs -------------------
15.09.2021 10:12:54 : b219545e02782aeaf14cce56615af4b7 : CarTopSpeedWindowingExample (RUNNING)
--------------------------------------------------------------
No scheduled jobs.
---------------------- Terminated Jobs -----------------------
15.09.2021 10:12:34 : 6a3f3c0520f89bda4132365489a12e60 : CarTopSpeedWindowingExample (CANCELED)
--------------------------------------------------------------
        """

        with mock.patch.object(ReadOnlyFlinkJobController, "_list_flink_job_status", return_value=mock_response):
            job = ReadOnlyJob(JobConfig("test_job", "read_only_flink", properties={'job_id': '12345'}))
            self.assertEqual("", controller.get_job_label(job))

            job = ReadOnlyJob(JobConfig("test_job", "read_only_flink",
                                        properties={'job_id': 'b219545e02782aeaf14cce56615af4b7'}))
            label = json.loads(controller.get_job_label(job))
            self.assertEqual("15.09.2021 10:12:54", label['start_time'])
            self.assertEqual("CarTopSpeedWindowingExample", label['job_name'])
            self.assertEqual("RUNNING", label['status'])

            job = ReadOnlyJob(JobConfig("test_job", "read_only_flink",
                                        properties={'job_id': '6a3f3c0520f89bda4132365489a12e60'}))
            label = json.loads(controller.get_job_label(job))
            self.assertEqual("15.09.2021 10:12:34", label['start_time'])
            self.assertEqual("CarTopSpeedWindowingExample", label['job_name'])
            self.assertEqual("CANCELED", label['status'])

