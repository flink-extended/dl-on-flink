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
import signal
import threading
import time
import os
import logging
import multiprocessing as mp
from subprocess import Popen
from ai_flow.plugin_interface.scheduler_interface import WorkflowExecutionInfo
from airflow.contrib.jobs.event_based_scheduler_job import EventBasedSchedulerJob
from airflow.events.scheduler_events import StopSchedulerEvent
from airflow.executors.local_executor import LocalExecutor
from typing import Callable

from notification_service.client import NotificationClient


def start_scheduler(file_path, port=50051, executor=None):
    if executor is None:
        executor = LocalExecutor(15)

    scheduler = EventBasedSchedulerJob(
        dag_directory=file_path,
        server_uri="localhost:{}".format(port),
        executor=executor,
        max_runs=-1,
        refresh_dag_dir_interval=30
    )
    print("scheduler starting")
    scheduler.run()


def start_airflow_scheduler_server(file_path, port=50051) -> mp.Process:
    mp.set_start_method('spawn')
    process = mp.Process(target=start_scheduler, args=(file_path, port))
    process.start()
    return process


def start_airflow_web_server() -> Popen:
    def pre_exec():
        # Restore default signal disposition and invoke setsid
        for sig in ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ'):
            if hasattr(signal, sig):
                signal.signal(getattr(signal, sig), signal.SIG_DFL)
        os.setsid()
    env = os.environ.copy()
    stdout_log = './web.log'
    with open(stdout_log, 'w') as out:
        sub_process = Popen(  # pylint: disable=subprocess-popen-preexec-fn
            'airflow webserver -p 8080',
            stdout=out,
            stderr=out,
            env=env,
            shell=True,
            preexec_fn=pre_exec,
        )
    logging.info('Process pid: %s', sub_process.pid)
    return sub_process


def run_ai_flow_workflow(dag_id, test_function: Callable[[NotificationClient], None], port=50051, executor=None):
    def run_test_fun():
        time.sleep(5)
        client = NotificationClient(server_uri="localhost:{}".format(port),
                                    default_namespace="test")
        try:
            test_function(client)
        except Exception as e:
            raise e
        finally:
            client.send_event(StopSchedulerEvent(job_id=0).to_event())

    t = threading.Thread(target=run_test_fun, args=())
    t.setDaemon(True)
    t.start()

    dag_file = '/tmp/airflow/' + dag_id + '.py'
    start_scheduler(file_path=dag_file, port=port, executor=executor)


def get_dag_id(namespace, workflow_name):
    return '{}.{}'.format(namespace, workflow_name)


class WorkflowExecutionWrapper(object):
    def __init__(self):
        self.workflow_execution_info: WorkflowExecutionInfo = None


workflow_wrapper = WorkflowExecutionWrapper()


def set_workflow_execution_info(workflow_execution_info: WorkflowExecutionInfo):
    global workflow_wrapper
    workflow_wrapper.workflow_execution_info = workflow_execution_info


def get_workflow_execution_info() -> WorkflowExecutionInfo:
    global workflow_wrapper
    return workflow_wrapper.workflow_execution_info
