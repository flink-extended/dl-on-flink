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
import abc
from typing import Optional, Callable

import cloudpickle as pickle
import torch.nn
from torch.nn.modules.loss import _Loss as Loss
from torch.optim.lr_scheduler import _LRScheduler as LRScheduler

from dl_on_flink_pytorch.pytorch_context import PyTorchContext

LR_SCHEDULER_CREATOR_T = Callable[[torch.optim.Optimizer], LRScheduler]
OPTIMIZER_CREATOR_T = Callable[[torch.nn.Module], torch.optim.Optimizer]


class PyTorchModelFactory(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def create_model(self, pytorch_context: PyTorchContext) -> torch.nn.Module:
        pass

    @abc.abstractmethod
    def create_loss(self,
                    pytorch_context: PyTorchContext) -> Loss:
        pass

    @abc.abstractmethod
    def create_optimizer(self,
                         pytorch_context: PyTorchContext,
                         model: torch.nn.Module) -> torch.optim.Optimizer:
        pass

    @abc.abstractmethod
    def create_lr_scheduler(self, pytorch_context: PyTorchContext,
                            optimizer: torch.optim.Optimizer) -> Optional[
        LRScheduler]:
        pass


class SimplePyTorchModelFactory(PyTorchModelFactory):

    def __init__(self, model: torch.nn.Module,
                 loss: Loss,
                 optimizer_creator: OPTIMIZER_CREATOR_T,
                 lr_scheduler_creator: Optional[LR_SCHEDULER_CREATOR_T] = None):
        super().__init__()
        self.pickled_model = pickle.dumps(model)
        self.pickled_loss = pickle.dumps(loss)
        self.pickled_optimizer_creator = pickle.dumps(optimizer_creator)
        self.pickled_lr_scheduler_creator = pickle.dumps(lr_scheduler_creator) \
            if lr_scheduler_creator is not None else None

    def create_model(self, pytorch_context: PyTorchContext) -> torch.nn.Module:
        return pickle.loads(self.pickled_model)

    def create_loss(self,
                    pytorch_context: PyTorchContext) -> Loss:
        return pickle.loads(self.pickled_loss)

    def create_optimizer(self,
                         pytorch_context: PyTorchContext,
                         model: torch.nn.Module) -> torch.optim.Optimizer:
        optimizer_creator: OPTIMIZER_CREATOR_T = \
            pickle.loads(self.pickled_optimizer_creator)
        return optimizer_creator(model)

    def create_lr_scheduler(self,
                            pytorch_context: PyTorchContext,
                            optimizer: torch.optim.Optimizer) \
            -> Optional[LRScheduler]:
        if self.pickled_lr_scheduler_creator is None:
            return None
        lr_scheduler_creator: LR_SCHEDULER_CREATOR_T = pickle.loads(
            self.pickled_lr_scheduler_creator)
        return lr_scheduler_creator(optimizer)
