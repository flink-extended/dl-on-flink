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
from airflow.operators.bash_operator import BashOperator

dag = DAG(dag_id='test_projec1', start_date=timezone.utcnow(), schedule_interval="@once")
env = {'PYTHONPATH': '/Users/chenwuchao/code/ali/ai_flow/python_ai_flow/test/python_codes/simple_python:/Users/chenwuchao/code/ali/ai_flow:/Users/chenwuchao/code/ali/ai_flow/flink_ai_flow/tests/python_codes:/Users/chenwuchao/code/ali/ai_flow/flink_ai_flow/tests:/Applications/PyCharm CE.app/Contents/helpers/pycharm:/anaconda3/lib/python37.zip:/anaconda3/lib/python3.7:/anaconda3/lib/python3.7/lib-dynload:/Users/chenwuchao/.local/lib/python3.7/site-packages:/anaconda3/lib/python3.7/site-packages:/anaconda3/lib/python3.7/site-packages/aeosa://anaconda3/lib/python3.7/site-packages:/Users/chenwuchao/airflow/dags:/Users/chenwuchao/airflow/config:/Users/chenwuchao/airflow/plugins:/Users/chenwuchao/code/ali/ai_flow/python_ai_flow:/Users/chenwuchao/code/ali/ai_flow/python_ai_flow/test/python_codes'}
op_0 = BashOperator(task_id='None', dag=dag, bash_command='/anaconda3/bin/python /Users/chenwuchao/code/ali/ai_flow/python_ai_flow/local_job_run.py /Users/chenwuchao/code/ali/ai_flow/python_ai_flow/test tmp_funca533b537-8e45-439c-8f71-0ad8dd9409c0LocalPythonJob_0 tmp_args713c2a6b-c023-4340-96ee-22f7c62f15b3LocalPythonJob_0 test_simple_python', env=env)
