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
import logging
import os

import torch
import torch.distributed as dist
from dl_on_flink_framework.context import Context
from dl_on_flink_pytorch.pytorch_context import PyTorchContext
from pyflink.common import Row
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.optim import SGD
from torch.utils.data import DataLoader

logger = logging.getLogger(__file__)


class Linear(nn.Module):

    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1, 1, dtype=torch.float64)

    def forward(self, x):
        return self.linear(x)


def train(context: Context):
    pytorch_context = PyTorchContext(context)
    os.environ['MASTER_ADDR'] = pytorch_context.get_master_ip()
    os.environ['MASTER_PORT'] = str(pytorch_context.get_master_port())
    dist.init_process_group(backend='gloo',
                            world_size=pytorch_context.get_world_size(),
                            rank=pytorch_context.get_rank())
    data_loader = DataLoader(pytorch_context.get_dataset_from_flink(),
                             batch_size=128)

    model = DDP(Linear())
    loss_fn = nn.MSELoss()
    optimizer = SGD(model.parameters(), lr=0.1)
    current_epoch = 1
    while True:
        logger.info(f"Epoch: {current_epoch}")
        has_data = False
        for batch, (x, y) in enumerate(data_loader):
            has_data = True
            optimizer.zero_grad()
            pred = model(x)
            loss = loss_fn(pred, y)
            loss.backward()
            optimizer.step()

            if batch % 100 == 0:
                loss = loss.item()
                logger.info(
                    f"rank: {pytorch_context.get_rank()} batch: {batch} "
                    f"loss: {loss:>7f}")
        if not has_data:
            break

        current_epoch += 1

    if pytorch_context.get_rank() == 0:
        model_save_path = pytorch_context.get_property("model_save_path")
        os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
        torch.save(model.module, model_save_path)


def inference(context: Context):
    pytorch_context = PyTorchContext(context)
    model_path = pytorch_context.get_property("model_save_path")
    model = torch.load(model_path)
    model.eval()

    data_loader = DataLoader(pytorch_context.get_dataset_from_flink())
    writer = pytorch_context.get_data_writer_to_flink()
    for (x, ) in data_loader:
        y = model(x)
        writer.write(Row(x=x.item(), y=y.item()))
