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
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
from airflow.contrib.jobs.event_handlers import RestartEventHandler

from airflow import DAG

DEFAULT_DATE = datetime(2016, 1, 1)
dag = DAG(dag_id="single", start_date=datetime.utcnow(), schedule_interval='@once')

op1 = BashOperator(task_id="task_1", dag=dag,  owner='airflow', bash_command='sleep 10')
op1.subscribe_event(event_key='a', event_namespace='test_namespace')
op1.set_events_handler(RestartEventHandler())
