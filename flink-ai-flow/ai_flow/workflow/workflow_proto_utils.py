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

from ai_flow.rest_endpoint.protobuf.message_pb2 import WorkflowProto, WorkflowExecutionProto, StateProto, JobProto
from ai_flow.workflow.workflow import WorkflowInfo, WorkflowExecutionInfo, JobInfo


def workflow_to_proto(workflow: WorkflowInfo) -> WorkflowProto:
    if workflow is None:
        return None
    return WorkflowProto(workflow_name=workflow.workflow_name)


def workflow_list_to_proto(workflow_list: List[WorkflowInfo]) -> List[WorkflowProto]:
    result = []
    for workflow in workflow_list:
        result.append(workflow_to_proto(workflow))
    return result


def workflow_execution_to_proto(workflow_execution: WorkflowExecutionInfo) -> WorkflowExecutionProto:
    return WorkflowExecutionProto(excution_id=workflow_execution.execution_id,
                                  state=StateProto.Value(workflow_execution.state.value),
                                  workflow=workflow_to_proto(workflow_execution.workflow_info))


def workflow_execution_list_to_proto(workflow_execution_list: List[WorkflowExecutionInfo]) \
        -> List[WorkflowExecutionProto]:
    result = []
    for workflow_execution in workflow_execution_list:
        result.append(workflow_execution_to_proto(workflow_execution))
    return result


def job_to_proto(job: JobInfo) -> JobProto:
    return JobProto(name=job.job_name,
                    state=StateProto.Value(job.state.value),
                    workflow_execution=workflow_execution_to_proto(job.workflow_execution))


def job_list_to_proto(job_list: List[JobInfo]) -> List[JobProto]:
    result = []
    for job in job_list:
        result.append(job_to_proto(job))
    return result
