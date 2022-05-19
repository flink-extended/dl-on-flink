#  Copyright 2022 Deep Learning on Flink Authors
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import inspect
from typing import Callable, Dict, Optional

from dl_on_flink_framework.context import Context


class ClusterConfig:
    """
    A config for the deep learning cluster. It is use for the following config:
    - The node type and the number of nodes for each node type in the cluster.
    - The python files and the python environment to run the deep learning node.
    - Any properties for the deep learning node.
    """

    def __init__(self, node_type_cnt_map: Dict[str, int],
                 properties: Dict[str, str],
                 entry: Callable[[Context], None]):
        self._node_type_cnt_map = node_type_cnt_map
        self._properties = properties
        self._entry = entry

    @staticmethod
    def new_builder() -> "ClusterConfig.Builder":
        """
        Create a new Builder for ClusterConfig.
        """
        return ClusterConfig.Builder()

    def get_node_type_cnt_map(self) -> Dict[str, int]:
        return self._node_type_cnt_map

    def get_properties(self) -> Dict[str, str]:
        return self._properties

    def get_property(self, key: str) -> str:
        return self._properties[key]

    def get_entry_python_file_path(self) -> str:
        return inspect.getfile(self._entry)

    def get_entry_func_name(self) -> str:
        return self._entry.__name__

    def get_node_count(self, node_type: str) -> int:
        return self._node_type_cnt_map[node_type]

    class Builder:
        """
        Builder for ClusterConfig.
        """

        def __init__(self):
            self._node_type_cnt_map: Dict[str, int] = {}
            self._properties: Dict[str, str] = {}
            self._entry: Optional[Callable[[Context], None]] = None

        def add_node_type(self, node_type: str,
                          count: int) -> "ClusterConfig.Builder":
            """
            Add a node type to the deep learning cluster and specify how many
            node with the given node type should be in the cluster.
            :param node_type: The node type to be added.
            :param count: The number of node with the node type should be in the
            cluster.
            """
            self._node_type_cnt_map[node_type] = count
            return self

        def set_property(self, key: str,
                         value: str) -> "ClusterConfig.Builder":
            """
            Set a property for the deep learning cluster and nodes.
            :param key: Key of the property.
            :param value: Value of the property.
            """
            self._properties[key] = value
            return self

        def set_node_entry(self, entry: Callable[[Context], None]) \
                -> "ClusterConfig.Builder":
            """
            Specify a python function as the entry point of the deep learning
            node.
            :param entry: The python function that takes Context as argument.
            """
            self._entry = entry
            return self

        def build(self) -> "ClusterConfig":
            """
            Return an immutable instance of ClusterConfig.
            """
            return ClusterConfig(self._node_type_cnt_map, self._properties,
                                 self._entry)
