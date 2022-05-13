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
import struct
from io import StringIO
from typing import List

import pandas as pd
import torch
from dl_on_flink_framework.context import Context
from dl_on_flink_framework.java_file import JavaFile
from torch.utils.data import IterableDataset


class FlinkDataset(IterableDataset):
    """
    The Pytorch Dataset that reads data from Flink. The Dataset returns a list
    of PyTorch tensors. Each column of the Flink row is a tensor.
    """

    def __init__(self, context: Context):
        self.java_file = JavaFile(context.from_java(), context.to_java())

    def __iter__(self) -> List[torch.Tensor]:
        first_read = True
        while True:
            try:
                res = self.java_file.read(4, not first_read)
                first_read = False
                data_len, = struct.unpack("<i", res)
                record = self.java_file.read(data_len, True).decode('utf-8')
                df = pd.read_csv(StringIO(record), header=None)
                tensors = [torch.tensor([df[key][0]]) for key in df.columns]
                yield tensors
            except EOFError as _:
                break
