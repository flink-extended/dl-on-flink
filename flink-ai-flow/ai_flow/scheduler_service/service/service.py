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
import logging
import traceback
from typing import Text

from ai_flow.api.context_extractor import WORKFLOW_EXECUTION_DEFAULT_CONTEXT
from ai_flow.context.project_context import ProjectContext, build_project_context
from ai_flow.endpoint.server.workflow_proto_utils import workflow_to_proto, workflow_execution_to_proto, \
    workflow_execution_list_to_proto, job_to_proto, job_list_to_proto
from ai_flow.plugin_interface.blob_manager_interface import BlobConfig, BlobManagerFactory
from ai_flow.plugin_interface.scheduler_interface import Scheduler, SchedulerFactory, WorkflowInfo
from ai_flow.protobuf.message_pb2 import ResultProto, StatusProto
from ai_flow.protobuf.scheduling_service_pb2 import \
    (ScheduleWorkflowRequest,
     WorkflowInfoResponse,
     WorkflowExecutionRequest,
     WorkflowExecutionResponse,
     ListWorkflowExecutionResponse,
     ScheduleJobRequest,
     JobInfoResponse,
     ListJobInfoResponse, WorkflowExecutionOnEventRequest)
from ai_flow.protobuf.scheduling_service_pb2_grpc import SchedulingServiceServicer
from ai_flow.scheduler_service.service.config import SchedulerServiceConfig
from ai_flow.scheduler_service.service.workflow_event_manager import WorkflowEventManager
from ai_flow.store.db.db_util import create_db_store
from ai_flow.util import json_utils
from ai_flow.workflow.control_edge import WorkflowAction
from ai_flow.workflow.workflow import Workflow
from ai_flow.workflow.workflow import WorkflowPropertyKeys


