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
import time
from datetime import timedelta
import datetime
from notification_service.base_notification import UNDEFINED_EVENT_TYPE
from airflow.contrib.jobs.event_handlers import ActionEventHandler, RestartEventHandler
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils import timezone

yesterday = datetime.date.today() + datetime.timedelta(-1)
DEFAULT_DATE = timezone.datetime(yesterday.year, yesterday.month, yesterday.day)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': DEFAULT_DATE,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}
dag = DAG(
    dag_id='event_based_scheduler_dag',
    default_args=default_args,
    #schedule_interval=timedelta(days=1),
)

t1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag,
)

t2 = BashOperator(
    task_id='sleep_1000_secs',
    bash_command='sleep 1000',
    dag=dag,
    event_handler=ActionEventHandler()
)
t2.subscribe_event(event_key="stop",
                   event_namespace='test_namespace',
                   event_type=UNDEFINED_EVENT_TYPE)


def my_sleeping_function(random_base):
    """This is a function that will run within the DAG execution"""
    time.sleep(random_base)


t3 = PythonOperator(
        task_id='python_sleep',
        python_callable=my_sleeping_function,
        op_kwargs={'random_base': 1000},
        dag=dag,
        event_handler=RestartEventHandler()
)
t3.subscribe_event(event_key="any_key",
                   event_namespace='test_namespace',
                   event_type=UNDEFINED_EVENT_TYPE)

dag.doc_md = __doc__


t1 >> [t2, t3]
