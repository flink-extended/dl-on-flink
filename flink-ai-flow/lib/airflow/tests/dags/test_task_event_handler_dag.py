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
from datetime import datetime
from typing import Tuple

from notification_service.base_notification import BaseEvent

from airflow.executors.scheduling_action import SchedulingAction

from airflow.models.baseoperator import EventHandler
from airflow.operators.dummy import DummyOperator

from airflow import DAG

DEFAULT_TASK_ARGS = {
    'owner': 'airflow',
    'start_date': datetime.now(),
    'max_active_runs': 1,
}

dag = DAG(dag_id="test_event_handler", default_args=DEFAULT_TASK_ARGS)


class ToggleEventHandler(EventHandler):

    def handle_event(self, event: BaseEvent, task_state: object) -> Tuple[SchedulingAction, object]:
        if task_state is None:
            return SchedulingAction.START, True

        if task_state:
            return SchedulingAction.STOP, False
        else:
            return SchedulingAction.START, True


op1 = DummyOperator(task_id="operator_toggle_handler", dag=dag, event_handler=ToggleEventHandler())
op1.subscribe_event("test_event")
