# -*- coding: utf-8 -*-
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
from airflow.operators.python_operator import PythonOperator
from airflow.utils import timezone


def print_hello():
    print("hello world!")


dag = DAG(dag_id='event_scheduler_example_k8s_cmd_dag', start_date=timezone.utcnow(), schedule_interval="@once")
op_0 = PythonOperator(task_id='test', dag=dag, python_callable=print_hello, provide_context=False)
