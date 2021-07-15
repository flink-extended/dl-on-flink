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
from typing import Text, List, Optional

from ai_flow.common.status import Status

from ai_flow.meta.project_meta import ProjectMeta

from ai_flow.meta.workflow_meta import WorkflowMeta
from ai_flow.exception.exceptions import EmptyGraphException
from ai_flow.plugin_interface.blob_manager_interface import BlobManagerFactory
from ai_flow.util import json_utils
from ai_flow.ai_graph.ai_graph import current_graph
from ai_flow.translator.translator import get_translator
from ai_flow.client.ai_flow_client import get_ai_flow_client
from ai_flow.context.project_context import current_project_config, current_project_context
from ai_flow.context.workflow_config_loader import current_workflow_config
from ai_flow.workflow.job import Job
from ai_flow.workflow.workflow import Workflow, WorkflowPropertyKeys
from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo, WorkflowExecutionInfo, WorkflowInfo
from ai_flow.plugin_interface.job_plugin_interface import get_registered_job_plugin_factory_list
from ai_flow.endpoint.server.workflow_proto_utils import \
    proto_to_workflow, proto_to_workflow_list, proto_to_workflow_execution, proto_to_workflow_execution_list, \
    proto_to_job, proto_to_job_list


def _upload_project_package(workflow: Workflow):
    """
    Upload the project package.

    :param workflow: The generated workflow.
    """
    blob_manager = BlobManagerFactory.get_blob_manager(current_project_config().get(WorkflowPropertyKeys.BLOB))
    uploaded_project_path = blob_manager.upload_project(str(workflow.workflow_snapshot_id),
                                                        current_project_context().project_path)
    workflow.project_uri = uploaded_project_path
    workflow.properties[WorkflowPropertyKeys.BLOB] = current_project_config().get(WorkflowPropertyKeys.BLOB)


def _set_entry_module_path(workflow: Workflow, entry_module_path: Text):
    """
    Set entry model path.
    :param workflow: The generated workflow.
    """
    for job in workflow.jobs.values():
        job.job_config.properties['entry_module_path'] = entry_module_path


def _set_job_plugins(workflow: Workflow):
    plugins = get_registered_job_plugin_factory_list()
    workflow.properties[WorkflowPropertyKeys.JOB_PLUGINS] = {}
    for node in workflow.nodes.values():
        job: Job = node
        job_type = job.job_config.job_type
        workflow.properties[WorkflowPropertyKeys.JOB_PLUGINS][job_type] \
            = [plugins.get(job_type)[0], plugins.get(job_type)[1]]


def submit_workflow(workflow_name: Text = None) -> WorkflowInfo:
    """
    Submit the ai flow workflow to the scheduler.
    :param workflow_name: The name of the workflow(ai_flow.workflow.workflow.Workflow).
    :return: The information of the workflow.
    """
    if current_graph().is_empty():
        raise EmptyGraphException("Cannot submit empty graph")
    entry_module_path = current_project_context().get_workflow_entry_module(workflow_name=workflow_name)
    namespace = current_project_config().get_project_name()
    translator = get_translator()
    workflow = translator.translate(graph=current_graph(), project_context=current_project_context())
    _apply_full_info_to_workflow(entry_module_path, workflow)
    current_graph().clear_graph()
    workflow_meta = get_ai_flow_client().get_workflow_by_name(project_name=current_project_config().get_project_name(),
                                                              workflow_name=workflow_name)
    if workflow_meta is None:
        get_ai_flow_client().register_workflow(name=workflow_name,
                                               project_id=int(current_project_config().get_project_uuid()))
    return proto_to_workflow(get_ai_flow_client()
                             .submit_workflow_to_scheduler(namespace=namespace,
                                                           workflow_json=json_utils.dumps(workflow),
                                                           workflow_name=workflow_name,
                                                           args={}))


def get_workflow(workflow_name: Text = None) -> Optional[WorkflowInfo]:
    """
    Get the workflow information.
    :param workflow_name: The name of the workflow(ai_flow.workflow.workflow.Workflow).
    :return: The information of the workflow.
    """
    workflow_meta: WorkflowMeta = get_ai_flow_client().get_workflow_by_name(project_name=current_project_config()
                                                                            .get_project_name(),
                                                                            workflow_name=workflow_name)
    if workflow_meta is None:
        return None
    project_meta: ProjectMeta = get_ai_flow_client().get_project_by_id(workflow_meta.project_id)
    return WorkflowInfo(workflow_name=workflow_meta.name, namespace=project_meta.name)


def delete_workflow(workflow_name: Text = None) -> WorkflowInfo:
    """
    Delete the ai flow workflow from the scheduler.
    :param workflow_name: The name of the workflow(ai_flow.workflow.workflow.Workflow).
    :return: The information of the workflow.
    """
    status: Status = get_ai_flow_client().delete_workflow_by_name(project_name=current_project_config()
                                                                  .get_project_name(),
                                                                  workflow_name=workflow_name)
    if status == Status.ERROR:
        raise Exception("Delete workflow {} failed")
    return proto_to_workflow(get_ai_flow_client().delete_workflow(namespace=current_project_config().get_project_name(),
                                                                  workflow_name=workflow_name))


