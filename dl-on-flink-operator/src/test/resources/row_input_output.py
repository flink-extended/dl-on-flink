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

from __future__ import print_function
import traceback
import sys
from dl_on_flink_framework.java_file import BytesRecorder


def map_func(context):
    bytes_recorder = BytesRecorder(context.from_java(), context.to_java())
    while True:
        try:
            data = bytes_recorder.read_record()
            print("Read from Flink: " + data.decode("utf-8"))
            f0_str, f1_str = data.decode("utf-8").split(",")
            f1 = float(f1_str) + 0.5
            out_data = f"{f0_str},{f1}".encode("utf-8")
            bytes_recorder.write_record(out_data)
            print("Write to Flink: " + out_data.decode("utf-8"))
        except EOFError as _:
            # Ignore and break
            break
