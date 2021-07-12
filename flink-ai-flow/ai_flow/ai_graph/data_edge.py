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
from typing import Text

from ai_flow.graph.edge import Edge


class DataEdge(Edge):
    """
    Connect two AINodes in a job.
    Data flows from the source node to the destination node.
    """
    def __init__(self,
                 source: Text,
                 destination: Text,
                 port: int = 0) -> None:
        """
        :param source: node_id of the data sending node.
        :param destination: node_id of the data receiving node.
        :param port: The serial number of the data sending port.
        """
        super().__init__(destination=destination, source=source)
        self.port = port

    def __eq__(self, o: object) -> bool:
        if isinstance(o, DataEdge):
            return self.destination == o.destination \
                   and self.source == o.source \
                   and self.port == o.port
        else:
            return False

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)
