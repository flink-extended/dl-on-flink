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
from enum import Enum


class Status(str, Enum):
    INIT = 'INIT'  # The scheduler create the job/workflow and do not scheduling it.
    STARTING = 'STARTING'  # The scheduler scheduling the job/workflow.
    RUNNING = 'RUNNING'  # The job/workflow is running.
    FINISHED = 'FINISHED'  # The job/workflow is finished without exceptions.
    FAILED = 'FAILED'  # The job/workflow is finished with exceptions.
    KILLING = 'KILLING'  # The scheduler receive kill signal and kill the job/workflow.
    KILLED = 'KILLED'  # When the job/workflow is running then the scheduler receive kill signal and kill it.
