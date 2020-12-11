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
from typing import Text
from ai_flow.graph.node import BaseNode
from ai_flow.workflow.job_context import JobContext
from ai_flow.meta.job_meta import State
from ai_flow.workflow.job_config import BaseJobConfig


class BaseJob(BaseNode):
    """
    A BaseJob contains the common information of a ai flow job. Users can implement custom jobs by adding other
    execution information for a specific engine and platform.
    """
    def __init__(self, job_context: JobContext, job_config: BaseJobConfig) -> None:
        """

        :param job_context: Job runtime context
        :param job_config: Job configuration information, including job name, running environment, etc.
        """
        super().__init__()
        self.job_context: JobContext = job_context
        self.job_config = job_config
        self.platform = job_config.platform
        self.exec_engine = job_config.engine
        self.status = State.INIT
        self.start_time = None
        self.end_time = None
        self.uuid = None
        self.job_name: Text = None

