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
from ai_flow.workflow.control_edge import EventCondition
from typing import Text, List, Optional

from ai_flow.ai_graph.ai_graph import current_graph
from ai_flow.client.ai_flow_client import get_ai_flow_client
from ai_flow.common.status import Status
from ai_flow.context.project_context import current_project_config, current_project_context
from ai_flow.context.workflow_config_loader import current_workflow_config
from ai_flow.endpoint.server.workflow_proto_utils import \
    proto_to_workflow, proto_to_workflow_execution, proto_to_workflow_execution_list, \
    proto_to_job, proto_to_job_list
from ai_flow.exception.exceptions import EmptyGraphException
from ai_flow.meta.project_meta import ProjectMeta
from ai_flow.meta.workflow_meta import WorkflowMeta
from ai_flow.plugin_interface.blob_manager_interface import BlobConfig, BlobManagerFactory
from ai_flow.plugin_interface.job_plugin_interface import get_registered_job_plugin_factory_list
from ai_flow.plugin_interface.scheduler_interface import JobExecutionInfo, WorkflowExecutionInfo, WorkflowInfo
from ai_flow.translator.translator import get_translator
from ai_flow.util import json_utils
from ai_flow.workflow.job import Job
from ai_flow.workflow.workflow import Workflow, WorkflowPropertyKeys


def _upload_project_package(workflow: Workflow):
    """
    Uploads the project package of the given :class:`~ai_flow.workflow.workflow.Workflow` by the
    :class:`~ai_flow.plugin_interface.blob_manager_interface.BlobManager`.

    :param workflow: The generated :class:`~ai_flow.workflow.workflow.Workflow`.
    """
    blob_config = BlobConfig(current_project_config().get(WorkflowPropertyKeys.BLOB))
    blob_manager = BlobManagerFactory.create_blob_manager(blob_config.blob_manager_class(),
                                                          blob_config.blob_manager_config())
    uploaded_project_path = blob_manager.upload_project(str(workflow.workflow_snapshot_id),
                                                        current_project_context().project_path)
    workflow.project_uri = uploaded_project_path
    workflow.properties[WorkflowPropertyKeys.BLOB] = current_project_config().get(WorkflowPropertyKeys.BLOB)


def _set_entry_module_path(workflow: Workflow, entry_module_path: Text):
    """
    Sets the specified entry module path to the job config of the given :class:`~ai_flow.workflow.workflow.Workflow`.
    
    :param workflow: The generated :class:`~ai_flow.workflow.workflow.Workflow`.
    :param entry_module_path: The entry module path of the workflow.
    """
    for job in workflow.jobs.values():
        job.job_config.properties['entry_module_path'] = entry_module_path


def _set_job_plugins(workflow: Workflow):
    """
    Sets the registered job plugins to the properties of the given :class:`~ai_flow.workflow.workflow.Workflow`.

    :param workflow: The generated :class:`~ai_flow.workflow.workflow.Workflow`.
    """
    plugins = get_registered_job_plugin_factory_list()
    workflow.properties[WorkflowPropertyKeys.JOB_PLUGINS] = {}
    for node in workflow.nodes.values():
        job: Job = node
        job_type = job.job_config.job_type
        workflow.properties[WorkflowPropertyKeys.JOB_PLUGINS][job_type] \
            = [plugins.get(job_type)[0], plugins.get(job_type)[1]]


def _apply_full_info_to_workflow(workflow: Workflow, entry_module_path: Text):
    """
    Applies the full information to the specified :class:`~ai_flow.workflow.workflow.Workflow` with the given entry
    module path. The application of the workflow full information sets the entry module path, uploads the project
    package of the workflow and set the registered job plugins.

    :param workflow: The generated :class:`~ai_flow.workflow.workflow.Workflow`.
    :param entry_module_path: The entry module path of the workflow.
    """
    workflow.workflow_config = current_workflow_config() # This line may be redundant as config is set in translation
    _set_entry_module_path(workflow, entry_module_path)
    _upload_project_package(workflow)
    _set_job_plugins(workflow)


