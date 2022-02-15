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
import sys
import traceback
import struct
from flink_ml_framework.java_file import JavaFile


def map_func(context):
    java_file = JavaFile(context.from_java(), context.to_java())
    try:
        res = java_file.read(4)
        # len = int(''.join(reversed(res)).encode('hex'), 16)
        data_len, = struct.unpack("<i", res)
        print("res", type(data_len), data_len)
        data = java_file.read(data_len)
        print("data", str(data))
    except Exception as e:
        msg = traceback.format_exc()
        print (msg)
