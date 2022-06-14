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
import base64
import logging
import os
import pickle
from io import StringIO
from typing import List

import pandas as pd
import torch
import torch.distributed as dist
from dl_on_flink_framework.context import Context
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader

from dl_on_flink_pytorch.flink_ml.pytorch_estimator_constants import \
    MODEL_FACTORY_BASE64, FEATURE_COLS, INPUT_COL_NAMES, INPUT_TYPES, LABEL_COL, \
    MODEL_SAVE_PATH, BATCH_SIZE
from dl_on_flink_pytorch.flink_ml.pytorch_model_factory import \
    PyTorchModelFactory
from dl_on_flink_pytorch.flink_stream_dataset import FlinkStreamDataset, \
    DL_ON_FLINK_TYPE_TO_PYTORCH_TYPE
from dl_on_flink_pytorch.pytorch_context import PyTorchContext

logger = logging.getLogger(__file__)


class PyTorchEstimatorFlinkStreamDataset(FlinkStreamDataset):

    def __init__(self, context: PyTorchContext):
        super().__init__(context)
        self.pytorch_context = context

    def parse_record(self, record):
        input_cols: List[str] = self.pytorch_context.get_property(
            INPUT_COL_NAMES) \
            .split(",")
        input_types: List[str] = self.pytorch_context.get_property(
            INPUT_TYPES).split(",")
        feature_cols: List[str] = self.pytorch_context.get_property(
            FEATURE_COLS).split(",")
        label_col = self.pytorch_context.get_property(LABEL_COL)

        df = pd.read_csv(StringIO(record), header=None, names=input_cols)

        feature_tensors = [torch.tensor([df[key][0]],
                                        dtype=DL_ON_FLINK_TYPE_TO_PYTORCH_TYPE[
                                            input_types[idx]])
                           for idx, key in enumerate(feature_cols)]
        label_tensor = torch.tensor([df[label_col][0]],
                                    dtype=DL_ON_FLINK_TYPE_TO_PYTORCH_TYPE[
                                        input_types[
                                            input_cols.index(label_col)]])

        return feature_tensors, label_tensor


def pytorch_train_entry(context: Context):
    pytorch_context = PyTorchContext(context)
    os.environ['MASTER_ADDR'] = pytorch_context.get_master_ip()
    os.environ['MASTER_PORT'] = str(pytorch_context.get_master_port())
    dist.init_process_group(backend='gloo',
                            world_size=pytorch_context.get_world_size(),
                            rank=pytorch_context.get_rank())
    batch_size = int(pytorch_context.get_property(BATCH_SIZE))
    data_loader = DataLoader(
        PyTorchEstimatorFlinkStreamDataset(pytorch_context),
        batch_size=batch_size)

    model_factory: PyTorchModelFactory = pickle.loads(
        base64.decodebytes(context.get_property(MODEL_FACTORY_BASE64)
                           .encode('utf-8')))
    model = model_factory.create_model(pytorch_context)
    model = DDP(model)
    loss_fn = model_factory.create_loss(pytorch_context)
    optimizer = model_factory.create_optimizer(pytorch_context, model)
    lr_scheduler = model_factory.create_lr_scheduler(pytorch_context, optimizer)
    current_epoch = 1
    while True:
        logger.info(f"Epoch: {current_epoch}")
        has_data = False
        epoch_loss = None
        for batch, (features, label) in enumerate(data_loader):
            has_data = True
            optimizer.zero_grad()
            pred = model(*features)
            loss = loss_fn(pred, label)
            loss.backward()
            optimizer.step()
            epoch_loss = loss

        if not has_data:
            break

        dist.all_reduce(epoch_loss, op=dist.ReduceOp.SUM)
        epoch_loss = epoch_loss.item() / dist.get_world_size()

        logger.info(
            f"rank: {pytorch_context.get_rank()} epoch: {current_epoch} "
            f"loss: {epoch_loss:>7f}")
        if lr_scheduler is not None:
            lr_scheduler.step()

        current_epoch += 1

    if pytorch_context.get_rank() == 0:
        model_save_path = pytorch_context.get_property(MODEL_SAVE_PATH)
        os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
        torch.save(model.module, model_save_path)
