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

from airflow.models.dag import DAG
from airflow.utils import timezone
from airflow.ti_deps.met_handlers.aiflow_met_handler import AIFlowMetHandler
from airflow.operators.dummy_operator import DummyOperator
from airflow.models.event import Event
from airflow.operators.send_event_operator import SendEventOperator

dag = DAG(dag_id='workflow_1', start_date=timezone.utcnow(), schedule_interval="@once")
op_0 = DummyOperator(task_id='0_job', dag=dag)
op_1 = DummyOperator(task_id='1_job', dag=dag)
op_2 = SendEventOperator(
    task_id='2_job',
    dag=dag,
    uri='localhost:50051',
    event=Event(key='key_1', value='value_1', event_type='UNDEFINED'))
op_3 = SendEventOperator(
    task_id='3_job',
    dag=dag,
    uri='localhost:50051',
    event=Event(key='key_2', value='value_2', event_type='UNDEFINED'))
op_4 = DummyOperator(task_id='4_job', dag=dag)
op_5 = SendEventOperator(
    task_id='5_job',
    dag=dag,
    uri='localhost:50051',
    event=Event(key='key_2', value='value_2', event_type='STOP_SCHEDULER_CMD'))
op_2.set_upstream(op_0)
op_2.set_upstream(op_1)
op_4.add_event_dependency('key_1', 'UNDEFINED')
op_4.add_event_dependency('key_2', 'UNDEFINED')
configs_op_4='[{"__af_object_type__": "jsonable", "__class__": "MetConfig", "__module__": "ai_flow.graph.edge", "action": "START", "condition": "NECESSARY", "event_key": "key_1", "event_type": "UNDEFINED", "event_value": "value_1", "life": "ONCE", "value_condition": "EQUAL"}, {"__af_object_type__": "jsonable", "__class__": "MetConfig", "__module__": "ai_flow.graph.edge", "action": "START", "condition": "NECESSARY", "event_key": "key_2", "event_type": "UNDEFINED", "event_value": "value_2", "life": "ONCE", "value_condition": "EQUAL"}]'

op_4.set_event_met_handler(AIFlowMetHandler(configs_op_4))
op_5.set_upstream(op_4)

