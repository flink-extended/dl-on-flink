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
from pyflink.common import Row
from torch.utils.data import DataLoader

from dl_on_flink_pytorch.pytorch_context import PytorchContext

from dl_on_flink_framework.context import Context


def main(context: Context):
    pytorch_context = PytorchContext(context)
    data_loader = DataLoader(pytorch_context.get_dataset_from_flink())
    writer = pytorch_context.get_data_writer_to_flink()
    for tensor, in data_loader:
        x = tensor.item()
        row = Row(x, x + 1)
        writer.write(row)
