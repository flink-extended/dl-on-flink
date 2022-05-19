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


class TFClusterConfig(ClusterConfig):
    """
    A config for the Tensorflow cluster.
    """

    def __init__(self,
                 node_type_cnt_map: Dict[str, int],
                 properties: Dict[str, str],
                 entry: Callable[[Context], None]):
        super().__init__(node_type_cnt_map, properties, entry)

    def _to_j_tf_cluster_config(self):
        gateway = get_gateway()
        j_builder = gateway.jvm.org.flinkextended.flink.ml.tensorflow.client.TFClusterConfig.newBuilder()
        for node_type, cnt in self.get_node_type_cnt_map().items():
            j_builder.addNodeType(node_type, cnt)

        for k, v in self.get_properties().items():
            j_builder.setProperty(k, v)

        j_builder.setNodeEntry(self.get_entry_python_file_path(),
                               self.get_entry_func_name())

        return j_builder.build()

    @staticmethod
    def new_builder() -> "TFClusterConfig.Builder":
        """
        Create a new Builder for TFClusterConfig.
        """
        return TFClusterConfig.Builder()

    class Builder(ClusterConfig.Builder):
        """
        Builder for TFClusterConfig.
        """

        def __init__(self):
            super().__init__()

        def set_worker_count(self, count: int) -> "TFClusterConfig.Builder":
            """
            Set the number of workers in the Tensorflow cluster.

            The node type of the worker nodes is "worker", i.e., the return
            value of dl_on_flink_framework.context.Context.get_node_type is
            "worker".

            :param count: Number of workers.
            """
            self.add_node_type("worker", count)
            return self

        def set_ps_count(self, count: int) -> "TFClusterConfig.Builder":
            """
            Set the number of parameter servers in the Tensorflow cluster.

            The node type of the worker nodes is "ps", i.e., the return value of
            dl_on_flink_framework.context.Context.get_node_type is "ps".

            :param count: Number of parameter servers.
            """
            self.add_node_type("ps", count)
            return self

        def set_is_worker_zero_chief(self, is_chief: bool) \
                -> "TFClusterConfig.Builder":
            """
            Specify whether the worker with index 0 should be designated as the
            chief.

            :param is_chief: Whether the worker 0 should be chief.
            """
            self.set_property("tf_is_worker_zero_chief", str(is_chief).lower())
            return self

        def build(self) -> "TFClusterConfig":
            """
            Return an immutable instance of TFClusterConfig.
            """
            return TFClusterConfig(self._node_type_cnt_map, self._properties,
                                   self._entry)