def submit_workflow(workflow_name: Text = None) -> WorkflowInfo:
    """
    Submits the user-defined workflow to the scheduler with the given name of workflow. Before the submission of
    workflow in Scheduler Service, the metadata of workflow will be registered in Metadata Service.

    The submission of workflow translates the current :class:`~ai_flow.ai_graph.ai_graph.AIGraph` , uploads the
    project package, registers the metadata of the specified workflow and submits the workflow by Scheduler Service
    which delegates the submission to the :class:`~ai_flow.plugin_interface.scheduler_interface.Scheduler`.

    :param workflow_name: The name of the workflow.
    :return: The :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowInfo` which contains the information
                 about the submitted workflow.
    """
    if current_graph().is_empty():
        raise EmptyGraphException("Cannot submit empty graph")
    entry_module_path = current_project_context().get_workflow_entry_module(workflow_name=workflow_name)
    namespace = current_project_config().get_project_name()
    translator = get_translator()
    workflow = translator.translate(graph=current_graph(), project_context=current_project_context())
    _apply_full_info_to_workflow(workflow, entry_module_path)
    current_graph().clear_graph()
    workflow_meta = get_ai_flow_client().get_workflow_by_name(project_name=current_project_config().get_project_name(),
                                                              workflow_name=workflow_name)
    if workflow_meta is None:
        get_ai_flow_client().register_workflow(name=workflow_name,
                                               project_id=int(current_project_config().get_project_uuid()),
                                               context_extractor=current_graph().get_context_extractor())
    return proto_to_workflow(get_ai_flow_client()
                             .submit_workflow_to_scheduler(namespace=namespace,
                                                           workflow_json=json_utils.dumps(workflow),
                                                           workflow_name=workflow_name,
                                                           args={}))


