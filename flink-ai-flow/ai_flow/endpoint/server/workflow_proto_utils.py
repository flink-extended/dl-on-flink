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
from typing import List

from ai_flow.endpoint.server import stringValue, int64Value
from ai_flow.protobuf.message_pb2 import WorkflowProto, WorkflowExecutionProto, StateProto, JobProto
from ai_flow.plugin_interface.scheduler_interface import WorkflowInfo, WorkflowExecutionInfo, JobExecutionInfo
from ai_flow.workflow.status import Status


def proto_to_state(state):
    if state == StateProto.INIT:
        return Status.INIT
    elif state == StateProto.STARTING:
        return Status.STARTING
    elif state == StateProto.RUNNING:
        return Status.RUNNING
    elif state == StateProto.FINISHED:
        return Status.FINISHED
    elif state == StateProto.FAILED:
        return Status.FAILED
    elif state == StateProto.KILLING:
        return Status.KILLING
    elif state == StateProto.KILLED:
        return Status.KILLED


def workflow_to_proto(workflow: WorkflowInfo) -> WorkflowProto:
    if workflow is None:
        return None
    wp = WorkflowProto(name=workflow.workflow_name, namespace=workflow.namespace)
    for k, v in workflow.properties.items():
        wp.properties[k] = v
    return wp


def proto_to_workflow(proto: WorkflowProto) -> WorkflowInfo:
    if proto is None:
        return None
    else:
        return WorkflowInfo(namespace=proto.namespace, workflow_name=proto.name, properties=dict(proto.properties))


def workflow_list_to_proto(workflow_list: List[WorkflowInfo]) -> List[WorkflowProto]:
    result = []
    for workflow in workflow_list:
        result.append(workflow_to_proto(workflow))
    return result


def proto_to_workflow_list(proto_list: List[WorkflowProto]) -> List[WorkflowInfo]:
    result = []
    for proto in proto_list:
        result.append(proto_to_workflow(proto))
    return result


def workflow_execution_to_proto(workflow_execution: WorkflowExecutionInfo) -> WorkflowExecutionProto:
    if workflow_execution is None:
        return None
    if workflow_execution.status is None:
        state = Status.INIT
    else:
        state = workflow_execution.status
    if workflow_execution.start_date is None:
        start_date = '0'
    else:
        start_date = workflow_execution.start_date

    if workflow_execution.end_date is None:
        end_date = '0'
    else:
        end_date = workflow_execution.end_date

    wp = WorkflowExecutionProto(execution_id=workflow_execution.workflow_execution_id,
                                execution_state=StateProto.Value(state),
                                start_time=int64Value(int(start_date)),
                                end_time=int64Value(int(end_date)),
                                workflow=workflow_to_proto(workflow_execution.workflow_info))
    for k, v in workflow_execution.properties.items():
        wp.properties[k] = v
    return wp


def proto_to_workflow_execution(proto: WorkflowExecutionProto) -> WorkflowExecutionInfo:
    if proto is None:
        return None
    else:
        return WorkflowExecutionInfo(workflow_execution_id=proto.execution_id,
                                     status=proto_to_state(proto.execution_state),
                                     start_date=str(proto.start_time.value),
                                     end_date=str(proto.end_time.value),
                                     workflow_info=proto_to_workflow(proto.workflow),
                                     properties=dict(proto.properties))


def workflow_execution_list_to_proto(workflow_execution_list: List[WorkflowExecutionInfo]) \
        -> List[WorkflowExecutionProto]:
    result = []
    for workflow_execution in workflow_execution_list:
        result.append(workflow_execution_to_proto(workflow_execution))
    return result


def proto_to_workflow_execution_list(proto_list: List[WorkflowExecutionProto]) -> List[WorkflowExecutionInfo]:
    result = []
    for proto in proto_list:
        result.append(proto_to_workflow_execution(proto))
    return result


def job_to_proto(job: JobExecutionInfo) -> JobProto:
    if job.status is None:
        state = Status.INIT
    else:
        state = job.status

    if job.start_date is None:
        start_date = '0'
    else:
        start_date = job.start_date

    if job.end_date is None:
        end_date = '0'
    else:
        end_date = job.end_date

    return JobProto(name=job.job_name,
                    job_id=stringValue(job.job_execution_id),
                    job_state=StateProto.Value(state),
                    start_time=int64Value(int(start_date)),
                    end_time=int64Value(int(end_date)),
                    properties=dict(job.properties),
                    workflow_execution=workflow_execution_to_proto(job.workflow_execution))


def proto_to_job(proto: JobProto) -> JobExecutionInfo:
    if proto is None:
        return None
    else:
        return JobExecutionInfo(job_name=proto.name,
                                job_execution_id=proto.job_id.value,
                                status=proto_to_state(proto.job_state),
                                start_date=str(proto.start_time.value),
                                end_date=str(proto.end_time.value),
                                properties=dict(proto.properties),
                                workflow_execution=proto_to_workflow_execution(proto.workflow_execution))


def job_list_to_proto(job_list: List[JobExecutionInfo]) -> List[JobProto]:
    result = []
    for job in job_list:
        result.append(job_to_proto(job))
    return result


def proto_to_job_list(proto_list: List[JobProto]) -> List[JobExecutionInfo]:
    result = []
    for proto in proto_list:
        result.append(proto_to_job(proto))
    return result
