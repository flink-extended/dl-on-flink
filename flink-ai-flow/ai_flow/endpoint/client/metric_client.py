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
from typing import Text, Tuple, Optional, Union, List

import grpc

from ai_flow.common.properties import Properties
from ai_flow.meta.metric_meta import MetricMeta, MetricSummary, MetricType
from ai_flow.metric.utils import proto_to_metric_meta, proto_to_metric_summary
from ai_flow.protobuf import metric_service_pb2, metric_service_pb2_grpc, message_pb2
from ai_flow.protobuf.message_pb2 import ReturnCode
from ai_flow.endpoint.server import stringValue, int64Value
from ai_flow.endpoint.client.base_client import BaseClient


class MetricClient(BaseClient):
    def __init__(self, server_uri):
        super(MetricClient, self).__init__(server_uri)
        channel = grpc.insecure_channel(server_uri)
        self.metric_stub = metric_service_pb2_grpc.MetricServiceStub(channel)

    def register_metric_meta(self,
                             name: Text,
                             dataset_id: int,
                             model_name: Optional[Text],
                             model_version: Optional[Text],
                             job_id: int,
                             start_time: int,
                             end_time: int,
                             metric_type: MetricType,
                             uri: Text,
                             tags: Text,
                             metric_description: Text,
                             properties: Properties,
                             ) -> Tuple[int, Text, Optional[MetricMeta]]:

        request = metric_service_pb2.MetricMetaRequest(
            metric_meta=message_pb2.MetricMetaProto(
                name=stringValue(name),
                dataset_id=int64Value(dataset_id),
                model_name=stringValue(model_name),
                model_version=stringValue(model_version),
                job_id=int64Value(job_id),
                start_time=int64Value(start_time),
                end_time=int64Value(end_time),
                metric_type=message_pb2.MetricTypeProto.Value(metric_type.value),
                uri=stringValue(uri),
                tags=stringValue(tags),
                metric_description=stringValue(metric_description),
                properties=properties)
        )
        response = self.metric_stub.registerMetricMeta(request)
        if 0 == response.return_code:
            metric_meta_proto = response.metric_meta
            metric_meta = proto_to_metric_meta(metric_meta_proto)
            return response.return_code, response.return_msg, metric_meta
        else:
            return response.return_code, response.return_msg, None

    def update_metric_meta(self,
                           uuid: int,
                           name: Text = None,
                           dataset_id: int = None,
                           model_name: Optional[Text] = None,
                           model_version: Optional[Text] = None,
                           job_id: int = None,
                           start_time: int = None,
                           end_time: int = None,
                           metric_type: MetricType = MetricType.DATASET,
                           uri: Text = None,
                           tags: Text = None,
                           metric_description: Text = None,
                           properties: Properties = None,
                           ) -> Tuple[int, Text, Optional[MetricMeta]]:

        pb_metric_type = message_pb2.MetricTypeProto.Value(metric_type.value)
        request = metric_service_pb2.MetricMetaRequest(
            metric_meta=message_pb2.MetricMetaProto(
                uuid=uuid,
                name=stringValue(name),
                dataset_id=int64Value(dataset_id),
                model_name=stringValue(model_name),
                model_version=stringValue(model_version),
                job_id=int64Value(job_id),
                start_time=int64Value(start_time),
                end_time=int64Value(end_time),
                metric_type=pb_metric_type,
                uri=stringValue(uri),
                tags=stringValue(tags),
                metric_description=stringValue(metric_description),
                properties=properties)
        )
        response = self.metric_stub.updateMetricMeta(request)
        if 0 == response.return_code:
            metric_meta_proto = response.metric_meta
            metric_meta = proto_to_metric_meta(metric_meta_proto)
            return response.return_code, response.return_msg, metric_meta
        else:
            return response.return_code, response.return_msg, None

    def delete_metric_meta(self, uuid: int):
        request = metric_service_pb2.UuidRequest(uuid=uuid)
        response = self.metric_stub.deleteMetricMeta(request)
        if response.return_code == str(ReturnCode.SUCCESS):
            return True
        else:
            return False

    def get_metric_meta(self, name: Text) -> Tuple[int, Text, Union[None, MetricMeta]]:
        request = metric_service_pb2.GetMetricMetaRequest(metric_name=name)
        response = self.metric_stub.getMetricMeta(request)

        if 0 == response.return_code:
            metric_meta_proto = response.metric_meta
            metric_meta = proto_to_metric_meta(metric_meta_proto)
            return response.return_code, response.return_msg, metric_meta
        else:
            return response.return_code, response.return_msg, None

    def get_dataset_metric_meta(self, dataset_id: int) -> Tuple[int, Text, Union[None, MetricMeta, List[MetricMeta]]]:
        request = metric_service_pb2.GetDataSetMetricMetaRequest(dataset_id=dataset_id)
        response = self.metric_stub.getDatasetMetricMeta(request)

        if 0 == response.return_code:
            repeated_metric_meta_proto = response.metric_meta
            if 1 == len(repeated_metric_meta_proto):
                metric_meta = proto_to_metric_meta(repeated_metric_meta_proto[0])
                return response.return_code, response.return_msg, metric_meta
            else:
                res = []
                for metric_meta_proto in repeated_metric_meta_proto:
                    res.append(proto_to_metric_meta(metric_meta_proto))
                return response.return_code, response.return_msg, res

        else:
            return response.return_code, response.return_msg, None

    def get_model_metric_meta(self, model_name, model_version) \
            -> Tuple[int, Text, Union[None, MetricMeta, List[MetricMeta]]]:
        request = metric_service_pb2.GetModelMetricMetaRequest(model_name=model_name, model_version=model_version)
        response = self.metric_stub.getModelMetricMeta(request)

        if 0 == response.return_code:
            repeated_metric_meta_proto = response.metric_meta
            if 1 == len(repeated_metric_meta_proto):
                metric_meta = proto_to_metric_meta(repeated_metric_meta_proto[0])
                return response.return_code, response.return_msg, metric_meta
            else:
                res = []
                for metric_meta_proto in repeated_metric_meta_proto:
                    res.append(proto_to_metric_meta(metric_meta_proto))
                return response.return_code, response.return_msg, res

        else:
            return response.return_code, response.return_msg, None

    def register_metric_summary(self,
                                metric_id: int,
                                metric_key: Text,
                                metric_value: Text
                                ) -> Tuple[int, Text, Optional[MetricSummary]]:

        request = metric_service_pb2.MetricSummaryRequest(
            metric_summary=message_pb2.MetricSummaryProto(
                metric_id=int64Value(metric_id),
                metric_key=stringValue(metric_key),
                metric_value=stringValue(metric_value))
        )
        response = self.metric_stub.registerMetricSummary(request)
        if 0 == response.return_code:
            metric_summary_proto = response.metric_summary
            metric_summary = proto_to_metric_summary(metric_summary_proto)
            return response.return_code, response.return_msg, metric_summary
        else:
            return response.return_code, response.return_msg, None

    def update_metric_summary(self,
                              uuid: int,
                              metric_id: int = None,
                              metric_key: Text = None,
                              metric_value: Text = None
                              ) -> Tuple[int, Text, Optional[MetricSummary]]:

        request = metric_service_pb2.MetricSummaryRequest(
            metric_summary=message_pb2.MetricSummaryProto(
                uuid=uuid,
                metric_id=int64Value(metric_id),
                metric_key=stringValue(metric_key),
                metric_value=stringValue(metric_value))
        )
        response = self.metric_stub.updateMetricSummary(request)
        if 0 == response.return_code:
            metric_summary_proto = response.metric_summary
            metric_summary = proto_to_metric_summary(metric_summary_proto)
            return response.return_code, response.return_msg, metric_summary
        else:
            return response.return_code, response.return_msg, None

    def delete_metric_summary(self, uuid: int):
        request = metric_service_pb2.UuidRequest(uuid=uuid)
        response = self.metric_stub.deleteMetricSummary(request)
        if response.return_code == str(ReturnCode.SUCCESS):
            return True
        else:
            return False

    def get_metric_summary(self, metric_id: int) \
            -> Tuple[int, Text, Union[None, List[MetricSummary]]]:
        request = metric_service_pb2.GetMetricSummaryRequest(metric_id=metric_id)
        response = self.metric_stub.getMetricSummary(request)
        if 0 == response.return_code:
            repeated_metric_summary_proto = response.metric_summary
            if 0 == len(repeated_metric_summary_proto):
                return response.return_code, response.return_msg, None
            else:
                res = []
                for metric_summary_proto in repeated_metric_summary_proto:
                    res.append(proto_to_metric_summary(metric_summary_proto))
                return response.return_code, response.return_msg, res

        else:
            return response.return_code, response.return_msg, None