def delete_workflow(workflow_name: Text = None) -> WorkflowInfo:
    """
    Deletes the workflow from the scheduler with the given name of workflow. Before the deletion of workflow in Scheduler
    Service, the metadata of workflow will be deleted in Metadata Service.

    The deletion of workflow deletes the metadata of the specified workflow, and removes the workflow by Scheduler
    Service that assigns the deletion to the :class:`~ai_flow.plugin_interface.scheduler_interface.Scheduler`.

    :param workflow_name: The name of the workflow.
    :return: The :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowInfo` which contains the information
                 about the deleted workflow.
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
    Lists the :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowInfo` with the given pagination.

    :param page_size: The limitation of the listed workflow pagination.
    :param offset: The offset of the listed workflow pagination.
    :return: Pagination list of the :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowInfo`.
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


def get_workflow(workflow_name: Text = None) -> Optional[WorkflowInfo]:
    """
    Gets the :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowInfo` with the given name of workflow.

    :param workflow_name: The name of the workflow.
    :return: The :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowInfo` which contains the information
                 about the workflow.
    """
    workflow_meta: WorkflowMeta = get_ai_flow_client().get_workflow_by_name(project_name=current_project_config()
                                                                            .get_project_name(),
                                                                            workflow_name=workflow_name)
    if workflow_meta is None:
        return None
    project_meta: ProjectMeta = get_ai_flow_client().get_project_by_id(workflow_meta.project_id)
    return WorkflowInfo(workflow_name=workflow_meta.name, namespace=project_meta.name)


def pause_workflow_scheduling(workflow_name: Text = None) -> WorkflowInfo:
    """
    Pauses the workflow by the scheduler with the given name of workflow in Scheduler Service.
    
    :param workflow_name: The name of the workflow.
    :return: The :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowInfo` which contains the information
                 about the scheduling paused workflow.
    """
    namespace = current_project_config().get_project_name()
    return proto_to_workflow(get_ai_flow_client().pause_workflow_scheduling(namespace, workflow_name))


def resume_workflow_scheduling(workflow_name: Text = None) -> WorkflowInfo:
    """
    Resumes the workflow by the scheduler with the given name of workflow in Scheduler Service.

    :param workflow_name: The name of the workflow.
    :return: The :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowInfo` which contains the information
                 about the scheduling resumed workflow.
    """
    namespace = current_project_config().get_project_name()
    return proto_to_workflow(get_ai_flow_client().resume_workflow_scheduling(namespace, workflow_name))


def start_new_workflow_execution_on_events(workflow_name: Text, event_conditions: List[EventCondition]):
    """
    Start new workflow executions whenever any EventCondition in the given list is met. The context of the started
    workflow execution is decided by the :class:`ContextExtractor` set to the workflow.
    Multiple calls on the same workflow will change the event conditions list. To disable starting new workflow
    executions on event, one could pass a empty list.

    :param workflow_name: The name of the workflow.
    :param event_conditions: A list of :class:`EventCondition`.
    """
    namespace = current_project_config().get_project_name()
    get_ai_flow_client().start_new_workflow_execution_on_events(namespace, workflow_name, event_conditions)


def stop_workflow_execution_on_events(workflow_name: Text, event_conditions: List[EventCondition]):
    """
    Stop new workflow executions whenever any EventCondition in the given list is met. The context of the workflow
    execution to stop is decided by the :class:`ContextExtractor` set to the workflow.
    Multiple calls on the same workflow will change the event conditions list. To disable stopping workflow
    execution on event, one could pass a empty list.

    :param workflow_name: The name of the workflow.
    :param event_conditions: A list of :class:`EventCondition`.
    """
    namespace = current_project_config().get_project_name()
    get_ai_flow_client().stop_workflow_execution_on_events(namespace, workflow_name, event_conditions)


def start_new_workflow_execution(workflow_name: Text, context: Text = None) -> WorkflowExecutionInfo:
    """
    Starts the new workflow execution by the scheduler with the given name of workflow. The start of the workflow
    execution is delegated to the :class:`~ai_flow.plugin_interface.scheduler_interface.Scheduler` in Scheduler Service,
    that runs the workflow based on the current project path.

    :param workflow_name: The name of the workflow.
    :param context: The context of the workflow execution to start.
    :return: The :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowExecutionInfo` which contains the
                 information about the started workflow execution.
    """
    namespace = current_project_config().get_project_name()
    return proto_to_workflow_execution(get_ai_flow_client().start_new_workflow_execution(namespace, workflow_name,
                                                                                         context))


def stop_all_workflow_executions(workflow_name: Text) -> List[WorkflowExecutionInfo]:
    """
    Stops the workflow executions by the scheduler with the given name of workflow. The stop of the workflow execution
    is delegated to the :class:`~ai_flow.plugin_interface.scheduler_interface.Scheduler` in Scheduler Service, that stops
    the workflow running.

    :param workflow_name: The name of the workflow.
    :return: The :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowExecutionInfo` which contains the
                 information about the stopped workflow execution.
    """
    namespace = current_project_config().get_project_name()
    return proto_to_workflow_execution_list(get_ai_flow_client().kill_all_workflow_executions(namespace, workflow_name))


def stop_workflow_execution(execution_id: Text) -> WorkflowExecutionInfo:
    """
    Stops the workflow execution by the scheduler with the given id of workflow execution. The stop of the workflow
    execution is delegated to the :class:`~ai_flow.plugin_interface.scheduler_interface.Scheduler` in Scheduler Service,
    that stops the workflow running.

    :param execution_id: The id of the workflow execution.
    :return: The :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowExecutionInfo` which contains the
                 information about the stopped workflow execution.
    """
    return proto_to_workflow_execution(get_ai_flow_client().kill_workflow_execution(execution_id))


def list_workflow_executions(workflow_name: Text) -> List[WorkflowExecutionInfo]:
    """
    Lists the :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowExecutionInfo` with the given workflow name.

    :param workflow_name: The name of the workflow.
    :return: List of the :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowExecutionInfo`.
    """
    namespace = current_project_config().get_project_name()
    return proto_to_workflow_execution_list(get_ai_flow_client().list_workflow_executions(namespace, workflow_name))


def get_workflow_execution(execution_id: Text) -> WorkflowExecutionInfo:
    """
    Gets the :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowExecutionInfo` with the given id of workflow
    execution.

    :param execution_id: The id of the workflow execution.
    :return: The :class:`~ai_flow.plugin_interface.scheduler_interface.WorkflowExecutionInfo` which contains the
                 information about the workflow execution.
    """
    return proto_to_workflow_execution(get_ai_flow_client().get_workflow_execution(execution_id))


def start_job_execution(job_name: Text,
                        execution_id: Text) -> JobExecutionInfo:
    """
    Starts the job execution by the scheduler with the given name of job and id of corresponding workflow execution. The
    start of the job execution is delegated to the :class:`~ai_flow.plugin_interface.scheduler_interface.Scheduler` in
    Scheduler Service, that runs the job based on the corresponding workflow execution.

    :param job_name: The name of the job.
    :param execution_id: The id of corresponding workflow execution.
    :return: The :class:`~ai_flow.plugin_interface.scheduler_interface.JobExecutionInfo` which contains the information
                 about the started job execution.
    """
    return proto_to_job(get_ai_flow_client().start_job(job_name, execution_id))


def stop_job_execution(job_name: Text,
                       execution_id: Text) -> JobExecutionInfo:
    """
    Stops the job execution by the scheduler with the given name of job and id of corresponding workflow execution. The
    stop of the job execution is delegated to the :class:`~ai_flow.plugin_interface.scheduler_interface.Scheduler` in
    Scheduler Service, that stops the job running.
    
    :param job_name: The name of the job.
    :param execution_id: The id of corresponding workflow execution.
    :return: The :class:`~ai_flow.plugin_interface.scheduler_interface.JobExecutionInfo` which contains the information
                 about the stopped job execution.
    """
    return proto_to_job(get_ai_flow_client().stop_job(job_name, execution_id))


def restart_job_execution(job_name: Text,
                          execution_id: Text) -> JobExecutionInfo:
    """
    Restarts the job execution by the scheduler with the given name of job and id of corresponding workflow execution.
    The restart of the job execution is delegated to the :class:`~ai_flow.plugin_interface.scheduler_interface.Scheduler`
    in Scheduler Service, that reruns the job based on the corresponding workflow execution.
    
    :param job_name: The name of the job.
    :param execution_id: The id of corresponding workflow execution.
    :return: The :class:`~ai_flow.plugin_interface.scheduler_interface.JobExecutionInfo` which contains the information
                 about the restarted job execution.
    """
    return proto_to_job(get_ai_flow_client().restart_job(job_name, execution_id))


def list_job_executions(execution_id: Text) -> List[JobExecutionInfo]:
    """
    Lists the :class:`~ai_flow.plugin_interface.scheduler_interface.JobExecutionInfo` with the given id of workflow
    execution.

    :param execution_id: The id of the workflow execution.
    :return: List of the :class:`~ai_flow.plugin_interface.scheduler_interface.JobExecutionInfo`.
    """
    return proto_to_job_list(get_ai_flow_client().list_jobs(execution_id))


def get_job_execution(job_name: Text,
                      execution_id: Text) -> JobExecutionInfo:
    """
    Gets the :class:`~ai_flow.plugin_interface.scheduler_interface.JobExecutionInfo` with the given name of job and
    id of corresponding workflow execution.

    :param job_name: The name of the job.
    :param execution_id: The id of corresponding workflow execution.
    :return: The :class:`~ai_flow.plugin_interface.scheduler_interface.JobExecutionInfo` which contains the information
                 about the job execution.
    """
    return proto_to_job(get_ai_flow_client().get_job(job_name, execution_id))
