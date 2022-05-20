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

from pyflink.common import Row

from dl_on_flink_framework.context import Context
from dl_on_flink_framework.java_file import JavaFile


def row_to_csv(row: Row) -> str:
    return ",".join(map(str, row._values))


class FlinkRowWriter:
    """
    Write data as rows to Flink for the downstream operator to consume. User
    has to ensure that the downstream operator expects the schema of the
    produced row.
    """

    def __init__(self, context: Context):
        self.java_file = JavaFile(context.from_java(), context.to_java())

    def write(self, row: Row):
        """
        Write a row to Flink.
        """
        csv_str = row_to_csv(row)
        data_len = len(csv_str)
        res = self.java_file.write(struct.pack("<i", data_len), 4)
        if not res:
            raise IOError("Fail to write to Flink")
        res = self.java_file.write(csv_str, data_len)
        if not res:
            raise IOError("Fail to write to Flink")
