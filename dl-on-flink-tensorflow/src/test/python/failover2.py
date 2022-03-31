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

import sys
import time
import logging
import logging.config


# test failover with some nodes already finished
def map_func(context):
    key = context.identity
    index = context.index
    fail_num = context.get_current_attempt_index()
    logging.info(key + " fail num: " + str(fail_num))
    sys.stdout.flush()
    if context.get_node_type() == "worker" and 0 == index and fail_num < 1:
        time.sleep(8)
        logging.info(key + " failover!")
        sys.stdout.flush()
        raise Exception("fail over!")

    if context.get_node_type() == "ps":
        while True:
            time.sleep(1)
    else:
        for i in range(2):
            logging.info(key + " run num: " + str(i))
            sys.stdout.flush()
            time.sleep(1)
        logging.info(key + " finished")
        sys.stdout.flush()


if __name__ == "__main__":
    pass
