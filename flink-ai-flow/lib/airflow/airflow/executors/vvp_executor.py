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

import queue
import threading
import traceback
from typing import Any, Dict, List, Optional
from airflow.models.dagbag import DagBag
from airflow.utils.state import State
from airflow.executors.scheduling_action import SchedulingAction
from airflow.models import dagbag
from airflow.configuration import conf
from airflow.executors.base_executor import BaseExecutor, CommandType
from airflow.models.taskinstance import TaskInstance, TaskInstanceKey
from airflow.utils.session import create_session
from airflow.utils.vvp import VVPRestfulUtil
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class EndMessage(object):
    pass


class VVPOperator(BaseOperator):
    template_fields = ('namespace', 'deployment_id', 'token')

    @apply_defaults
    def __init__(self, *, namespace: str, deployment_id: str, token: str = None, **kwargs):
        super().__init__(**kwargs)
        self.namespace = namespace
        self.deployment_id = deployment_id
        self.token = token

    def execute(self, context: Any):
        pass


class VVPExecutor(BaseExecutor):
    """
    This executor handle jobs on vvp platform
    """

    def __init__(self, parallelism=None):
        super().__init__()
        self.queue = queue.Queue()
        if parallelism is None:
            self.parallelism = conf.getint('core', 'parallelism', fallback=3)
        else:
            self.parallelism = parallelism
        self.dagbag = dagbag.DagBag(read_dags_from_db=True)
        self.vvp_restful_util = VVPRestfulUtil(base_url=conf.get('VVPExecutor', 'base_url', fallback=None),
                                               namespaces=conf.get('VVPExecutor', 'namespaces', fallback='vvp'),
                                               tokens=conf.get('VVPExecutor', 'tokens', fallback=None))
        self.threads = []

    def _start_task_instance(self, key: TaskInstanceKey):
        ti = self.get_task_instance(key)
        ti.set_state(State.QUEUED)
        ti.register_task_execution()
        self.queue.put((key, SchedulingAction.START))

    def _stop_related_process(self, ti: TaskInstance) -> bool:
        return True

    def _stop_task_instance(self, key: TaskInstanceKey) -> bool:
        ti = self.get_task_instance(key)
        ti.set_state(State.KILLING)
        self.queue.put((key, SchedulingAction.STOP))
        return True

    def execute_async(self, key: TaskInstanceKey, command: CommandType, queue: Optional[str] = None,
                      executor_config: Optional[Any] = None) -> None:
        self._start_task_instance(key)

    def start(self):
        def _handler(queue: queue.Queue, vvp_restful_util: VVPRestfulUtil, dagbag: DagBag):
            while True:
                try:
                    message = queue.get()
                    if isinstance(message, EndMessage):
                        queue.put(message)
                        break
                    else:
                        key, action = message
                        with create_session() as session:
                            dag = dagbag.get_dag(key.dag_id, session)
                            task = dag.get_task(key.task_id)
                            ti = self.get_task_instance(key)
                            if isinstance(task, VVPOperator) or task.task_type == "VVPOperator":
                                if SchedulingAction.START == action:
                                    vvp_restful_util.start_deployment(task.namespace, task.deployment_id, task.token)
                                    ti.set_state(State.RUNNING)
                                elif SchedulingAction.STOP == action:
                                    vvp_restful_util.stop_deployment(task.namespace, task.deployment_id, task.token)
                                    ti.set_state(State.KILLED)
                            else:
                                self.log.error('VVPExecutor can not execute task {}, which is not VVPOperator(is {})'
                                               .format(ti.task_id, str(task)))
                except Exception as e:
                    self.log.error('VVP job has errors {}'.format(traceback.format_exc()))

        for i in range(self.parallelism):
            thread = threading.Thread(target=_handler, args=(self.queue, self.vvp_restful_util, self.dagbag))
            thread.setName('vvp-executor-{}'.format(i))
            thread.setDaemon(True)
            self.threads.append(thread)
            thread.start()
            self.log.info('start vvp executor parallelism {}'.format(i))

    def sync(self) -> None:
        # Get VVP platform deployments status then update taskInstance and taskExecution
        deployment_status_map = {}
        try:
            namespaces = self.vvp_restful_util.get_namespaces()
            for namespace in namespaces:
                deployments = self.vvp_restful_util.list_deployments(namespace)
                for deployment in deployments:
                    deployment_status_map[(namespace, deployment.id)] = deployment.state
        except Exception as e:
            self.log.error(traceback.format_exc())
        if len(deployment_status_map) > 0:
            with create_session() as session:
                running_tis = session.query(TaskInstance).filter(TaskInstance.state == State.RUNNING).all()
                for ti in running_tis:
                    dag = self.dagbag.get_dag(ti.dag_id, session)
                    task = dag.get_task(ti.task_id)
                    if isinstance(task, VVPOperator) or task.task_type == "VVPOperator":
                        if (task.namespace, task.deployment_id) in deployment_status_map:
                            state = deployment_status_map[(task.namespace, task.deployment_id)]
                            if state == 'SUCCESS':
                                ti.set_state(State.SUCCESS, session)
                                ti.update_latest_task_execution()
                            elif state == 'CANCELLED':
                                ti.set_state(State.KILLED, session)
                                ti.update_latest_task_execution()
                            elif state == 'FAILED':
                                ti.set_state(State.FAILED, session)
                                ti.update_latest_task_execution()
                        else:
                            ti.set_state(State.KILLED, session)
                            ti.update_latest_task_execution()

    def end(self) -> None:
        self.terminate()

    def terminate(self):
        if self.threads is not None and len(self.threads) > 0:
            self.queue.put(EndMessage())
            for t in self.threads:
                t.join()

    def recover_state(self):
        with create_session() as session:
            queued_tis = session.query(TaskInstance).filter(TaskInstance.state.in_([State.QUEUED, State.KILLING])).all()
            for ti in queued_tis:
                dag = self.dagbag.get_dag(ti.dag_id, session)
                task = dag.get_task(ti.task_id)
                if isinstance(task, VVPOperator) or task.task_type == "VVPOperator":
                    key = TaskInstanceKey(ti.dag_id, ti.task_id, ti.execution_date, ti.try_number)
                    if ti.state == State.QUEUED:
                        self.queue.put((key, SchedulingAction.START))
                    elif ti.state == State.KILLING:
                        self.queue.put((key, SchedulingAction.STOP))
