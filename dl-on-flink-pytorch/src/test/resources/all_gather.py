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
import os

from dl_on_flink_pytorch.pytorch_context import PytorchContext

from dl_on_flink_framework.context import Context

import torch
import torch.distributed as dist


def main(context: Context):
    pytorch_context = PytorchContext(context)
    os.environ['MASTER_ADDR'] = pytorch_context.get_master_ip()
    os.environ['MASTER_PORT'] = str(pytorch_context.get_master_port())
    dist.init_process_group('gloo', world_size=pytorch_context.get_world_size(),
                            rank=pytorch_context.get_rank())
    res_tensors = [torch.zeros(1, dtype=torch.long) for _ in
                   range(pytorch_context.get_world_size())]
    dist.all_gather(res_tensors, torch.tensor([pytorch_context.get_rank()]))
    print(res_tensors)
