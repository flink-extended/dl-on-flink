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
from ai_flow.protobuf.deploy_service_pb2_grpc import DeployServiceServicer
from ai_flow.protobuf.deploy_service_pb2 import ScheduleResponse, WorkflowRequest, MasterConfigResponse
from ai_flow.endpoint.client.aiflow_client import _SERVER_URI
from ai_flow.deployer.scheduler import SchedulerManager
from ai_flow.workflow.workflow import Workflow
from ai_flow.util.json_utils import loads
import logging


class DeployService(DeployServiceServicer):

    def __init__(self, server_uri=_SERVER_URI):
        self.scheduler_manager = SchedulerManager(server_uri=server_uri)

    def startScheduleWorkflow(self, request, context):
        try:
            rq: WorkflowRequest = request
            workflow_json = rq.workflow_json
            workflow: Workflow = loads(workflow_json)
            workflow_id = self.scheduler_manager.schedule_workflow(workflow=workflow)
            return ScheduleResponse(return_code=0, return_msg='', data=str(workflow_id))
        except Exception as err:
            logging.error(err.args)
            return ScheduleResponse(return_code=1, return_msg=str(err), data='0')

    def stopScheduleWorkflow(self, request, context):
        try:
            rq: WorkflowRequest = request
            workflow_id = rq.id
            self.scheduler_manager.stop_schedule_workflow(workflow_id=workflow_id)
            return ScheduleResponse(return_code=0, return_msg='', data=str(workflow_id))
        except Exception as err:
            return ScheduleResponse(return_code=1, return_msg=str(err), data='0')

    def getWorkflowExecutionResult(self, request, context):
        try:
            rq: WorkflowRequest = request
            workflow_id = rq.id
            res = self.scheduler_manager.get_schedule_result(workflow_id=workflow_id)
            if res is None:
                res = 0
            return ScheduleResponse(return_code=0, return_msg='', data=str(res))
        except Exception as err:
            return ScheduleResponse(return_code=1, return_msg=str(err), data='0')

    def isWorkflowExecutionAlive(self, request, context):
        try:
            rq: WorkflowRequest = request
            workflow_id = rq.id
            res = self.scheduler_manager.workflow_is_alive(workflow_id=workflow_id)
            if res is None:
                return ScheduleResponse(return_code=1,
                                        return_msg='no such workflow execution: {}'.format(workflow_id), data='')
            else:
                return ScheduleResponse(return_code=0, return_msg='', data=str(res))
        except Exception as err:
            return ScheduleResponse(return_code=1, return_msg=str(err), data=str(False))

    def getMasterConfig(self, request, context):
        try:
            from ai_flow.application_master.master import GLOBAL_MASTER_CONFIG
            config = {}
            for key, value in GLOBAL_MASTER_CONFIG.items():
                config[key] = str(value)
            master_config_response = MasterConfigResponse(return_code=0, return_msg='', config=config)
            return master_config_response
        except Exception as err:
            return ScheduleResponse(return_code=1, return_msg=str(err), config={})

    def start_scheduler_manager(self):
        self.scheduler_manager.start()

    def stop_scheduler_manager(self):
        self.scheduler_manager.stop()
