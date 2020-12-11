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
from notification_service.base_notification import BaseEvent
from ai_flow.notification.event_types import AI_FLOW_TYPE
from ai_flow.rest_endpoint.service.client.deploy_client import DeployClient
from ai_flow.rest_endpoint.service.client.metadata_client import MetadataClient
from ai_flow.rest_endpoint.service.client.model_center_client import ModelCenterClient
from notification_service.client import NotificationClient
from ai_flow.rest_endpoint.service.client.metric_client import MetricClient

_SERVER_URI = 'localhost:50051'


class AIFlowClient(MetadataClient, ModelCenterClient, NotificationClient, DeployClient, MetricClient):
    """
    Client of an AIFlow Server that manages metadata store, model center and notification service.
    """

    def __init__(self, server_uri=_SERVER_URI, notification_service_uri=None):
        MetadataClient.__init__(self, server_uri)
        ModelCenterClient.__init__(self, server_uri)
        DeployClient.__init__(self, server_uri)
        MetricClient.__init__(self, server_uri)
        if notification_service_uri is None:
            NotificationClient.__init__(self, server_uri)
        else:
            NotificationClient.__init__(self, notification_service_uri)

    def publish_event(self, key: str, value: str, event_type: str = AI_FLOW_TYPE) -> BaseEvent:
        return self.send_event(BaseEvent(key, value, event_type))
