# -*- coding: utf-8 -*-
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

from airflow.ti_deps.deps.base_ti_dep import BaseTIDep


class EventTIDep(BaseTIDep):
    """
    AirFlow Operator running dependent Events
    """
    NAME = "Event Dependencies"
    IGNOREABLE = True

    def _get_dep_statuses(self, ti, session, dep_context=None):
        from airflow.models.taskstate import TaskState, TaskAction
        task_state: TaskState = TaskState.query_task_state(ti, session)
        event_handler = task_state.event_handler
        if event_handler is None:
            yield self._passing_status(
                reason="handler is NULL")
            return
        if task_state.action is None or task_state.action == TaskAction.NONE:
            yield self._failing_status("{0} action is None".format(ti))
        else:
            yield self._passing_status(
                reason="{0} handler pass status".format(ti))
