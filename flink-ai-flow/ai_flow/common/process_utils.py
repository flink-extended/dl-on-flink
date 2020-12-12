#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import psutil
from typing import List


def get_all_children_pids(current_pid=None) -> List:
    result = []
    if not psutil.pid_exists(current_pid):
        return result
    p = psutil.Process(current_pid)
    for pp in p.children():
        result.append(pp.pid)
        result.extend(get_all_children_pids(pp.pid))
    return result


