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
    """
    INIT: INIT is the execution unit creation status.
    STARTING: STARTING is the execution unit starting status.
    RUNNING: RUNNING is the execution unit running status.
    FINISHED: FINISHED is the successful state of the execution unit.
    FAILED: FAILED is the failed state of the execution unit.
    KILLING: KILLING means the execution unit is being stopped.
    KILLED: KILLED is the state of the execution unit being stopped.
    """
    INIT = 'INIT'
    STARTING = 'STARTING'
    RUNNING = 'RUNNING'
    FINISHED = 'FINISHED'
    FAILED = 'FAILED'
    KILLING = 'KILLING'
    KILLED = 'KILLED'
