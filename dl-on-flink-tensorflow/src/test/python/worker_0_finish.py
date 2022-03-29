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
import time
from dl_on_flink_tensorflow.tensorflow_context import TFContext

def map_func(context):
    tf_context = TFContext(context)
    job_name = tf_context.get_node_type()
    index = tf_context.get_index()
    cluster_json = tf_context.get_tf_cluster()
    print (cluster_json)
    sys.stdout.flush()
    if "worker" == job_name and 0 == index:
        time.sleep(3)
        print("worker 0 finish!")
        sys.stdout.flush()
    else:
        while True:
            print("hello world!")
            sys.stdout.flush()
            time.sleep(3)


if __name__ == "__main__":
    pass
