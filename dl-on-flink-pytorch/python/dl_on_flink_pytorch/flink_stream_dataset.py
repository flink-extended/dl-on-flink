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
import struct
from io import StringIO
from typing import List, Mapping

import pandas as pd
import torch
from dl_on_flink_framework.context import Context
from dl_on_flink_framework.java_file import JavaFile
from torch.utils.data import IterableDataset

from dl_on_flink_pytorch.flink_ml.pytorch_estimator_constants import \
    INPUT_TYPES

DL_ON_FLINK_TYPE_TO_PYTORCH_TYPE: Mapping[str, torch.dtype] = {
    "INT_32": torch.int32,
    "INT_64": torch.int64,
    "FLOAT_32": torch.float32,
    "FLOAT_64": torch.float64
}


class FlinkStreamDataset(IterableDataset):
    """
    The Pytorch Dataset that reads data from Flink. The Dataset returns a list
    of PyTorch tensors. Each column of the Flink row is a tensor.
    """

    def __init__(self, context: Context):
        from dl_on_flink_pytorch.pytorch_context import PyTorchContext
        self.pytorch_context = PyTorchContext(context)
        self.java_file = JavaFile(context.from_java(), context.to_java())
        self.input_types: List[str] = self.pytorch_context.get_property(
            INPUT_TYPES).split(",")

    def __iter__(self) -> List[torch.Tensor]:
        first_read = True
        while True:
            try:
                res = self.java_file.read(4, not first_read)
                first_read = False
                data_len, = struct.unpack("<i", res)
                record = self.java_file.read(data_len, True).decode('utf-8')
                tensors = self.parse_record(record)
                yield tensors
            except EOFError as _:
                break

    def parse_record(self, record):
        df = pd.read_csv(StringIO(record), header=None)
        tensors = [torch.tensor([df[key][0]],
                                dtype=DL_ON_FLINK_TYPE_TO_PYTORCH_TYPE[
                                    self.input_types[idx]])
                   for idx, key in enumerate(df.columns)]
        return tensors
