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
                 uuid: int = None
                 ) -> None:
        """

        :param name: the project name
        :param uri: the address of the code of the project
        :param properties: the project properties
        """

        self.name = name
        self.uri = uri
        self.properties = properties
        self.uuid = uuid

    def __str__(self):
        return '<\n' \
               'ProjectMeta\n' \
               'uuid:{},\n' \
               'name:{},\n' \
               'properties:{},\n' \
               'uri:{},\n' \
               '>'.format(self.uuid,
                          self.name,
                          self.properties,
                          self.uri)


def create_project(name: Text,
                   uri: Text,
                   properties: Properties = None) -> ProjectMeta:
    return ProjectMeta(name=name, uri=uri, properties=properties)
