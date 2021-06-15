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

from ai_flow.util.json_utils import Jsonable
from ai_flow.common.properties import Properties
from typing import Text
from ai_flow.meta.job_meta import State


class WorkflowExecutionMeta(Jsonable):
    """define workflow execution meta"""

    def __init__(self,
                 name: Text,
                 execution_state: State,
                 project_id: int = None,
                 properties: Properties = None,
                 start_time: int = None,
                 end_time: int = None,
                 log_uri: Text = None,
                 workflow_json=None,
                 signature=None,
                 uuid: int = None
                 ) -> None:
        """

        :param name: the workflow execution name
        :param project_id: refer to which project
        :param properties: the properties of the workflow execution
        :param start_time: the workflow execution start time
        :param end_time: the workflow execution end time
        :param log_uri: the address of the workflow execution log
        :param workflow_json: the workflow json format
        :param signature: the signature of the code
        :param uuid: the address of the workflow execution log
        """
        self.name = name
        self.execution_state = execution_state
        self.project_id = project_id
        self.properties = properties
        self.start_time = start_time
        self.end_time = end_time
        self.log_uri = log_uri
        self.workflow_json = workflow_json
        self.signature = signature
        self.uuid = uuid

    def __str__(self):
        return '<\n' \
               'WorkflowExecutionMeta\n' \
               'uuid:{}\n' \
               'name:{},\n' \
               'project_id:{},\n' \
               'execution_state:{},\n' \
               'properties:{},\n' \
               'start_time:{},\n' \
               'end_time:{},\n' \
               'log_uri:{},\n' \
               'workflow_json:{},\n' \
               'signature:{},\n' \
               '>'.format(self.uuid,
                          self.name,
                          self.project_id,
                          self.execution_state,
                          self.properties,
                          self.start_time,
                          self.end_time,
                          self.log_uri,
                          self.workflow_json,
                          self.signature)


def create_workflow_execution(
        name: Text,
        execution_state: State,
        project_id: int,
        properties: Properties = None,
        start_time: int = None,
        end_time: int = None,
        log_uri: Text = None,
        workflow_json: Text = None,
        signature: Text = None):
    return WorkflowExecutionMeta(name=name, properties=properties, start_time=start_time, end_time=end_time,
                                 execution_state=execution_state, log_uri=log_uri, project_id=project_id,
                                 workflow_json=workflow_json,
                                 signature=signature)
