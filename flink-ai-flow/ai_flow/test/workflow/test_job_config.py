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

from ai_flow.workflow.job_config import JobConfig


class TestJobConfig(unittest.TestCase):
    def test_job_config_from_dict(self):
        job_config = JobConfig.from_dict({
            'test_job': {
                'job_type': 'job_type'
            }
        })
        self.assertEqual('test_job', job_config.job_name)
        self.assertEqual('job_type', job_config.job_type)
        self.assertEqual(5.0, job_config.job_label_report_interval)

        job_config = JobConfig.from_dict({
            'test_job': {
                'job_type': 'job_type',
                'job_label_report_interval': 60.0
            }
        })
        self.assertEqual(60.0, job_config.job_label_report_interval)

    def test_job_config_from_to_dict(self):
        job_config = JobConfig('test_job', 'job_type', 60.0)
        job_config2 = JobConfig.from_dict(JobConfig.to_dict(job_config))
        self.assertEqual(job_config, job_config2)
