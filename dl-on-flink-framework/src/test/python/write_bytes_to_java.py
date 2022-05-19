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

from __future__ import print_function
import sys
import traceback
from dl_on_flink_framework.java_file import *


def map_func(context):

    bytes_recorder = BytesRecorder(context.from_java(), context.to_java())
    try:
        res = bytes_recorder.write_record(bytes("aaaaaaa", 'iso-8859-1'))
        print("res:", res)
    except Exception as e:
        msg = traceback.format_exc()
        print (msg)
