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
from dl_on_flink_framework.java_file import JavaFile
import json
import struct


def map_func(context):

    java_file = JavaFile(context.from_java(), context.to_java())
    try:
        json_object = {'aa': 'aa'}
        json_bytes = json.dumps(json_object)
        json_len = struct.pack("<i", len(json_bytes))
        res = java_file.write(json_len, 4)
        print("res:", res)
        res = java_file.write(json_bytes, len(json_bytes))
        print("res:", res)
    except Exception as e:
        msg = traceback.format_exc()
        print (msg)
