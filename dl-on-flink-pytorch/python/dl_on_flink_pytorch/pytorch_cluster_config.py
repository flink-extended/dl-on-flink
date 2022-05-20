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
from typing import Dict, Callable

from dl_on_flink_framework.cluster_config import ClusterConfig
from dl_on_flink_framework.context import Context
from pyflink.java_gateway import get_gateway


class PyTorchClusterConfig(ClusterConfig):
    """
    A config for the PyTorch cluster.
    """

    def __init__(self,
                 node_type_cnt_map: Dict[str, int],
                 properties: Dict[str, str],
                 entry: Callable[[Context], None]):
        super().__init__(node_type_cnt_map, properties, entry)

    def _to_j_pytorch_cluster_config(self):
        gateway = get_gateway()
        j_builder = gateway.jvm.org.flinkextended.flink.ml.pytorch.PyTorchClusterConfig.newBuilder()
        for node_type, cnt in self.get_node_type_cnt_map().items():
            j_builder.addNodeType(node_type, cnt)

        for k, v in self.get_properties().items():
            j_builder.setProperty(k, v)

        j_builder.setNodeEntry(self.get_entry_python_file_path(),
                               self.get_entry_func_name())

        return j_builder.build()

    @staticmethod
    def new_builder() -> "PyTorchClusterConfig.Builder":
        """
        Create a new Builder for TFClusterConfig.
        """
        return PyTorchClusterConfig.Builder()

    class Builder(ClusterConfig.Builder):
        """
        Builder for TFClusterConfig.
        """

        def __init__(self):
            super().__init__()

        def set_world_size(self, world_size):
            """
            Set the number of processes participating in the PyTorch job.

            :param world_size: Number of processes participating in the PyTorch job.
            """
            self.add_node_type("worker", world_size)
            return self

        def build(self) -> "PyTorchClusterConfig":
            """
            Return an immutable instance of TFClusterConfig.
            """
            return PyTorchClusterConfig(self._node_type_cnt_map,
                                        self._properties,
                                        self._entry)
