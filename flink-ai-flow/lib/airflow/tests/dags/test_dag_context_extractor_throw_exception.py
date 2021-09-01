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

from airflow import DAG
from airflow.operators.bash import BashOperator
from tests.dags.test_context_extractor import ErrorContextExtractor

DEFAULT_DATE = datetime(2016, 1, 1)
dag = DAG(dag_id="test_dag_context_extractor", start_date=datetime.utcnow(), schedule_interval='@once')
dag.context_extractor = ErrorContextExtractor()

op1 = BashOperator(task_id="task_1", dag=dag, owner='airflow', bash_command='echo "hello world 1!"')
op1.subscribe_event(event_key='k', event_namespace='*', from_task_id='*')
op1.subscribe_event(event_key='broadcast', event_namespace='*', from_task_id='*')
