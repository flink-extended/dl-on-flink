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

from airflow.operators.python import PythonOperator
from airflow.contrib.jobs.event_handlers import ActionEventHandler

from airflow import DAG

DEFAULT_DATE = datetime(2016, 1, 1)
dag = DAG(dag_id="task_retry", start_date=datetime.utcnow(), schedule_interval='@once')


def py_func():
    print('hello world!')
    raise Exception('error')


op = PythonOperator(task_id="task_1", dag=dag, owner='airflow', python_callable=py_func, retries=2,
                    retry_delay=timedelta(seconds=5))

op.subscribe_event('start', '', '')
op.set_events_handler(ActionEventHandler())
