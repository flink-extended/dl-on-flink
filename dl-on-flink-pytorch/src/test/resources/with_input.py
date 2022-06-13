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
import os

import torch
from torch.utils.data import DataLoader
import torch.distributed as dist

from dl_on_flink_framework.context import Context
from dl_on_flink_pytorch.pytorch_context import PyTorchContext


def main(context: Context):
    pytorch_context = PyTorchContext(context)
    os.environ['MASTER_ADDR'] = pytorch_context.get_master_ip()
    os.environ['MASTER_PORT'] = str(pytorch_context.get_master_port())
    dist.init_process_group('gloo', world_size=pytorch_context.get_world_size(),
                            rank=pytorch_context.get_rank())

    dataloader = DataLoader(pytorch_context.get_dataset_from_flink())
    for r, in dataloader:
        output_tensors = [torch.zeros([1, 1], dtype=torch.int32) for _ in
                         range(dist.get_world_size())]
        dist.all_gather(output_tensors, r)
        print(f"Rank {pytorch_context.get_rank()}: {output_tensors}")

