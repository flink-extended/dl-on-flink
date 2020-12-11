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
from ai_flow.plugins.kubernetes_cmd_operator import KubernetesCMDOperator

dag = DAG(dag_id='test_project', start_date=timezone.utcnow(), schedule_interval='@deploy')
k8s_cmd_0 = """{"__af_object_type__": "jsonable", "__class__": "KubernetesCMDJob", "__module__": "ai_flow.plugins.kubernetes_cmd_job_plugin", "end_time": null, "exec_cmd": "echo 'hello world' && sleep 1", "exec_engine": "cmd_line", "instance_id": "KubernetesCMDJob_0", "job_config": {"__af_object_type__": "jsonable", "__class__": "KubernetesCMDJobConfig", "__module__": "ai_flow.plugins.kubernetes_cmd_job_plugin", "engine": "cmd_line", "exec_mode": "BATCH", "job_name": "test_cmd", "periodic_config": null, "platform": "kubernetes", "project_desc": {"__af_object_type__": "jsonable", "__class__": "ProjectDesc", "__module__": "ai_flow.project.project_description", "jar_dependencies": null, "log_path": "logs", "project_config": {"entry_module_path": "test_k8s_generator", "master_ip": "localhost", "master_port": 50051, "project_name": "test_project", "project_uuid": "1", "uploaded_project_path": "/Users/chenwuchao/code/ali/ai_flow/ai_flow/test"}, "project_name": "test_project", "project_path": "/Users/chenwuchao/code/ali/ai_flow/ai_flow/test", "project_temp_path": "temp", "python_dependencies": null, "python_paths": [], "resources": null}, "project_local_path": "/Users/chenwuchao/code/ali/ai_flow/ai_flow/test", "project_path": "/Users/chenwuchao/code/ali/ai_flow/ai_flow/test", "properties": {"clean_job_resource": "True", "entry_module_path": "test_k8s_generator", "master_ip": "localhost", "master_port": 50051, "project_name": "test_project", "project_uuid": "1"}}, "job_context": {"__af_object_type__": "jsonable", "__class__": "JobContext", "__module__": "ai_flow.workflow.job_context", "execution_mode": "BATCH", "job_instance_id": null, "job_name": null, "job_uuid": null, "project_config": null, "properties": {}, "workflow_execution_id": 1}, "job_name": "test_cmd", "k8s_job_handler": null, "name": "KubernetesCMDJob_0", "output_num": 1, "platform": "kubernetes", "properties": {}, "start_time": null, "status": "INIT", "uuid": null}"""
op_0 = KubernetesCMDOperator(task_id='test_cmd', dag=dag, job=k8s_cmd_0)