class SchedulerService(SchedulingServiceServicer):
    def __init__(self,
                 scheduler_service_config: SchedulerServiceConfig,
                 db_uri,
                 notification_uri):
        self._scheduler_service_config = scheduler_service_config
        self._scheduler: Scheduler \
            = SchedulerFactory.create_scheduler(scheduler_service_config.scheduler().scheduler_class(),
                                                scheduler_service_config.scheduler().scheduler_config())
        self.store = create_db_store(db_uri)

        if notification_uri is not None:
            self.workflow_event_manager = WorkflowEventManager(notification_uri=notification_uri,
                                                               db_uri=db_uri,
                                                               scheduler_service_config=scheduler_service_config)
        else:
            self.workflow_event_manager = None
            logging.warning('notification_uri is None, workflow event manager did not start. '
                            'WorkflowExecution will not start/stop on events')

    def start(self):
        if self.workflow_event_manager:
            self.workflow_event_manager.start()

    def stop(self):
        logging.info("stopping SchedulerService.")
        if self.workflow_event_manager:
            self.workflow_event_manager.stop()
        logging.info("SchedulerService stopped.")

    # workflow interface
    def submitWorkflow(self, request, context):
        try:
            rq: ScheduleWorkflowRequest = request
            if rq.workflow_json is None or '' == rq.workflow_json:
                return WorkflowInfoResponse(result=ResultProto(status=StatusProto.ERROR,
                                                               error_message='workflow json is empty!'))
            workflow: Workflow = json_utils.loads(rq.workflow_json)
            raw_config = {}
            raw_config.update(workflow.properties[WorkflowPropertyKeys.BLOB])
            blob_config = BlobConfig(raw_config)
            blob_manager = BlobManagerFactory.create_blob_manager(blob_config.blob_manager_class(),
                                                                  blob_config.blob_manager_config())
            project_path: Text = blob_manager \
                .download_project(workflow_snapshot_id=workflow.workflow_snapshot_id,
                                  remote_path=workflow.project_uri,
                                  local_path=self._scheduler_service_config.repository())

            project_context: ProjectContext = build_project_context(project_path)
            project_name = project_context.project_name

            workflow_meta = \
                self.store.get_workflow_by_name(project_name=project_name, workflow_name=rq.workflow_name)
            workflow_info = self._scheduler.submit_workflow(workflow, workflow_meta.get_context_extractor(),
                                                            project_context)
            if workflow_info is None:
                return WorkflowInfoResponse(
                    result=ResultProto(status=StatusProto.ERROR,
                                       error_message='{}, {} do not exist!'.format(project_name,
                                                                                   workflow.workflow_name)))
            return WorkflowInfoResponse(result=ResultProto(status=StatusProto.OK),
                                        workflow=workflow_to_proto(workflow_info))
        except Exception as err:
            return WorkflowInfoResponse(result=ResultProto(status=StatusProto.ERROR,
                                                           error_message=traceback.format_exc()))

    def deleteWorkflow(self, request, context):
        try:
            rq: ScheduleWorkflowRequest = request
            workflow_info = self._scheduler.delete_workflow(rq.namespace, rq.workflow_name)
            if workflow_info is None:
                return WorkflowInfoResponse(
                    result=ResultProto(status=StatusProto.ERROR,
                                       error_message='{} do not exist!'.format(rq.workflow_name)))
            return WorkflowInfoResponse(result=ResultProto(status=StatusProto.OK),
                                        workflow=workflow_to_proto(workflow_info))
        except Exception as err:
            return WorkflowInfoResponse(result=ResultProto(status=StatusProto.ERROR,
                                                           error_message=traceback.format_exc()))

    def pauseWorkflowScheduling(self, request, context):
        try:
            rq: ScheduleWorkflowRequest = request
            workflow_info = self._scheduler.pause_workflow_scheduling(rq.namespace, rq.workflow_name)
            if workflow_info is None:
                return WorkflowInfoResponse(
                    result=ResultProto(status=StatusProto.ERROR,
                                       error_message='{} do not exist!'.format(rq.workflow_name)))
            return WorkflowInfoResponse(result=ResultProto(status=StatusProto.OK),
                                        workflow=workflow_to_proto(workflow_info))
        except Exception as err:
            return WorkflowInfoResponse(result=ResultProto(status=StatusProto.ERROR,
                                                           error_message=traceback.format_exc()))

    def resumeWorkflowScheduling(self, request, context):
        try:
            rq: ScheduleWorkflowRequest = request
            workflow_info = self._scheduler.resume_workflow_scheduling(rq.namespace, rq.workflow_name)
            if workflow_info is None:
                return WorkflowInfoResponse(
                    result=ResultProto(status=StatusProto.ERROR,
                                       error_message='{} do not exist!'.format(rq.workflow_name)))
            return WorkflowInfoResponse(result=ResultProto(status=StatusProto.OK),
                                        workflow=workflow_to_proto(workflow_info))
        except Exception as err:
            return WorkflowInfoResponse(result=ResultProto(status=StatusProto.ERROR,
                                                           error_message=traceback.format_exc()))

    def getWorkflow(self, request, context):
        return WorkflowInfoResponse(result=ResultProto(status=StatusProto.ERROR,
                                                       error_message='Do not support getWorkflow'))

    def listWorkflows(self, request, context):
        return WorkflowInfoResponse(result=ResultProto(status=StatusProto.ERROR,
                                                       error_message='Do not support listWorkflows'))

    # workflow execution interface

    def startNewWorkflowExecutionOnEvent(self, request, context):
        try:
            rq: WorkflowExecutionOnEventRequest = request
            namespace = rq.namespace
            workflow_name = rq.workflow_name
            event_conditions_json = rq.event_conditions_json
            workflow = self.store.get_workflow_by_name(namespace, workflow_name)
            workflow.update_condition(json_utils.loads(event_conditions_json), WorkflowAction.START)
            self.store.update_workflow(project_name=namespace, workflow_name=workflow_name,
                                       context_extractor_in_bytes=workflow.context_extractor_in_bytes,
                                       scheduling_rules=workflow.scheduling_rules)
            context_state = self.store \
                .get_workflow_context_event_handler_state(project_name=namespace,
                                                          workflow_name=workflow_name,
                                                          context=WORKFLOW_EXECUTION_DEFAULT_CONTEXT)
            if context_state is None:
                self.store.register_workflow_context_event_handler_state(
                    project_name=namespace,
                    workflow_name=workflow_name,
                    context=WORKFLOW_EXECUTION_DEFAULT_CONTEXT)

            workflow_info = WorkflowInfo(namespace=namespace, workflow_name=workflow_name)
            return WorkflowInfoResponse(result=ResultProto(status=StatusProto.OK),
                                        workflow=workflow_to_proto(workflow_info))
        except Exception as err:
            return WorkflowInfoResponse(result=ResultProto(status=StatusProto.ERROR,
                                                           error_message=traceback.format_exc()))

    def startNewWorkflowExecution(self, request, context):
        try:
            rq: WorkflowExecutionRequest = request
            context = rq.context.value if rq.HasField('context') else None
            workflow_execution = self._scheduler.start_new_workflow_execution(rq.namespace, rq.workflow_name,
                                                                              context)
            if workflow_execution is None:
                return WorkflowInfoResponse(
                    result=ResultProto(status=StatusProto.ERROR,
                                       error_message='{}, {} do not exist!'.format(rq.namespace, rq.workflow_name)))
            return WorkflowExecutionResponse(result=ResultProto(status=StatusProto.OK),
                                             workflow_execution=workflow_execution_to_proto(workflow_execution))
        except Exception as err:
            return WorkflowExecutionResponse(result=ResultProto(status=StatusProto.ERROR,
                                                                error_message=traceback.format_exc()))

    def killAllWorkflowExecutions(self, request, context):
        try:
            rq: WorkflowExecutionRequest = request
            workflow_execution_list = self._scheduler.stop_all_workflow_execution(rq.namespace, rq.workflow_name)
            response = ListWorkflowExecutionResponse(result=ResultProto(status=StatusProto.OK))
            response.workflow_execution_list.extend(workflow_execution_list_to_proto(workflow_execution_list))
            return response
        except Exception as err:
            return ListWorkflowExecutionResponse(result=ResultProto(status=StatusProto.ERROR,
                                                                    error_message=traceback.format_exc()))

    def killWorkflowExecutionOnEvent(self, request, context):
        try:
            rq: WorkflowExecutionOnEventRequest = request
            namespace = rq.namespace
            workflow_name = rq.workflow_name
            event_conditions_json = rq.event_conditions_json
            workflow = self.store.get_workflow_by_name(namespace, workflow_name)
            workflow.update_condition(json_utils.loads(event_conditions_json), WorkflowAction.STOP)
            self.store.update_workflow(project_name=namespace, workflow_name=workflow_name,
                                       context_extractor_in_bytes=workflow.context_extractor_in_bytes,
                                       scheduling_rules=workflow.scheduling_rules)
            context_state = self.store \
                .get_workflow_context_event_handler_state(project_name=namespace,
                                                          workflow_name=workflow_name,
                                                          context=WORKFLOW_EXECUTION_DEFAULT_CONTEXT)
            if context_state is None:
                self.store.register_workflow_context_event_handler_state(
                    project_name=namespace,
                    workflow_name=workflow_name,
                    context=WORKFLOW_EXECUTION_DEFAULT_CONTEXT)

            workflow_info = WorkflowInfo(namespace=namespace, workflow_name=workflow_name)
            return WorkflowInfoResponse(result=ResultProto(status=StatusProto.OK),
                                        workflow=workflow_to_proto(workflow_info))
        except Exception as err:
            return WorkflowExecutionResponse(result=ResultProto(status=StatusProto.ERROR,
                                                                error_message=traceback.format_exc()))

    def killWorkflowExecution(self, request, context):
        try:
            rq: WorkflowExecutionRequest = request
            workflow_execution = self._scheduler.stop_workflow_execution(rq.execution_id)
            if workflow_execution is None:
                return WorkflowExecutionResponse(
                    result=ResultProto(status=StatusProto.ERROR,
                                       error_message='{} do not exist!'.format(rq.execution_id)))
            return WorkflowExecutionResponse(result=ResultProto(status=StatusProto.OK),
                                             workflow_execution=workflow_execution_to_proto(workflow_execution))
        except Exception as err:
            return WorkflowExecutionResponse(result=ResultProto(status=StatusProto.ERROR,
                                                                error_message=traceback.format_exc()))

    def getWorkflowExecution(self, request, context):
        try:
            rq: WorkflowExecutionRequest = request
            workflow_execution = self._scheduler.get_workflow_execution(rq.execution_id)
            if workflow_execution is None:
                return WorkflowExecutionResponse(
                    result=ResultProto(status=StatusProto.ERROR,
                                       error_message='{} do not exist!'.format(rq.execution_id)))
            return WorkflowExecutionResponse(result=ResultProto(status=StatusProto.OK),
                                             workflow_execution=workflow_execution_to_proto(workflow_execution))
        except Exception as err:
            return WorkflowExecutionResponse(result=ResultProto(status=StatusProto.ERROR,
                                                                error_message=traceback.format_exc()))

    def listWorkflowExecutions(self, request, context):
        try:
            rq: WorkflowExecutionRequest = request
            workflow_execution_list = self._scheduler.list_workflow_executions(rq.namespace, rq.workflow_name)
            response = ListWorkflowExecutionResponse(result=ResultProto(status=StatusProto.OK))
            response.workflow_execution_list.extend(workflow_execution_list_to_proto(workflow_execution_list))
            return response
        except Exception as err:
            return ListWorkflowExecutionResponse(result=ResultProto(status=StatusProto.ERROR,
                                                                    error_message=traceback.format_exc()))

    # job interface
    def startJob(self, request, context):
        try:
            rq: ScheduleJobRequest = request
            job = self._scheduler.start_job_execution(rq.job_name, rq.execution_id)
            if job is None:
                return JobInfoResponse(
                    result=ResultProto(status=StatusProto.ERROR,
                                       error_message='{} do not exist!'.format(rq.job_name)))
            return JobInfoResponse(result=ResultProto(status=StatusProto.OK), job=job_to_proto(job))
        except Exception as err:
            return JobInfoResponse(result=ResultProto(status=StatusProto.ERROR,
                                                      error_message=traceback.format_exc()))

    def stopJob(self, request, context):
        try:
            rq: ScheduleJobRequest = request
            job = self._scheduler.stop_job_execution(rq.job_name, rq.execution_id)
            if job is None:
                return JobInfoResponse(
                    result=ResultProto(status=StatusProto.ERROR,
                                       error_message='{} do not exist!'.format(rq.job_name)))
            return JobInfoResponse(result=ResultProto(status=StatusProto.OK), job=job_to_proto(job))
        except Exception as err:
            return JobInfoResponse(result=ResultProto(status=StatusProto.ERROR,
                                                      error_message=traceback.format_exc()))

    def restartJob(self, request, context):
        try:
            rq: ScheduleJobRequest = request
            job = self._scheduler.restart_job_execution(rq.job_name, rq.execution_id)
            if job is None:
                return JobInfoResponse(
                    result=ResultProto(status=StatusProto.ERROR,
                                       error_message='{} do not exist!'.format(rq.job_name)))
            return JobInfoResponse(result=ResultProto(status=StatusProto.OK), job=job_to_proto(job))
        except Exception as err:
            return JobInfoResponse(result=ResultProto(status=StatusProto.ERROR,
                                                      error_message=traceback.format_exc()))

    def getJob(self, request, context):
        try:
            rq: ScheduleJobRequest = request
            jobs = self._scheduler.get_job_executions(rq.job_name, rq.execution_id)
            if jobs is None:
                return JobInfoResponse(
                    result=ResultProto(status=StatusProto.ERROR,
                                       error_message='{} do not exist!'.format(rq.job_name)))
            return JobInfoResponse(result=ResultProto(status=StatusProto.OK), job=job_to_proto(jobs[0]))
        except Exception as err:
            return JobInfoResponse(result=ResultProto(status=StatusProto.ERROR,
                                                      error_message=traceback.format_exc()))

    def listJobs(self, request, context):
        try:
            rq: ScheduleJobRequest = request
            job_list = self._scheduler.list_job_executions(rq.execution_id)
            response = ListJobInfoResponse(result=ResultProto(status=StatusProto.OK))
            response.job_list.extend(job_list_to_proto(job_list))
            return response
        except Exception as err:
            return ListJobInfoResponse(result=ResultProto(status=StatusProto.ERROR,
                                                          error_message=traceback.format_exc()))
