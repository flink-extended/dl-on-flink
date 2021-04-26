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
#
from airflow.contrib.jobs.scheduler_client import EventSchedulerClient, ExecutionContext
from airflow.contrib.jobs.event_based_scheduler_job import SCHEDULER_NAMESPACE
from airflow.events.scheduler_events import StopDagEvent
from airflow.executors.scheduling_action import SchedulingAction
from notification_service.client import NotificationClient

_workflow_execution_id_set_flag = False
_workflow_execution_id = None


def set_workflow_execution_id(workflow_execution_id: int):
    global _workflow_execution_id_set_flag
    if _workflow_execution_id_set_flag:
        raise Exception("project configuration cannot be set repeatedly!")
    else:
        _workflow_execution_id = workflow_execution_id
        _workflow_execution_id_set_flag = True


def get_workflow_execution_id():
    return _workflow_execution_id


class AirflowOperation(object):
    def __init__(self, notification_server_uri=None, ns_client: NotificationClient = None):
        self.server_uri = notification_server_uri
        self.namespace = SCHEDULER_NAMESPACE
        if ns_client is not None:
            self.airflow_client = EventSchedulerClient(ns_client=ns_client, namespace=SCHEDULER_NAMESPACE)
        elif notification_server_uri is not None:
            self.airflow_client = EventSchedulerClient(server_uri=notification_server_uri,
                                                       namespace=SCHEDULER_NAMESPACE)
        else:
            raise Exception('notification_server_uri and ns_client can not both empty!')

    def stop_workflow(self, workflow_name) -> bool:
        """
        Stop the workflow. No more workflow execution(Airflow dag_run) would be scheduled and all running jobs would be stopped.

        :param workflow_name: workflow name
        :return: True if succeed
        """
        # TODO For now, simply return True as long as message is sent successfully,
        #  actually we need a response from
        try:
            notification_client = NotificationClient(self.server_uri, SCHEDULER_NAMESPACE)
            notification_client.send_event(StopDagEvent(workflow_name).to_event())
            return True
        except Exception:
            return False

    def suspend_workflow(workflow_name) -> bool:
        """
        Suspend the workflow. No more dag_run would be scheduled.

        :param workflow_name: workflow name
        :return: True if succeed
        """
        pass

    def resume_workflow(workflow_name) -> bool:
        """
        Resume a stopped workflow.

        :param workflow_name: workflow name
        :return: True if succeed
        """
        pass

    def trigger_workflow_execution(self, project_desc, workflow_name) -> ExecutionContext:
        """
        Trigger a new instance of workflow immediately.

        :param workflow_name: workflow name
        :param project_desc: project desc
        :return: True if a new instance is triggered
        """
        deploy_path = project_desc.project_config.get_airflow_deploy_path()
        if deploy_path is None:
            raise Exception("airflow_deploy_path config not set!")
        airflow_file_path = deploy_path + '/' + workflow_name + '.py'
        self.airflow_client.trigger_parse_dag(airflow_file_path)
        return self.airflow_client.schedule_dag(workflow_name)

    def stop_workflow_execution(self, workflow_name, context) -> bool:
        """
        Stop the specific workflow execution(Airflow dag_run)
        """
        result = self.airflow_client.stop_dag_run(dag_id=workflow_name,
                                                  context=context)
        if result and result.dagrun_id == context.dagrun_id:
            return True
        else:
            return False

    def start_task_instance(self, workflow_name, job_name, context: ExecutionContext) -> bool:
        """
        Force start a task. if it is running, do nothing.

        :param workflow_name: workflow name
        :param job_name: job name
        :param context: context of workflow instance
        :return: True if the task is started
        """
        result = self.airflow_client.schedule_task(dag_id=workflow_name,
                                                   task_id=job_name,
                                                   action=SchedulingAction.START,
                                                   context=context)
        if result and result.dagrun_id == context.dagrun_id:
            return True
        else:
            return False

    def stop_task_instance(self, workflow_name, job_name, context: ExecutionContext) -> bool:
        """
        Force stop a running task

        :param workflow_name: workflow name
        :param job_name: job name
        :param context: context of workflow instance
        :return: True if the task is stopped
        """
        result = self.airflow_client.schedule_task(dag_id=workflow_name,
                                                   task_id=job_name,
                                                   action=SchedulingAction.STOP,
                                                   context=context)
        if result and result.dagrun_id == context.dagrun_id:
            return True
        else:
            return False

    def restart_task_instance(self, workflow_name, job_name, context: ExecutionContext) -> bool:
        """
        Force restart a task

        :param workflow_name: workflow name
        :param job_name: job name
        :param context: context of workflow instance
        :return: True if the task is restarted
        """
        result = self.airflow_client.schedule_task(dag_id=workflow_name,
                                                   task_id=job_name,
                                                   action=SchedulingAction.RESTART,
                                                   context=context)
        if result and result.dagrun_id == context.dagrun_id:
            return True
        else:
            return False

    def trigger_parse_dag(self, file_path):
        """Trigger a dag parse of specific file. """
        return self.airflow_client.trigger_parse_dag(file_path)
