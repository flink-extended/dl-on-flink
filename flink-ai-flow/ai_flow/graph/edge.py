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

from ai_flow.util.json_utils import Jsonable


class Edge(Jsonable):
    """
    Edges are part of the graph(ai_flow.graph.graph.Graph),
    and there are edges connected between nodes(ai_flow.graph.node.Node).
    """

    def __init__(self,
                 source: Text,
                 destination: Text,
                 ) -> None:
        """
        :param source: source identifies the starting node's node_id of the directed edge.
        :param destination: destination identifies the ending node's node_id of the directed edge.
        """
        super().__init__()
        if source is None or destination is None:
            raise Exception('destination node id or source node id can not be None!')
        self.source = source
        self.destination = destination

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Edge):
            return self.destination == o.destination and self.source == o.source
        else:
            return False

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)
