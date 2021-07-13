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
from ai_flow.endpoint.client.base_client import BaseClient
from ai_flow.endpoint.server import int64Value, stringValue
from ai_flow.meta.metric_meta import MetricMeta, MetricSummary, MetricType
from ai_flow.metric.utils import proto_to_metric_meta, proto_to_metric_summary
from ai_flow.protobuf import metric_service_pb2_grpc
from ai_flow.protobuf.message_pb2 import ReturnCode, MetricTypeProto, MetricSummaryProto, MetricMetaProto
from ai_flow.protobuf.metric_service_pb2 import MetricNameRequest, MetricMetaRequest, \
    ListDatasetMetricMetasRequest, ListModelMetricMetasRequest, MetricSummaryRequest, UuidRequest, \
    ListMetricSummariesRequest


class MetricClient(BaseClient):
    def __init__(self, server_uri):
        super(MetricClient, self).__init__(server_uri)
        channel = grpc.insecure_channel(server_uri)
        self.metric_stub = metric_service_pb2_grpc.MetricServiceStub(channel)

    def register_metric_meta(self,
                             metric_name: Text,
                             metric_type: MetricType,
                             project_name: Text,
                             metric_desc: Optional[Text] = None,
                             dataset_name: Optional[Text] = None,
                             model_name: Optional[Text] = None,
                             job_name: Optional[Text] = None,
                             start_time: int = None,
                             end_time: int = None,
                             uri: Optional[Text] = None,
                             tags: Optional[Text] = None,
                             properties: Properties = None
                             ) -> Tuple[int, Text, Optional[MetricMeta]]:
        """
        Register metric metadata in Metric Center.
        
        :param metric_name: Name of registered metric meta. This is expected to be unique in the backend store.
        :param metric_type: Type of registered metric meta.
        :param project_name: Name of the project associated with the registered metric meta.
        :param metric_desc: (Optional) Description of registered metric meta.
        :param dataset_name: (Optional) Name of the dataset associated with the registered metric meta.
        :param model_name: (Optional) Name of the model associated with the registered metric meta.
        :param job_name: (Optional) Name of the job associated with the registered metric meta.
        :param start_time: (Optional) Start time of registered metric meta.
        :param end_time: (Optional) End time of registered metric meta.
        :param uri: (Optional) Uri of registered metric meta.
        :param tags: (Optional) Tags of registered metric meta.
        :param properties: (Optional) Properties of registered metric meta.
        
        :return: A single :py:class:`ai_flow.meta.metric_meta.MetricMeta` object.
        """
        request = MetricMetaRequest(
            metric_meta=MetricMetaProto(
                metric_name=stringValue(metric_name),
                metric_type=MetricTypeProto.Value(metric_type.value),
                metric_desc=stringValue(metric_desc),
                project_name=stringValue(project_name),
                dataset_name=stringValue(dataset_name),
                model_name=stringValue(model_name),
                job_name=stringValue(job_name),
                start_time=int64Value(start_time),
                end_time=int64Value(end_time),
                uri=stringValue(uri),
                tags=stringValue(tags),
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
                           metric_name: Text,
                           project_name: Optional[Text] = None,
                           metric_desc: Optional[Text] = None,
                           dataset_name: Optional[Text] = None,
                           model_name: Optional[Text] = None,
                           job_name: Optional[Text] = None,
                           start_time: int = None,
                           end_time: int = None,
                           uri: Optional[Text] = None,
                           tags: Optional[Text] = None,
                           properties: Properties = None
                           ) -> Tuple[int, Text, Optional[MetricMeta]]:
        """
        Update metric metadata in Metric Center.

        :param metric_name: Name of registered metric meta. This is expected to be unique in the backend store.
        :param project_name: (Optional) Name of the project associated with the registered metric meta.
        :param metric_desc: (Optional) Description of registered metric meta.
        :param dataset_name: (Optional) Name of the dataset associated with the registered metric meta.
        :param model_name: (Optional) Name of the model associated with the registered metric meta.
        :param job_name: (Optional) Name of the job associated with the registered metric meta.
        :param start_time: (Optional) Start time of registered metric meta.
        :param end_time: (Optional) End time of registered metric meta.
        :param uri: (Optional) Uri of registered metric meta.
        :param tags: (Optional) Tags of registered metric meta.
        :param properties: (Optional) Properties of registered metric meta.
        
        :return: A single :py:class:`ai_flow.meta.metric_meta.MetricMeta` object.
        """
        request = MetricMetaRequest(
            metric_meta=MetricMetaProto(
                metric_name=stringValue(metric_name),
                metric_desc=stringValue(metric_desc),
                project_name=stringValue(project_name),
                dataset_name=stringValue(dataset_name),
                model_name=stringValue(model_name),
                job_name=stringValue(job_name),
                start_time=int64Value(start_time),
                end_time=int64Value(end_time),
                uri=stringValue(uri),
                tags=stringValue(tags),
                properties=properties)
        )
        response = self.metric_stub.updateMetricMeta(request)
        if 0 == response.return_code:
            metric_meta_proto = response.metric_meta
            metric_meta = proto_to_metric_meta(metric_meta_proto)
            return response.return_code, response.return_msg, metric_meta
        else:
            return response.return_code, response.return_msg, None

    def delete_metric_meta(self, metric_name: Text) -> bool:
        """
        Delete metric metadata by metric name in Metric Center backend.

        :param metric_name: Name of registered metric meta. This is expected to be unique in the backend store.

        :return: Whether to delete the given metric metadata.
        """
        request = MetricNameRequest(metric_name=metric_name)
        response = self.metric_stub.deleteMetricMeta(request)
        if response.return_code == str(ReturnCode.SUCCESS):
            return True
        else:
            return False

    def get_metric_meta(self, metric_name: Text) -> Tuple[int, Text, Union[None, MetricMeta]]:
        """
        Get metric metadata detail filter by metric name for Metric Center.

        :param metric_name: Name of registered metric meta. This is expected to be unique in the backend store.

       :return: A single :py:class:`ai_flow.meta.metric_meta.MetricMeta` object.
        """
        request = MetricNameRequest(metric_name=metric_name)
        response = self.metric_stub.getMetricMeta(request)

        if 0 == response.return_code:
            metric_meta_proto = response.metric_meta
            metric_meta = proto_to_metric_meta(metric_meta_proto)
            return response.return_code, response.return_msg, metric_meta
        else:
            return response.return_code, response.return_msg, None

    def list_dataset_metric_metas(self, dataset_name: Text, project_name: Optional[Text] = None) -> Tuple[
            int, Text, Union[None, MetricMeta, List[MetricMeta]]]:
        """
        List of dataset metric metadata filter by dataset name and project name for Metric Center.

        :param dataset_name: Name of the dataset associated with the registered metric meta.
        :param project_name: Name of the project associated with the registered metric meta.

        :return: List of :py:class:`ai_flow.meta.metric_meta.MetricMeta` objects.
        """
        request = ListDatasetMetricMetasRequest(dataset_name=dataset_name, project_name=stringValue(project_name))
        response = self.metric_stub.listDatasetMetricMetas(request)

        if 0 == response.return_code:
            repeated_metric_meta_proto = response.metric_metas
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

    def list_model_metric_metas(self, model_name: Text, project_name: Optional[Text] = None) -> Tuple[
            int, Text, Union[None, MetricMeta, List[MetricMeta]]]:
        """
        List of model metric metadata filter by model name and project name for Metric Center.

        :param model_name: Name of the model associated with the registered metric meta.
        :param project_name: Name of the project associated with the registered metric meta.

        :return: List of :py:class:`ai_flow.meta.metric_meta.MetricMeta` objects.
        """
        request = ListModelMetricMetasRequest(model_name=model_name, project_name=stringValue(project_name))
        response = self.metric_stub.listModelMetricMetas(request)
        if 0 == response.return_code:
            repeated_metric_meta_proto = response.metric_metas
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
                                metric_name: Text,
                                metric_key: Text,
                                metric_value: Text,
                                metric_timestamp: int,
                                model_version: Optional[Text] = None,
                                job_execution_id: Optional[Text] = None
                                ) -> Tuple[int, Text, Optional[MetricSummary]]:
        """
        Register metric summary in Metric Center.

        :param metric_name: Name of registered metric summary.
        :param metric_key: Key of registered metric summary.
        :param metric_value: Value of registered metric summary.
        :param metric_timestamp: Timestamp of registered metric summary.
        :param model_version: (Optional) Version of the model version associated with the registered metric summary.
        :param job_execution_id: (Optional) ID of the job execution associated with the registered metric summary.

        :return: A single :py:class:`ai_flow.meta.metric_meta.MetricSummary` object.
        """
        request = MetricSummaryRequest(
            metric_summary=MetricSummaryProto(
                metric_name=stringValue(metric_name),
                metric_key=stringValue(metric_key),
                metric_value=stringValue(metric_value),
                metric_timestamp=int64Value(metric_timestamp),
                model_version=stringValue(model_version),
                job_execution_id=stringValue(job_execution_id))
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
                              metric_name: Optional[Text] = None,
                              metric_key: Optional[Text] = None,
                              metric_value: Optional[Text] = None,
                              metric_timestamp: int = None,
                              model_version: Optional[Text] = None,
                              job_execution_id: Optional[Text] = None
                              ) -> Tuple[int, Text, Optional[MetricSummary]]:
        """
        Update metric summary in Metric Center.

        :param uuid: UUID of registered metric summary.
        :param metric_name: Name of registered metric summary.
        :param metric_key: Key of registered metric summary.
        :param metric_value: (Optional) Value of registered metric summary.
        :param metric_timestamp: (Optional) Timestamp of registered metric summary.
        :param model_version: (Optional) Version of the model version associated with the registered metric summary.
        :param job_execution_id: (Optional) ID of the job execution associated with the registered metric summary.

        :return: A single :py:class:`ai_flow.meta.metric_meta.MetricSummary` object.
        """
        request = MetricSummaryRequest(
            metric_summary=MetricSummaryProto(
                uuid=uuid,
                metric_name=stringValue(metric_name),
                metric_key=stringValue(metric_key),
                metric_value=stringValue(metric_value),
                metric_timestamp=int64Value(metric_timestamp),
                model_version=stringValue(model_version),
                job_execution_id=stringValue(job_execution_id))
        )
        response = self.metric_stub.updateMetricSummary(request)
        if 0 == response.return_code:
            metric_summary_proto = response.metric_summary
            metric_summary = proto_to_metric_summary(metric_summary_proto)
            return response.return_code, response.return_msg, metric_summary
        else:
            return response.return_code, response.return_msg, None

    def delete_metric_summary(self, uuid: int) -> bool:
        """
        Delete metric summary by metric uuid in Metric Center backend.

        :param uuid: UUID of registered metric summary.

        :return: Whether to delete the given metric summary.
        """
        request = UuidRequest(uuid=uuid)
        response = self.metric_stub.deleteMetricSummary(request)
        if response.return_code == str(ReturnCode.SUCCESS):
            return True
        else:
            return False

    def get_metric_summary(self, uuid: int) -> Tuple[int, Text, Union[None, MetricSummary]]:
        """
        Get metric summary detail filter by summary uuid for Metric Center.

        :param uuid: UUID of registered metric summary.

        :return: A single :py:class:`ai_flow.meta.metric_meta.MetricSummary` object.
        """
        request = UuidRequest(uuid=uuid)
        response = self.metric_stub.getMetricSummary(request)

        if 0 == response.return_code:
            metric_summary_proto = response.metric_summary
            metric_summary = proto_to_metric_summary(metric_summary_proto)
            return response.return_code, response.return_msg, metric_summary
        else:
            return response.return_code, response.return_msg, None

    def list_metric_summaries(self, metric_name: Optional[Text] = None, metric_key: Optional[Text] = None,
                              model_version: Optional[Text] = None, start_time: int = None, end_time=None) -> Tuple[
            int, Text, Union[None, MetricSummary, List[MetricSummary]]]:
        """
        List of metric summaries filter by metric summary fields for Metric Center.

         :param metric_name: (Optional) Name of filtered metric summary.
        :param metric_key: (Optional) Key of filtered metric summary.
        :param model_version: (Optional) Version of the model version associated with the registered metric summary.
        :param start_time: (Optional) Start time for timestamp filtered metric summary.
        :param end_time: (Optional) End time for timestamp filtered metric summary.

        :return: List of :py:class:`ai_flow.meta.metric_meta.MetricSummary` objects.
        """
        request = ListMetricSummariesRequest(metric_name=stringValue(metric_name), metric_key=stringValue(metric_key),
                                             model_version=stringValue(model_version),
                                             start_time=int64Value(start_time), end_time=int64Value(end_time))
        response = self.metric_stub.listMetricSummaries(request)

        if 0 == response.return_code:
            repeated_metric_summary_proto = response.metric_summaries
            if 1 == len(repeated_metric_summary_proto):
                metric_summary = proto_to_metric_summary(repeated_metric_summary_proto[0])
                return response.return_code, response.return_msg, metric_summary
            else:
                res = []
                for metric_summary_proto in repeated_metric_summary_proto:
                    res.append(proto_to_metric_summary(metric_summary_proto))
                return response.return_code, response.return_msg, res

        else:
            return response.return_code, response.return_msg, None
