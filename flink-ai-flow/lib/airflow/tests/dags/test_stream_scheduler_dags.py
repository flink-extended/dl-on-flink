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

from airflow.models.event import Event, StopSchedulerCMDEvent
from airflow.operators.send_event_operator import SendEventOperator
from airflow.utils import timezone
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.settings import conf
from tests.dags.event_met_handlers import RestartEventMetHandler

port = conf.getint('scheduler', 'notification_port')
dag1 = DAG(
    dag_id='test_start_scheduling',
    start_date=timezone.utcnow(),
    schedule_interval="@once")

dag1_task1 = SendEventOperator(
    task_id='event_1',
    dag=dag1,
    owner='airflow',
    uri="localhost:{0}".format(port),
    event=Event(key="key_1", value="value_1"))

dag1_task2 = DummyOperator(
    task_id='dummy_2',
    dag=dag1,
    owner='airflow')

dag1_task3 = SendEventOperator(
    task_id='event_3',
    dag=dag1,
    owner='airflow',
    uri="localhost:{0}".format(port),
    event=Event(key="key_1", value="value_2"))

dag1_task4 = DummyOperator(
    task_id='dummy_4',
    dag=dag1,
    owner='airflow')

dag1_task5 = DummyOperator(
    task_id='dummy_5',
    dag=dag1,
    owner='airflow')


dag1_stop_task = SendEventOperator(
    task_id='event_5',
    dag=dag1,
    owner='airflow',
    uri="localhost:{0}".format(port),
    event=StopSchedulerCMDEvent())

dag1_task2.add_event_dependency("key_1", "UNDEFINED")
dag1_task2.set_event_met_handler(RestartEventMetHandler())

dag1_task2.set_downstream(dag1_task3)
dag1_task3.set_downstream(dag1_task4)
dag1_task4.set_downstream(dag1_task5)
dag1_stop_task.set_upstream(dag1_task5)
