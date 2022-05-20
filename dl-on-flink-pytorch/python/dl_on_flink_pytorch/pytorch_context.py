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
import json

from dl_on_flink_framework.context import Context
from dl_on_flink_pytorch.flink_stream_dataset import FlinkStreamDataset
from dl_on_flink_pytorch.flink_row_writer import FlinkRowWriter


class PyTorchContext(Context):
    """
    PyTorchContext extends Context and provides some convenient methods to get the
    config of the Pytorch cluster. And it provides the Pytorch Dataset to
    read data from Flink and writer to write data to Flink.
    """

    def __init__(self, other: Context):
        if isinstance(other, Context):
            self.__dict__ = other.__dict__.copy()

    def get_world_size(self) -> int:
        """
        Get the total number of processes in the PyTorch cluster.
        """
        return self.get_node_type_count_map()['worker']

    def get_rank(self) -> int:
        """
        Get the rank of the current process.
        """
        return self.get_index()

    def get_master_ip(self) -> str:
        """
        Get the ip address of the master, i.e., process with rank 0
        """
        master_properties = self._get_master_properties()
        return master_properties['sys:pytorch_master_ip']

    def get_master_port(self) -> int:
        """
        Get the port of the master, i.e., process with rank 0
        """
        master_properties = self._get_master_properties()
        return master_properties['sys:pytorch_master_port']

    def get_dataset_from_flink(self) -> FlinkStreamDataset:
        """
        Get the data loader to read data from Flink.
        """
        return FlinkStreamDataset(self)

    def get_data_writer_to_flink(self) -> FlinkRowWriter:
        """
        Get the data writer to write data to Flink.
        """
        return FlinkRowWriter(self)

    def _get_master_properties(self):
        cluster_json = json.loads(self.get_property('cluster'))
        return cluster_json['job'][0]['tasks']['0']['props']
