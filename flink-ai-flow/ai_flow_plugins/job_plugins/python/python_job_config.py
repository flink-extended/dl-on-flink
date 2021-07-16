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
from typing import Dict, Text, Optional

from ai_flow import ExecutionMode, Jsonable
from ai_flow.workflow.job_config import JobConfig


class PythonJobConfig(JobConfig):
    """
    PythonJobConfig is the configuration of the python job.
    It has a configuration item env, which represents the environment variables of the python job.
    Job config example:
        job_name:
            job_type: python
            properties:
                python_executable_path: /usr/bin/python3
                env:
                    a: a
                    b: b
    """
    def __init__(self, job_name: Text = None,
                 properties: Dict[Text, Jsonable] = None) -> None:
        super().__init__(job_name, 'python', properties)

    @property
    def env(self):
        return self.properties.get('env')