def list_workflows(page_size: int, offset: int) -> Optional[List[WorkflowInfo]]:
    """
    List the ai flow workflows.
    :param page_size: Limitation of listed workflows.
    :param offset: Offset of listed workflows.
    :return: The information of the workflow list.
    """
    project_name = current_project_config().get_project_name()
    workflow_list = get_ai_flow_client().list_workflows(project_name=project_name,
                                                        page_size=page_size,
                                                        offset=offset)
    if workflow_list is None:
        return None

    workflow_info_list = []
    for workflow_meta in workflow_list:
        workflow_info_list.append(WorkflowInfo(namespace=project_name, workflow_name=workflow_meta.name))
    return workflow_info_list


def _apply_full_info_to_workflow(entry_module_path, workflow):
    workflow.workflow_config = current_workflow_config()
    _set_entry_module_path(workflow, entry_module_path)
    _upload_project_package(workflow)
    _set_job_plugins(workflow)


def pause_workflow_scheduling(workflow_name: Text = None) -> WorkflowInfo:
    """
    Pause the ai flow workflow from the scheduler.
    :param workflow_name: The name of the workflow(ai_flow.workflow.workflow.Workflow).
    :return: The information of the workflow.
    """
    namespace = current_project_config().get_project_name()
    return proto_to_workflow(get_ai_flow_client().pause_workflow_scheduling(namespace, workflow_name))


def resume_workflow_scheduling(workflow_name: Text = None) -> WorkflowInfo:
    """
    Resume the ai flow workflow from the scheduler.
    :param workflow_name: The name of the workflow(ai_flow.workflow.workflow.Workflow).
    :return: The information of the workflow.
    """
    namespace = current_project_config().get_project_name()
    return proto_to_workflow(get_ai_flow_client().resume_workflow_scheduling(namespace, workflow_name))


def start_new_workflow_execution(workflow_name: Text) -> WorkflowExecutionInfo:
    """
    Run the project under the current project path.
    :param workflow_name: The name of the workflow(ai_flow.workflow.workflow.Workflow).
    :return: The information of a execution of workflow.
    """
    namespace = current_project_config().get_project_name()
    return proto_to_workflow_execution(get_ai_flow_client().start_new_workflow_execution(namespace, workflow_name))


def stop_all_workflow_executions(workflow_name: Text) -> List[WorkflowExecutionInfo]:
    """
    Stop all instances of the workflow.
    :param workflow_name: The name of the workflow(ai_flow.workflow.workflow.Workflow).
    :return: The information of executions of workflow.
    """
    namespace = current_project_config().get_project_name()
    return proto_to_workflow_execution_list(get_ai_flow_client().kill_all_workflow_executions(namespace, workflow_name))


def stop_workflow_execution(execution_id: Text) -> WorkflowExecutionInfo:
    """
    Stop the instance of the workflow.
    :param execution_id: The ai flow workflow execution identify.
    :return: The information of a execution of workflow.
    """
    return proto_to_workflow_execution(get_ai_flow_client().kill_workflow_execution(execution_id))


def get_workflow_execution(execution_id: Text) -> WorkflowExecutionInfo:
    """
    Get the WorkflowExecutionInfo from scheduler.
    :param execution_id: The workflow identity of one execution.
    :return: The information of a execution of workflow.
    """
    return proto_to_workflow_execution(get_ai_flow_client().get_workflow_execution(execution_id))


def list_workflow_executions(workflow_name: Text) -> List[WorkflowExecutionInfo]:
    """
    :param workflow_name: The name of the workflow(ai_flow.workflow.workflow.Workflow).
    :return: All workflow executions of the workflow.
    """
    namespace = current_project_config().get_project_name()
    return proto_to_workflow_execution_list(get_ai_flow_client().list_workflow_executions(namespace, workflow_name))


def start_job_execution(job_name: Text,
                        execution_id: Text) -> JobExecutionInfo:
    """
    Start a job defined in the ai flow workflow.
    :param job_name: The job name which task defined in workflow.
    :param execution_id: The workflow identity of one execution.
    :return: Information about one execution of the job.
    """
    return proto_to_job(get_ai_flow_client().start_job(job_name, execution_id))


def stop_job_execution(job_name: Text,
                       execution_id: Text) -> JobExecutionInfo:
    """
    Stop a job defined in the ai flow workflow.
    :param job_name: The job name which task defined in workflow.
    :param execution_id: The workflow identity of one execution.
    :return: Information about one execution of the job.
    """
    return proto_to_job(get_ai_flow_client().stop_job(job_name, execution_id))


def restart_job_execution(job_name: Text,
                          execution_id: Text) -> JobExecutionInfo:
    """
    Restart a task defined in the ai flow workflow.
    :param job_name: The job name which task defined in workflow.
    :param execution_id: The workflow identity of one execution.
    :return: Information about one execution of the job.
    """
    return proto_to_job(get_ai_flow_client().restart_job(job_name, execution_id))


def get_job_execution(job_name: Text,
                      execution_id: Text) -> JobExecutionInfo:
    """
    Get job information by job name.
    :param job_name: The job name which task defined in workflow.
    :param execution_id: The workflow identity of one execution.
    :return: Information about one execution of the job.
    """
    return proto_to_job(get_ai_flow_client().get_job(job_name, execution_id))


def list_job_executions(execution_id: Text) -> List[JobExecutionInfo]:
    """
    List the jobs of the workflow execution.
    :param execution_id: The workflow identity of one execution.
    :return: Information about executions of the job in the workflow.
    """
    return proto_to_job_list(get_ai_flow_client().list_jobs(execution_id))
