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
from typing import Dict, Text

from ai_flow import Jsonable
from ai_flow.workflow.job_config import JobConfig


class FlinkJobConfig(JobConfig):
    """
    FlinkJobConfig is the configuration of the flink job.
    job_name:
        job_type: flink
        properties:
            run_mode: local or cluster (default local)
            flink_run_args: The flink run command args(-pym etc.). It's type is List.
                - -pym
                - /usr/lib/python
            flink_stop_args: The flink run command args(--savepointPath etc.). It's type is List.
                - --savepointPath
                - /tmp/savepoint
    """

    def __init__(self, job_name: Text = None,
                 properties: Dict[Text, Jsonable] = None) -> None:
        super().__init__(job_name, 'flink', properties)

    @property
    def env(self):
        return self.properties.get('env')

    @property
    def run_mode(self):
        if 'run_mode' in self.properties:
            return self.properties.get('run_mode')
        else:
            return 'local'

    @property
    def flink_run_args(self):
        if 'flink_run_args' in self.properties:
            return self.properties.get('flink_run_args')
        else:
            return None

    @property
    def flink_stop_args(self):
        if 'flink_stop_args' in self.properties:
            return self.properties.get('flink_stop_args')
        else:
            return None

    @classmethod
    def from_job_config(cls, job_config: JobConfig) -> 'FlinkJobConfig':
        return FlinkJobConfig(job_name=job_config.job_name,
                              properties=job_config.properties)
