#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from typing import Dict, Set

from pyflink.java_gateway import get_gateway
from pyflink.util.java_utils import to_jarray


class TFClusterConfig:
    """
    A config for the Tensorflow cluster.
    """

    def __init__(self, j_tf_cluster_config):
        self._j_tf_cluster_config = j_tf_cluster_config

    @staticmethod
    def new_builder() -> "TFClusterConfig.Builder":
        gateway = get_gateway()
        j_builder = gateway.jvm.org.flinkextended.flink.ml.tensorflow.client \
            .TFClusterConfig.newBuilder()
        return TFClusterConfig.Builder(j_builder)

    def to_builder(self) -> "TFClusterConfig.Builder":
        j_builder = self._j_tf_cluster_config.toBuilder()
        return TFClusterConfig.Builder(j_builder)

    def get_node_type_cnt_map(self) -> Dict[str, int]:
        return self._j_tf_cluster_config.getNodeTypeCntMap()

    def get_properties(self) -> Dict[str, str]:
        return self._j_tf_cluster_config.getProperties()

    def get_property(self, key: str) -> str:
        return self._j_tf_cluster_config.getProperty(key)

    def get_entry_python_file_path(self) -> str:
        return self._j_tf_cluster_config.getEntryPythonFilePath()

    def get_entry_func_name(self) -> str:
        return self._j_tf_cluster_config.getEntryFuncName()

    def get_python_virtual_env_zip_path(self) -> str:
        return self._j_tf_cluster_config.getPythonVirtualEnvZipPath()

    def get_python_file_paths(self) -> Set[str]:
        return self._j_tf_cluster_config.getPythonFilePaths()

    def get_node_count(self, node_type: str) -> int:
        return self._j_tf_cluster_config.getNodeCount(node_type)

    class Builder:
        def __init__(self, j_builder):
            self._j_builder = j_builder

        def add_node_type(self, node_type: str,
                          count: int) -> "TFClusterConfig.Builder":
            self._j_builder.addNodeType(node_type, count)
            return self

        def set_property(self, key: str,
                         value: str) -> "TFClusterConfig.Builder":
            self._j_builder.setProperty(key, value)
            return self

        def add_python_file(self,
                            *python_file_paths: str) -> "TFClusterConfig.Builder":
            self._j_builder.addPythonFile(to_jarray(get_gateway().jvm.String,
                                                    python_file_paths))
            return self

        def set_node_entry(self, python_file_path: str,
                           func_name: str) -> "TFClusterConfig.Builder":
            self._j_builder.setNodeEntry(python_file_path, func_name)
            return self

        def set_python_virtual_env_zip(self,
                                       python_virtual_env_path: str) -> "TFClusterConfig.Builder":
            self._j_builder.setPythonVirtualEnvZip(python_virtual_env_path)
            return self

        def set_worker_count(self, count: int) -> "TFClusterConfig.Builder":
            self._j_builder.setWorkerCount(count)
            return self

        def set_ps_count(self, count: int) -> "TFClusterConfig.Builder":
            self._j_builder.setPsCount(count)
            return self

        def set_is_worker_zero_chief(self,
                                     is_chief: bool) -> "TFClusterConfig.Builder":
            self._j_builder.setIsWorkerZeroChief(is_chief)
            return self

        def build(self) -> "TFClusterConfig":
            return TFClusterConfig(self._j_builder.build())
