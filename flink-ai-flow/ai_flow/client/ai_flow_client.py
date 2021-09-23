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
import logging
import threading
import time
from functools import wraps
from random import shuffle
from typing import Text

import grpc
from notification_service.base_notification import BaseEvent
from notification_service.client import NotificationClient
from ai_flow.context.project_context import current_project_config
from ai_flow.endpoint.client.metadata_client import MetadataClient
from ai_flow.endpoint.client.metric_client import MetricClient
from ai_flow.endpoint.client.model_center_client import ModelCenterClient
from ai_flow.endpoint.client.scheduler_client import SchedulerClient
from ai_flow.endpoint.server.high_availability import proto_to_member, sleep_and_detecting_running
from ai_flow.project.project_config import ProjectConfig
from ai_flow.protobuf.high_availability_pb2 import ListMembersRequest, ReturnStatus
from ai_flow.protobuf.high_availability_pb2_grpc import HighAvailabilityManagerStub
from ai_flow.protobuf.metadata_service_pb2_grpc import MetadataServiceStub
from ai_flow.protobuf.metric_service_pb2_grpc import MetricServiceStub
from ai_flow.protobuf.model_center_service_pb2_grpc import ModelCenterServiceStub
from ai_flow.protobuf.scheduling_service_pb2_grpc import SchedulingServiceStub

if not hasattr(time, 'time_ns'):
    time.time_ns = lambda: int(time.time() * 1e9)

AI_FLOW_TYPE = "AI_FLOW"

_SERVER_URI = 'localhost:50051'

_default_ai_flow_client = None
_default_server_uri = 'localhost:50051'

_default_airflow_operation_client = None


def get_ai_flow_client():
    """ Get AI flow Client. """

    global _default_ai_flow_client, _default_server_uri
    if _default_ai_flow_client is None:
        current_uri = current_project_config().get_server_uri()
        if current_uri is None:
            return None
        else:
            _default_server_uri = current_uri
            _default_ai_flow_client \
                = AIFlowClient(server_uri=_default_server_uri,
                               notification_service_uri=current_project_config().get_notification_service_uri(),
                               project_config=current_project_config())
            return _default_ai_flow_client
    else:
        current_uri = current_project_config().get_server_uri()
        if current_uri != _default_server_uri:
            _default_server_uri = current_uri
            _default_ai_flow_client \
                = AIFlowClient(server_uri=_default_server_uri,
                               notification_service_uri=current_project_config().get_notification_service_uri(),
                               project_config=current_project_config())
        else:
            # when reuse previous client, confirm once whether server is available
            _default_ai_flow_client.wait_for_ready_and_throw_error()
        return _default_ai_flow_client


