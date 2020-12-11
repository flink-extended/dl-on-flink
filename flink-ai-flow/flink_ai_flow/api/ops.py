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
from typing import Text

from ai_flow.executor.executor import BaseExecutor

from ai_flow.api.ops import user_define_operation
from ai_flow.common.args import ExecuteArgs
from ai_flow.graph.channel import NoneChannel


def vvp_job(exec_args: ExecuteArgs = None,
            name: Text = None)->NoneChannel:
    return user_define_operation(executor=BaseExecutor('vvp'),
                                 output_num=0,
                                 input_data_list=None,
                                 exec_args=exec_args,
                                 name=name)
