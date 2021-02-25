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
from airflow.executors.scheduling_action import SchedulingAction


class StopSchedulerEvent(object):
    pass


class TaskStatusChangedEvent(object):
    def __init__(self, task_id, dag_id, execution_date, status):
        self.task_id = task_id
        self.dag_id = dag_id
        self.execution_date = execution_date
        self.status = status


class DagExecutableEvent(object):
    def __init__(self, dag_id):
        self.dag_id = dag_id


class TaskSchedulingEvent(object):
    def __init__(self, task_id, dag_id, execution_date, try_number, action: SchedulingAction):
        self.task_id = task_id
        self.dag_id = dag_id
        self.execution_date = execution_date
        self.try_number = try_number
        self.action = action
