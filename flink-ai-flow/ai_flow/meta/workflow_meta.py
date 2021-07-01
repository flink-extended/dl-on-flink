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
from typing import Text
from ai_flow.common.properties import Properties


class WorkflowMeta(Jsonable):
    """define workflow meta"""

    def __init__(self,
                 name: Text,
                 project_id: int,
                 properties: Properties = None,
                 create_time: int = None,
                 update_time: int = None,
                 uuid: int = None
                 ) -> None:
        """

        :param name: the workflow name
        :param project_id: the uuid of project which contains this workflow
        :param properties: the workflow properties
        :param create_time: create time represented as milliseconds since epoch.
        :param update_time: update time represented as milliseconds since epoch.
        :param uuid: uuid in database
        """

        self.name = name
        self.project_id = project_id
        self.properties = properties
        self.create_time = create_time
        self.update_time = update_time
        self.uuid = uuid

    def __str__(self):
        return '<\n' \
               'WorkflowMeta\n' \
               'uuid:{},\n' \
               'name:{},\n' \
               'project_id:{},\n' \
               'properties:{},\n' \
               'create_time:{},\n' \
               'update_time:{},\n' \
               '>'.format(self.uuid,
                          self.name,
                          self.project_id,
                          self.properties,
                          self.create_time,
                          self.update_time)


def create_workflow(name: Text,
                    project_id: Text,
                    properties: Properties = None,
                    create_time: int = None,
                    update_time: int = None,
                    ) -> WorkflowMeta:
    return WorkflowMeta(name=name, project_id=project_id, properties=properties,
                        create_time=create_time, update_time=update_time)
