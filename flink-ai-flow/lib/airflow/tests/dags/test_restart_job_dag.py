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
from airflow.models.event import Event
from airflow.operators.send_event_operator import SendEventOperator
from airflow.utils import timezone
from airflow.models import DAG
from airflow.settings import conf
from airflow.operators.bash_operator import BashOperator
from tests.dags.event_met_handlers import StopRestartEventMetHandler


port = conf.getint('scheduler', 'notification_port')
dag1 = DAG(
    dag_id='test_restart_job',
    start_date=timezone.utcnow(),
    schedule_interval="@once")

dag1_task1 = BashOperator(
    bash_command="sleep 15",
    task_id='task_1',
    dag=dag1,
    owner='airflow')

dag1_task2 = SendEventOperator(
    task_id='task_2',
    dag=dag1,
    owner='airflow',
    uri="localhost:{0}".format(port),
    event=Event(key="key_1", value="value_1"))

dag1_task3 = BashOperator(
    bash_command="sleep 5",
    task_id='task_3',
    dag=dag1,
    owner='airflow')

dag1_task4 = SendEventOperator(
    task_id='task_4',
    dag=dag1,
    owner='airflow',
    uri="localhost:{0}".format(port),
    event=Event(key="restart", value="value_1"))


dag1_task1.add_event_dependency("key_1", "UNDEFINED")
dag1_task1.add_event_dependency("restart", "UNDEFINED")
dag1_task1.set_event_met_handler(StopRestartEventMetHandler())

dag1_task3.set_downstream(dag1_task4)
