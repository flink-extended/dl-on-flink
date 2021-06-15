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


class ProjectMeta(Jsonable):
    """define project meta"""

    def __init__(self,
                 name: Text,
                 uri: Text,
                 properties: Properties = None,
                 user: Text = None,
                 password: Text = None,
                 project_type: Text = None,
                 uuid: int = None
                 ) -> None:
        """

        :param name: the project name
        :param uri: the address of the code of the project
        :param user: the project user
        :param password: the project password
        :param properties: the project properties
        :param project_type: the project type, GIT, notebook or etc.
        """

        self.name = name
        self.project_type = project_type
        self.uri = uri
        self.user = user
        self.password = password
        self.properties = properties
        self.uuid = uuid

    def __str__(self):
        return '<\n' \
               'ProjectMeta\n' \
               'uuid:{},\n' \
               'name:{},\n' \
               'project_type:{},\n' \
               'properties:{},\n' \
               'uri:{},\n' \
               'user:{},\n' \
               'password:{},\n' \
               '>'.format(self.uuid,
                          self.name,
                          self.project_type,
                          self.properties,
                          self.uri,
                          self.user,
                          self.password)


def create_project(name: Text,
                   uri: Text,
                   user: Text = None,
                   password: Text = None,
                   properties: Properties = None,
                   project_type: Text = None) -> ProjectMeta:
    return ProjectMeta(name=name, uri=uri, user=user, password=password, properties=properties,
                       project_type=project_type)
