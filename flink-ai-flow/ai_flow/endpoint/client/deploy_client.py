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
from typing import Text, Tuple
import grpc
from ai_flow.util.bool_util import str_to_bool
from ai_flow.protobuf import deploy_service_pb2, deploy_service_pb2_grpc
from ai_flow.endpoint.client.base_client import BaseClient


class DeployClient(BaseClient):
    def __init__(self, server_uri):
        super(DeployClient, self).__init__(server_uri)
        channel = grpc.insecure_channel(server_uri)
        self.deploy_stub = deploy_service_pb2_grpc.DeployServiceStub(channel)

    def submit_workflow(self, workflow: Text) -> Tuple[int, int, Text]:
        """
        submit ExecutableWorkflow to DeployService
        :param workflow: workflow json
        :return: return_code, workflow_id, message
        """
        request = deploy_service_pb2.WorkflowRequest(id=0, workflow_json=workflow)
        response = self.deploy_stub.startScheduleWorkflow(request)
        return response.return_code, int(response.data), str(response.return_msg)

    def stop_workflow(self, workflow_id: int) -> Tuple[int, int, Text]:
        """
        stop WorkflowExecution
        :param workflow_id: WorkflowExecution uuid
        :return: return_code, workflow_id, message
        """
        request = deploy_service_pb2.WorkflowRequest(id=workflow_id, workflow_json='')
        response = self.deploy_stub.stopScheduleWorkflow(request)
        return response.return_code, int(response.data), str(response.return_msg)

    def get_workflow_execution_result(self, workflow_id: int) -> Tuple[int, int, Text]:
        """
        stop WorkflowExecution
        :param workflow_id: WorkflowExecution uuid
        :return: return_code, schedule result, message
        """
        request = deploy_service_pb2.WorkflowRequest(id=workflow_id, workflow_json='')
        response = self.deploy_stub.getWorkflowExecutionResult(request)
        return response.return_code, int(response.data), str(response.return_msg)

    def is_alive_workflow(self, workflow_id: int) -> Tuple[int, int, Text]:
        """
        stop WorkflowExecution
        :param workflow_id: WorkflowExecution uuid
        :return: return_code, workflow_id, message
        """
        request = deploy_service_pb2.WorkflowRequest(id=workflow_id, workflow_json='')
        response = self.deploy_stub.isWorkflowExecutionAlive(request)
        return response.return_code, str_to_bool(str(response.data)), str(response.return_msg)

    def get_master_config(self):
        request = deploy_service_pb2.MasterConfigRequest(id=0)
        response = self.deploy_stub.getMasterConfig(request)
        return response.return_code, response.config, str(response.return_msg)
