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
from ai_flow.meta.job_meta import ExecutionMode
from ai_flow.util.json_utils import Jsonable
from typing import Text, Dict, Optional


class JobConfig(Jsonable):
    """
    Base class for job config. It is used to set the basic job config.

    """

    def __init__(self,
                 job_name: Text = None,
                 job_type: Text = None,
                 properties: Dict[Text, Jsonable] = None) -> None:
        """
        The job config
        :param job_name: Name of the configured job.
        :param job_type: The engine of the job.
        :param properties: Properties of the configured job.
        """
        super().__init__()
        self.job_name: Text = job_name
        self.job_type = job_type
        if properties is None:
            self.properties: Dict[Text, Jsonable] = {}
        else:
            self.properties: Dict[Text, Jsonable] = properties

    @staticmethod
    def from_dict(data: Dict) -> 'JobConfig':
        job_name = list(data.keys())[0]
        return JobConfig(job_name=job_name,
                         job_type=data[job_name].get('job_type', None),
                         properties=data[job_name].get('properties', {}))

    @staticmethod
    def to_dict(job_config: 'JobConfig') -> Dict:
        return {job_config.job_name: {'job_type': job_config.job_type, 'properties': job_config.properties}}
