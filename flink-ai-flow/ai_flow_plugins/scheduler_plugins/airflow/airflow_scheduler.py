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
import os
import shutil
from tempfile import NamedTemporaryFile
from typing import Dict, Text, List, Optional
from ai_flow_plugins.scheduler_plugins.airflow.dag_generator import DAGGenerator
from ai_flow.context.project_context import ProjectContext
from ai_flow.plugin_interface.scheduler_interface import Scheduler, \
    WorkflowInfo, JobExecutionInfo, WorkflowExecutionInfo
from ai_flow.workflow.workflow import Workflow
from ai_flow.workflow import status
from ai_flow.util.time_utils import datetime_to_int64
from airflow.executors.scheduling_action import SchedulingAction
from airflow.models.taskexecution import TaskExecution
from airflow.models.dag import DagModel
from airflow.models.dagrun import DagRun
from airflow.utils.db import create_session
from airflow.utils.state import State
from airflow.contrib.jobs.scheduler_client import EventSchedulerClient, SCHEDULER_NAMESPACE, ExecutionContext


class AirFlowScheduler(Scheduler):
    """
    AirFlowScheduler is an implementation of a Scheduler interface based on AirFlow.
    AirFlowScheduler contains two configuration items:
    1. notification_service_uri: The address of NotificationService.
    2. airflow_deploy_path: AirFlow dag file deployment directory.
    """

    def __init__(self, config: Dict):
        if 'notification_service_uri' not in config:
            raise Exception('`notification_service_uri` option of scheduler config is not configured. '
                            'Please add the `notification_service_uri` option under `scheduler_config` option!')
        if 'airflow_deploy_path' not in config:
            raise Exception('`airflow_deploy_path` option of scheduler config is not configured. '
                            'Please add the `notification_service_uri` option under `airflow_deploy_path` option!')
        super().__init__(config)
        self.dag_generator = DAGGenerator()
        self._airflow_client = None

    @classmethod
    def airflow_dag_id(cls, namespace, workflow_name):
        return '{}.{}'.format(namespace, workflow_name)

    @classmethod
    def dag_id_to_namespace_workflow(cls, dag_id: Text):
        tmp = dag_id.split('.')
        return tmp[0], tmp[1]

    @classmethod
    def airflow_state_to_status(cls, state) -> status.Status:
        if State.SUCCESS == state:
            return status.Status.FINISHED
        elif State.FAILED == state:
            return status.Status.FAILED
        elif State.RUNNING == state:
            return status.Status.RUNNING
        elif State.KILLED == state or State.SHUTDOWN == state \
                or State.KILLING == state:
            # We map airflow state KILLING to KILLED in the assumption that KILLING is a transient state,
            # and it is the best we can do.
            return status.Status.KILLED
        else:
            return status.Status.INIT

    @classmethod
    def status_to_airflow_state(cls, status_: status.Status) -> Text:
        if status.Status.FINISHED == status_:
            return State.SUCCESS
        elif status.Status.FAILED == status_:
            return State.FAILED
        elif status.Status.RUNNING == status_:
            return State.RUNNING
        elif status.Status.KILLED == status_:
            return State.KILLED
        else:
            return State.NONE

    @classmethod
    def dag_exist(cls, dag_id):
        with create_session() as session:
            dag = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
            if dag is None:
                return False
            else:
                return True

    @property
    def airflow_client(self):
        if self._airflow_client is None:
            self._airflow_client = EventSchedulerClient(server_uri=self.config.get('notification_service_uri'),
                                                        namespace=SCHEDULER_NAMESPACE)
        return self._airflow_client

    def submit_workflow(self, workflow: Workflow, project_context: ProjectContext) -> WorkflowInfo:
        dag_id = self.airflow_dag_id(project_context.project_name, workflow.workflow_name)
        code_text = self.dag_generator.generate(workflow=workflow,
                                                project_name=project_context.project_name)
        deploy_path = self.config.get('airflow_deploy_path')
        if deploy_path is None:
            raise Exception("airflow_deploy_path config not set!")
        if not os.path.exists(deploy_path):
            os.makedirs(deploy_path)
        airflow_file_path = os.path.join(deploy_path,
                                         dag_id + '.py')
        if os.path.exists(airflow_file_path):
            os.remove(airflow_file_path)
        with NamedTemporaryFile(mode='w+t', prefix=dag_id, suffix='.py', dir='/tmp', delete=False) as f:
            f.write(code_text)
        shutil.move(f.name, airflow_file_path)
        self.airflow_client.trigger_parse_dag(airflow_file_path)
        return WorkflowInfo(namespace=project_context.project_name,
                            workflow_name=workflow.workflow_name,
                            properties={'dag_file': airflow_file_path})

    def delete_workflow(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        dag_id = self.airflow_dag_id(project_name, workflow_name)
        deploy_path = self.config.get('airflow_deploy_path')
        if deploy_path is None:
            raise Exception("airflow_deploy_path config not set!")
        airflow_file_path = os.path.join(deploy_path,
                                         dag_id + '.py')
        if os.path.exists(airflow_file_path):
            os.remove(airflow_file_path)
            return WorkflowInfo(namespace=project_name,
                                workflow_name=workflow_name,
                                properties={'dag_file': airflow_file_path})
        else:
            return None

    def pause_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        dag_id = self.airflow_dag_id(project_name, workflow_name)
        DagModel.get_dagmodel(dag_id=dag_id).set_is_paused(is_paused=True)
        return WorkflowInfo(namespace=project_name, workflow_name=workflow_name)

    def resume_workflow_scheduling(self, project_name: Text, workflow_name: Text) -> WorkflowInfo:
        dag_id = self.airflow_dag_id(project_name, workflow_name)
        DagModel.get_dagmodel(dag_id=dag_id).set_is_paused(is_paused=False)
        return WorkflowInfo(namespace=project_name, workflow_name=workflow_name)

    def start_new_workflow_execution(self, project_name: Text, workflow_name: Text,
                                     workflow_execution_context: Text = None) \
            -> Optional[WorkflowExecutionInfo]:
        dag_id = self.airflow_dag_id(project_name, workflow_name)
        deploy_path = self.config.get('airflow_deploy_path')
        if deploy_path is None:
            raise Exception("airflow_deploy_path config not set!")
        if not self.dag_exist(dag_id):
            return None
        # TODO: schedule dag with context
        context: ExecutionContext = self.airflow_client.schedule_dag(dag_id)
        with create_session() as session:
            dagrun = DagRun.get_run_by_id(session=session, dag_id=dag_id, run_id=context.dagrun_id)
            if dagrun is None:
                return None
            else:
                return WorkflowExecutionInfo(
                    workflow_info=WorkflowInfo(namespace=project_name, workflow_name=workflow_name),
                    workflow_execution_id=str(dagrun.id),
                    status=status.Status.INIT)

    def stop_all_workflow_execution(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        workflow_execution_list = self.list_workflow_executions(project_name, workflow_name)
        for we in workflow_execution_list:
            if we.status == status.Status.RUNNING:
                self.stop_workflow_execution(we.workflow_execution_id)
        return workflow_execution_list

    def stop_workflow_execution_by_context(self, workflow_name: Text, context: Text) -> Optional[WorkflowExecutionInfo]:
        # TODO: impl
        pass

    def stop_workflow_execution(self, workflow_execution_id: Text) -> Optional[WorkflowExecutionInfo]:
        with create_session() as session:
            dagrun = session.query(DagRun).filter(DagRun.id == int(workflow_execution_id)).first()
            if dagrun is None:
                return None
            project_name, workflow_name = self.dag_id_to_namespace_workflow(dagrun.dag_id)
            context: ExecutionContext = ExecutionContext(dagrun_id=dagrun.run_id)
            current_context = self.airflow_client.stop_dag_run(dagrun.dag_id, context)
            return WorkflowExecutionInfo(workflow_info=WorkflowInfo(namespace=project_name,
                                                                    workflow_name=workflow_name),
                                         workflow_execution_id=workflow_execution_id,
                                         status=status.Status.KILLED)

    def get_workflow_execution(self, workflow_execution_id: Text) -> Optional[WorkflowExecutionInfo]:
        with create_session() as session:
            dagrun = session.query(DagRun).filter(DagRun.id == int(workflow_execution_id)).first()
            if dagrun is None:
                return None
            else:
                status_ = self.airflow_state_to_status(dagrun.state)
                project_name, workflow_name = self.dag_id_to_namespace_workflow(dagrun.dag_id)
                return WorkflowExecutionInfo(workflow_info=WorkflowInfo(namespace=project_name,
                                                                        workflow_name=workflow_name),
                                             workflow_execution_id=workflow_execution_id,
                                             status=status_,
                                             start_date=str(datetime_to_int64(dagrun.start_date)),
                                             end_date=str(datetime_to_int64(dagrun.end_date))
                                             )

    def list_workflow_executions(self, project_name: Text, workflow_name: Text) -> List[WorkflowExecutionInfo]:
        dag_id = self.airflow_dag_id(project_name, workflow_name)
        with create_session() as session:
            dagrun_list = session.query(DagRun).filter(DagRun.dag_id == dag_id).all()
            if dagrun_list is None:
                return []
            else:
                result = []
                for dagrun in dagrun_list:
                    status_ = self.airflow_state_to_status(dagrun.state)
                    result.append(WorkflowExecutionInfo(workflow_info=WorkflowInfo(namespace=project_name,
                                                                                   workflow_name=workflow_name),
                                                        workflow_execution_id=str(dagrun.id),
                                                        status=status_,
                                                        start_date=str(datetime_to_int64(dagrun.start_date)),
                                                        end_date=str(datetime_to_int64(dagrun.end_date)),
                                                        ))
                return result

    def start_job_execution(self, job_name: Text, workflow_execution_id: Text) -> Optional[JobExecutionInfo]:
        with create_session() as session:
            dagrun = session.query(DagRun).filter(DagRun.id == int(workflow_execution_id)).first()
            if dagrun is None:
                return None
            if dagrun.state != State.RUNNING:
                raise Exception('execution: {} state: {} can not trigger job.'.format(workflow_execution_id,
                                                                                      dagrun.state))
            task = dagrun.get_task_instance(job_name, session)
            if task is None:
                return None
            if task.state in State.unfinished:
                raise Exception('job:{} state: {} can not start!'.format(job_name, task.state))
            self.airflow_client.schedule_task(dag_id=dagrun.dag_id,
                                              task_id=job_name,
                                              action=SchedulingAction.START,
                                              context=ExecutionContext(dagrun_id=dagrun.run_id))
            project_name, workflow_name = self.dag_id_to_namespace_workflow(dagrun.dag_id)
            return JobExecutionInfo(job_name=job_name,
                                    status=self.airflow_state_to_status(task.state),
                                    workflow_execution
                                    =WorkflowExecutionInfo(workflow_info=WorkflowInfo(namespace=project_name,
                                                                                      workflow_name=workflow_name),
                                                           workflow_execution_id=workflow_execution_id,
                                                           status=self.airflow_state_to_status(dagrun.state)))

    def stop_job_execution(self, job_name: Text, workflow_execution_id: Text) -> Optional[JobExecutionInfo]:
        with create_session() as session:
            dagrun = session.query(DagRun).filter(DagRun.id == int(workflow_execution_id)).first()
            if dagrun is None:
                return None
            task = dagrun.get_task_instance(job_name, session)
            if task is None:
                return None
            if task.state in State.finished:
                raise Exception('job:{} state: {} can not stop!'.format(job_name, task.state))
            else:
                self.airflow_client.schedule_task(dag_id=dagrun.dag_id,
                                                  task_id=job_name,
                                                  action=SchedulingAction.STOP,
                                                  context=ExecutionContext(dagrun_id=dagrun.run_id))
            project_name, workflow_name = self.dag_id_to_namespace_workflow(dagrun.dag_id)
            return JobExecutionInfo(job_name=job_name,
                                    status=self.airflow_state_to_status(task.state),
                                    workflow_execution
                                    =WorkflowExecutionInfo(workflow_info=WorkflowInfo(namespace=project_name,
                                                                                      workflow_name=workflow_name),
                                                           workflow_execution_id=workflow_execution_id,
                                                           status=self.airflow_state_to_status(dagrun.state)))

    def restart_job_execution(self, job_name: Text, workflow_execution_id: Text) -> Optional[JobExecutionInfo]:
        with create_session() as session:
            dagrun = session.query(DagRun).filter(DagRun.id == int(workflow_execution_id)).first()
            if dagrun is None:
                return None
            if dagrun.state != State.RUNNING:
                raise Exception('execution: {} state: {} can not trigger job.'.format(workflow_execution_id,
                                                                                      dagrun.state))
            task = dagrun.get_task_instance(job_name, session)
            if task is None:
                return None
            self.airflow_client.schedule_task(dag_id=dagrun.dag_id,
                                              task_id=job_name,
                                              action=SchedulingAction.RESTART,
                                              context=ExecutionContext(dagrun_id=dagrun.run_id))
            project_name, workflow_name = self.dag_id_to_namespace_workflow(dagrun.dag_id)
            return JobExecutionInfo(job_name=job_name,
                                    status=self.airflow_state_to_status(task.state),
                                    workflow_execution
                                    =WorkflowExecutionInfo(workflow_info=WorkflowInfo(namespace=project_name,
                                                                                      workflow_name=workflow_name),
                                                           workflow_execution_id=workflow_execution_id,
                                                           status=self.airflow_state_to_status(dagrun.state)))

    def get_job_executions(self, job_name: Text, workflow_execution_id: Text) -> List[JobExecutionInfo]:
        with create_session() as session:
            dagrun = session.query(DagRun).filter(DagRun.id == int(workflow_execution_id)).first()
            if dagrun is None:
                return None
            task_list = session.query(TaskExecution).filter(TaskExecution.dag_id == dagrun.dag_id,
                                                            TaskExecution.execution_date == dagrun.execution_date,
                                                            TaskExecution.task_id == job_name).all()
            if task_list is None:
                return []
            else:
                result = self.build_job_execution_info_list(dagrun, task_list)
                return result

    def build_job_execution_info_list(self, dagrun, task_list):
        project_name, workflow_name = self.dag_id_to_namespace_workflow(dagrun.dag_id)
        result = []
        for task in task_list:
            job = JobExecutionInfo(job_name=task.task_id,
                                   status=self.airflow_state_to_status(task.state),
                                   start_date=str(datetime_to_int64(task.start_date)),
                                   end_date=str(datetime_to_int64(task.end_date)),
                                   workflow_execution
                                   =WorkflowExecutionInfo(workflow_info=WorkflowInfo(namespace=project_name,
                                                                                     workflow_name=workflow_name),
                                                          workflow_execution_id=str(dagrun.id),
                                                          status=self.airflow_state_to_status(dagrun.state)))
            result.append(job)
        return result

    def list_job_executions(self, workflow_execution_id: Text) -> List[JobExecutionInfo]:
        with create_session() as session:
            dagrun = session.query(DagRun).filter(DagRun.id == int(workflow_execution_id)).first()
            if dagrun is None:
                return None
            task_list = session.query(TaskExecution).filter(TaskExecution.dag_id == dagrun.dag_id,
                                                            TaskExecution.execution_date == dagrun.execution_date).all()
            if task_list is None:
                return []
            else:
                result = self.build_job_execution_info_list(dagrun, task_list)
                return result
