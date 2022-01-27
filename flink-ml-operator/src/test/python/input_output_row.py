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
from flink_ml_framework.java_file import *


def map_func(context):
    bytes_recorder = BytesRecorder(context.from_java(), context.to_java())
    try:
        while True:

            data = bytes_recorder.read_record()
            print(context.index, "data:", data)
            sys.stdout.flush()
            res = bytes_recorder.write_record(data)
            print(context.index, "res:", res)
            sys.stdout.flush()
    except Exception as e:
        msg = traceback.format_exc()
        print (msg)
