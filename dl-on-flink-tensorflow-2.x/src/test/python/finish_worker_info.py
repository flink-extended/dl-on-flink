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

import sys
import time


def map_func(context):
    key = context.identity
    index = context.index
    for i in range(11 - index):
        print(key + " finish worker:" + str(context.getFinishWorkerNode()))
        print(key + " finish worker:" + str(len(context.getFinishWorkerNode())))
        print(len(set(context.getFinishWorkerNode())))
        if 0 == index and 5 == i:
            context.stopJob()

        time.sleep(1)


if __name__ == "__main__":
    pass