class AIFlowClient(NotificationClient, MetadataClient, ModelCenterClient, MetricClient, SchedulerClient):
    """
    Client of an AIFlow Server that manages metadata store, model center and notification service.
    """
    CLIENT_INIT_WAIT_READY_TIMEOUT = 5.

    def __init__(self,
                 server_uri=_SERVER_URI,
                 notification_service_uri=None,
                 project_config: ProjectConfig = None):
        MetadataClient.__init__(self, server_uri)
        ModelCenterClient.__init__(self, server_uri)
        MetricClient.__init__(self, server_uri)
        SchedulerClient.__init__(self, server_uri)
        self.aiflow_ha_enabled = False
        self.list_member_interval_ms = 5000
        self.retry_interval_ms = 1000
        self.retry_timeout_ms = 10000
        project_name = None
        if project_config is not None:
            if server_uri is None:
                server_uri = project_config.get_server_uri()
            if notification_service_uri is None:
                notification_service_uri = project_config.get_notification_service_uri()
            project_name = project_config.get_project_name()
            self.aiflow_ha_enabled = project_config.get_enable_ha()
            self.list_member_interval_ms = project_config.get_list_member_interval_ms()
            self.retry_interval_ms = project_config.get_retry_interval_ms()
            self.retry_timeout_ms = project_config.get_retry_timeout_ms()
        self.server_uri = server_uri
        self.wait_for_ready_and_throw_error()
        if notification_service_uri is None:
            NotificationClient.__init__(
                self,
                server_uri,
                list_member_interval_ms=self.list_member_interval_ms,
                retry_interval_ms=self.retry_interval_ms,
                retry_timeout_ms=self.retry_timeout_ms,
                default_namespace=project_name)
        else:
            NotificationClient.__init__(
                self,
                notification_service_uri,
                list_member_interval_ms=self.list_member_interval_ms,
                retry_interval_ms=self.retry_interval_ms,
                retry_timeout_ms=self.retry_timeout_ms,
                default_namespace=project_name)
        if self.aiflow_ha_enabled:
            server_uris = server_uri.split(",")
            self.living_aiflow_members = []
            self.current_aiflow_uri = None
            last_error = None
            for server_uri in server_uris:
                channel = grpc.insecure_channel(server_uri)
                high_availability_stub = HighAvailabilityManagerStub(channel)
                try:
                    request = ListMembersRequest(timeout_seconds=0)
                    response = high_availability_stub.listMembers(request)
                    if response.return_code == ReturnStatus.CALL_SUCCESS:
                        self.living_aiflow_members = [proto_to_member(proto).server_uri
                                                      for proto in response.members]
                    else:
                        raise Exception(response.return_msg)
                    self.current_aiflow_uri = server_uri
                    self.high_availability_stub = high_availability_stub
                    break
                except grpc.RpcError as e:
                    last_error = e
            if self.current_aiflow_uri is None:
                raise Exception("No available aiflow server uri!") from last_error
            self.aiflow_ha_change_lock = threading.Lock()
            self.aiflow_ha_running = True
            self._replace_aiflow_stubs(self.current_aiflow_uri)
            self.list_aiflow_member_thread = threading.Thread(target=self._list_aiflow_members, daemon=True)
            self.list_aiflow_member_thread.start()

    def wait_for_ready_and_throw_error(self):
        server_uris = self.server_uri.split(",")
        available = False
        for uri in server_uris:
            try:
                channel = grpc.insecure_channel(uri)
                fut = grpc.channel_ready_future(channel)
                fut.result(self.CLIENT_INIT_WAIT_READY_TIMEOUT)
                available = True
                break
            except:
                pass
        if not available:
            raise Exception(f"Client connection to server({self.server_uri}) is not ready. Please confirm the status of the process for `AIFlowServer`.")

    def publish_event(self, key: str, value: str, event_type: str = AI_FLOW_TYPE) -> BaseEvent:
        return self.send_event(BaseEvent(key, value, event_type))

    def _list_aiflow_members(self):
        while self.aiflow_ha_running:
            # refresh the living members
            request = ListMembersRequest(timeout_seconds=int(self.list_member_interval_ms / 1000))
            response = self.high_availability_stub.listMembers(request)
            if response.return_code == ReturnStatus.CALL_SUCCESS:
                with self.aiflow_ha_change_lock:
                    self.living_aiflow_members = [proto_to_member(proto).server_uri
                                                  for proto in response.members]
            else:
                logging.error("Exception thrown when updating the living members: %s" %
                              response.return_msg)

    def _aiflow_ha_wrapper(self, func, stub_name):
        @wraps(func)
        def call_with_retry(*args, **kwargs):
            current_stub = getattr(self, stub_name)
            current_func = getattr(current_stub, func.__name__).inner_func
            start_time = time.time_ns() / 1000000
            failed_members = set()
            while True:
                try:
                    return current_func(*args, **kwargs)
                except grpc.RpcError:
                    logging.error("Exception thrown when calling rpc, change the connection.",
                                  exc_info=True)
                    with self.aiflow_ha_change_lock:
                        # check the current_uri to ensure thread safety
                        if current_func.server_uri == self.current_aiflow_uri:
                            living_members = list(self.living_aiflow_members)
                            failed_members.add(self.current_aiflow_uri)
                            shuffle(living_members)
                            found_new_member = False
                            for server_uri in living_members:
                                if server_uri in failed_members:
                                    continue
                                next_uri = server_uri

                                self._replace_aiflow_stubs(next_uri)

                                current_func = getattr(getattr(self, stub_name),
                                                       current_func.__name__).inner_func
                                self.current_aiflow_uri = next_uri
                                found_new_member = True
                            if not found_new_member:
                                logging.error("No available living members currently. Sleep and retry.")
                                failed_members.clear()
                                sleep_and_detecting_running(self.retry_interval_ms,
                                                            lambda: self.aiflow_ha_running)

                # break if stopped or timeout
                if not self.aiflow_ha_running or \
                        time.time_ns() / 1000000 > start_time + self.retry_timeout_ms:
                    if not self.aiflow_ha_running:
                        raise Exception("HA has been disabled.")
                    else:
                        raise Exception("Rpc retry timeout!")

        call_with_retry.inner_func = func
        return call_with_retry

    def _wrap_aiflow_rpcs(self, stub, server_uri, stub_name):
        for method_name, method in dict(stub.__dict__).items():
            method.__name__ = method_name
            method.server_uri = server_uri
            setattr(stub, method_name, self._aiflow_ha_wrapper(method, stub_name))
        return stub

    def _replace_aiflow_stubs(self, server_uri):
        high_availability_channel = grpc.insecure_channel(server_uri)
        high_availability_stub = self._wrap_aiflow_rpcs(
            HighAvailabilityManagerStub(high_availability_channel),
            server_uri,
            "high_availability_stub")
        self.high_availability_stub = high_availability_stub

        metadata_channel = grpc.insecure_channel(server_uri)
        metadata_store_stub = self._wrap_aiflow_rpcs(
            MetadataServiceStub(metadata_channel),
            server_uri,
            "metadata_store_stub")
        self.metadata_store_stub = metadata_store_stub

        model_center_channel = grpc.insecure_channel(server_uri)
        model_center_stub = self._wrap_aiflow_rpcs(
            ModelCenterServiceStub(model_center_channel),
            server_uri,
            "model_center_stub")
        self.model_center_stub = model_center_stub

        metric_channel = grpc.insecure_channel(server_uri)
        metric_stub = self._wrap_aiflow_rpcs(
            MetricServiceStub(metric_channel),
            server_uri,
            "metric_stub")
        self.metric_stub = metric_stub

        scheduling_channel = grpc.insecure_channel(server_uri)
        scheduling_stub = self._wrap_aiflow_rpcs(
            SchedulingServiceStub(scheduling_channel),
            server_uri,
            "scheduling_stub")
        self.scheduling_stub = scheduling_stub

    def disable_high_availability(self):
        if hasattr(self, "aiflow_ha_running"):
            self.aiflow_ha_running = False
        NotificationClient.disable_high_availability(self)
        if hasattr(self, "aiflow_ha_running"):
            self.list_aiflow_member_thread.join()
