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
    JobConfig is the configuration information of the Job(ai_flow.workflow.job.Job).
    """

    def __init__(self,
                 job_name: Text = None,
                 job_type: Text = None,
                 job_label_report_interval: float = 5.0,
                 properties: Dict[Text, Jsonable] = None) -> None:
        """
        :param job_name: Name of the configured job.
        :param job_type: The job type of the job, such as bash python etc..
        :param properties: Properties of the configured job.
        """
        super().__init__()
        self.job_name: Text = job_name
        self.job_type = job_type
        self.job_label_report_interval = job_label_report_interval
        if properties is None:
            self.properties: Dict[Text, Jsonable] = {}
        else:
            self.properties: Dict[Text, Jsonable] = properties

    @staticmethod
    def from_dict(data: Dict) -> 'JobConfig':
        """
        Build JobConfig from a dict.
        The dict example:
        {'job_name':{'job_type':'bash', 'properties': {}}}
        """
        job_name = list(data.keys())[0]
        return JobConfig(job_name=job_name,
                         job_type=data[job_name].get('job_type', None),
                         job_label_report_interval=data[job_name].get('job_label_report_interval',
                                                                      5.0),
                         properties=data[job_name].get('properties', {}))

    @staticmethod
    def to_dict(job_config: 'JobConfig') -> Dict:
        """Convert the JobConfig to a dict"""
        return {job_config.job_name: {'job_type': job_config.job_type,
                                      'job_label_report_interval':
                                          job_config.job_label_report_interval,
                                      'properties': job_config.properties}}

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return self.__dict__.__repr__()
